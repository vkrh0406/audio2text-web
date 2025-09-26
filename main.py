import os
import uuid
import time
import math
from pathlib import Path
from typing import Optional, Dict, Any, List

from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException, Request
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Lazy import for faster-whisper (loaded when first used)
FW_AVAILABLE = True
try:
    import torch  # for device detection (optional)
    from faster_whisper import WhisperModel
except Exception:
    FW_AVAILABLE = False

APP_DIR = Path(__file__).parent.resolve()
DATA_DIR = Path(os.getenv("DATA_DIR", APP_DIR / "data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTS = {".wav", ".mp3", ".m4a", ".ogg", ".webm", ".flac"}

app = FastAPI(title="Transcriber App", version="0.1.0")
app.mount("/static", StaticFiles(directory=str(APP_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(APP_DIR / "templates"))

# Very small in-memory job store for MVP
JOBS: Dict[str, Dict[str, Any]] = {}

def srt_timestamp(seconds: float) -> str:
    if seconds is None or math.isnan(seconds):
        seconds = 0
    ms = int(seconds * 1000)
    hh = ms // 3600000
    ms %= 3600000
    mm = ms // 60000
    ms %= 60000
    ss = ms // 1000
    ms %= 1000
    return f"{hh:02d}:{mm:02d}:{ss:02d},{ms:03d}"

def write_txt(segments: List[Dict[str, Any]], out_path: Path, with_timestamps=True):
    lines = []
    for seg in segments:
        if with_timestamps:
            lines.append(f"[{srt_timestamp(seg['start'])} - {srt_timestamp(seg['end'])}] {seg['text']}")
        else:
            lines.append(seg["text"])
    out_path.write_text("\n".join(lines), encoding="utf-8")

def write_srt(segments: List[Dict[str, Any]], out_path: Path):
    # Simple SRT writer
    parts = []
    for i, seg in enumerate(segments, start=1):
        start = srt_timestamp(seg["start"])
        end = srt_timestamp(seg["end"])
        text = seg["text"].strip()
        parts.append(f"{i}\n{start} --> {end}\n{text}\n")
    out_path.write_text("\n".join(parts), encoding="utf-8")

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/upload")
async def upload(file: UploadFile = File(...), background: BackgroundTasks = None):
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTS:
        raise HTTPException(status_code=400, detail=f"허용되지 않는 확장자: {ext}")

    job_id = uuid.uuid4().hex
    job_dir = DATA_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    audio_path = job_dir / f"input{ext}"
    with audio_path.open("wb") as f:
        while True:
            chunk = await file.read(1024 * 1024)
            if not chunk:
                break
            f.write(chunk)

    JOBS[job_id] = {
        "status": "queued",
        "progress": 0.0,
        "audio_path": str(audio_path),
        "created_at": time.time(),
        "model": None,
        "language": None,
        "error": None,
        "segments": [],
        "outputs": {},
    }

    if background is None:
        background = BackgroundTasks()
    background.add_task(run_transcription_job, job_id)
    return JSONResponse({"job_id": job_id})

@app.get("/api/jobs/{job_id}")
def job_status(job_id: str):
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="존재하지 않는 작업")
    resp = {
        "status": job["status"],
        "progress": job["progress"],
        "model": job.get("model"),
        "language": job.get("language"),
        "error": job.get("error"),
    }
    return JSONResponse(resp)

@app.get("/api/jobs/{job_id}/download")
def job_download(job_id: str, format: str = "txt"):
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="존재하지 않는 작업")
    if job["status"] != "done":
        raise HTTPException(status_code=400, detail="아직 완료되지 않았습니다.")
    outputs = job.get("outputs", {})
    if format not in outputs:
        raise HTTPException(status_code=404, detail=f"{format} 포맷 파일이 없습니다.")
    path = Path(outputs[format])
    if not path.exists():
        raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다.")
    media_type = "text/plain"
    if format == "json":
        media_type = "application/json"
    return FileResponse(path, media_type=media_type, filename=f"{job_id}.{format}")

def load_model():
    if not FW_AVAILABLE:
        raise RuntimeError("faster-whisper 가 설치되지 않았습니다. requirements.txt 를 확인하세요.")
    model_size = os.getenv("WHISPER_MODEL", "small")
    device = os.getenv("WHISPER_DEVICE")
    if device not in ("cpu", "cuda"):
        # auto detect
        try:
            device = "cuda" if torch.cuda.is_available() else "cpu"  # type: ignore
        except Exception:
            device = "cpu"
    compute_type = "float16" if device == "cuda" else "int8"
    model = WhisperModel(model_size, device=device, compute_type=compute_type)
    return model, model_size, device

def run_transcription_job(job_id: str):
    job = JOBS.get(job_id)
    if not job:
        return
    try:
        job["status"] = "processing"
        job["progress"] = 0.05

        model, model_size, device = load_model()
        job["model"] = f"faster-whisper/{model_size} ({device})"

        audio_path = job["audio_path"]
        # Transcribe
        segments_iter, info = model.transcribe(
            audio_path,
            beam_size=5,
            vad_filter=True,
            language=None,  # auto detect
        )
        job["language"] = info.language

        # Collect segments with progress updates
        segments: List[Dict[str, Any]] = []
        last_update = time.time()
        for seg in segments_iter:
            segments.append({
                "id": seg.id,
                "start": float(seg.start or 0.0),
                "end": float(seg.end or 0.0),
                "text": seg.text.strip(),
            })
            # throttle progress update
            if time.time() - last_update > 0.3:
                job["progress"] = min(0.95, job["progress"] + 0.02)
                last_update = time.time()

        # Write outputs
        out_txt = Path(audio_path).with_name("transcript.txt")
        out_srt = Path(audio_path).with_name("subtitles.srt")
        out_json = Path(audio_path).with_name("segments.json")
        write_txt(segments, out_txt, with_timestamps=True)
        write_srt(segments, out_srt)
        out_json.write_text(__import__("json").dumps({"language": info.language, "segments": segments}, ensure_ascii=False, indent=2), encoding="utf-8")

        job["segments"] = segments
        job["outputs"] = {"txt": str(out_txt), "srt": str(out_srt), "json": str(out_json)}
        job["progress"] = 1.0
        job["status"] = "done"
    except Exception as e:
        job["status"] = "error"
        job["error"] = str(e)
        job["progress"] = 1.0