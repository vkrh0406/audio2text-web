# Transcriber App (FastAPI + faster-whisper)

[🇰🇷 Korean](README.md) · [🇺🇸 English](README.en.md)

Upload an audio file through a simple web UI, let the background worker transcribe
it with a Korean-finetuned faster-whisper model, and download the results as
`transcript.txt`, `subtitles.srt`, or `segments.json`. The dropzone instantly shows
the selected filename and size so users can confirm the upload state.

## Highlights

- **Korean-finetuned default model**: Uses Hugging Face model `ghost613/faster-whisper-large-v3-turbo-korean` to reduce awkward Korean sentences. The first run downloads roughly 5 GB of model data.
- **Progress monitoring**: Each upload spawns a job card displaying status, progress, model id, and language.
- **Multiple output formats**: Generates `transcript.txt` (with timestamps), `subtitles.srt`, and `segments.json`.
- **Forced Korean decoding**: `WHISPER_LANGUAGE=ko` is the default to avoid language mis-detection.

## Quickstart (Local)

1. **Prerequisites**
   - Python 3.10+
   - `ffmpeg`
   - Optional: NVIDIA GPU (falls back to CPU automatically)

2. **Install**
   ```bash
   git clone https://github.com/haragu/audio2text-web.git
   cd audio2text-web
   python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Environment variables**
   - `WHISPER_MODEL` (default: `ghost613/faster-whisper-large-v3-turbo-korean`)
   - `WHISPER_LANGUAGE` (default: `ko`)
   - `WHISPER_DEVICE` (`cuda`/`cpu`, auto-detected by default)
   - `DATA_DIR` (default: `./data`)

4. **Run**
   ```bash
   uvicorn main:app --reload
   ```
   Open http://127.0.0.1:8000 and upload an audio file.

> ℹ️ The model download happens on the first run. Allocate at least 6 GB of free disk space and expect a few minutes depending on your connection.

## Docker

1. Install Docker Desktop or Docker Engine 28+
2. (Optional) Pre-fetch the model by running `docker compose build`
3. Start the stack
   ```bash
   docker compose up -d
   ```
4. Shut down
   ```bash
   docker compose down
   ```

Edit the `environment` section in `docker-compose.yml` to point to a different model, language, or data directory if needed.

## Model Tips

- Need multilingual? Set `WHISPER_MODEL=openai/whisper-large-v3` or another official checkpoint.
- On smaller machines choose lighter models such as `base` or `small`.
- Private Hugging Face models require an access token. Provide it via environment variables or mount the token file inside the container.

## Limitations / Roadmap

- No diarization (speaker separation) yet. Consider integrating `pyannote.audio` or `whisperx`.
- Uses an in-memory job store by default. Redis is used automatically when `REDIS_URL` is set, but persistence must be managed separately.
- For very large uploads, consider chunked uploads, reverse proxies, or object storage (S3/MinIO).
- No authentication is bundled. Run behind a trusted network or add auth at the proxy level.

## License

Feel free to adapt this project to your own requirements.
