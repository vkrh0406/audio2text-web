# Transcriber App (FastAPI + faster-whisper)

<b>AI로 작성되었습니다.</b>
간단한 파이썬 웹앱으로, 회의 음성 파일을 업로드하면 백그라운드로 텍스트로 변환하고
완료되면 `.txt`/`.srt`로 다운로드할 수 있습니다.

## 빠른 시작

1) **시스템 요구사항**
   - Python 3.10+
   - `ffmpeg` 설치 (Mac: `brew install ffmpeg`, Ubuntu: `apt-get install ffmpeg` 등)
   - (선택) NVIDIA GPU가 있으면 속도 향상. CPU만으로도 동작함.

2) **설치**
```bash
cd transcriber_app
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

3) **환경 변수 (선택)**
   - `WHISPER_MODEL`: 모델 크기 (`tiny`, `base`, `small`, `medium`, `large-v3` 등). 기본값: `small`
   - `WHISPER_DEVICE`: `cuda` 또는 `cpu` (자동 감지 기본)
   - `DATA_DIR`: 업로드/결과 저장 경로 (기본: `./data`)

4) **실행**
```bash
uvicorn main:app --reload
```
웹 브라우저에서 http://127.0.0.1:8000 접속

## 기능
- 업로드: MP3, WAV, M4A, OGG 등 주요 오디오 형식 허용
- 백그라운드 변환: 업로드 즉시 큐잉되어 진행
- 상태 확인: 진행률/상태를 폴링으로 조회
- 다운로드: `.txt`(타임스탬프 포함/미포함) 및 `.srt` 자막 파일
- 언어 자동 감지

## 한계 / 확장 포인트
- 현재는 인메모리 잡 스토어(서버 재시작 시 휘발). 운영에서는 Redis/Celery 또는 DB 사용 권장.
- 스피커 분리(화자 분할)는 포함하지 않았습니다. `whisperx`나 `pyannote.audio` 연동으로 확장 가능.
- 큰 파일에 대해서는 리버스 프록시(nginx), 청크 업로드, 오브젝트 스토리지(S3/MinIO) 연동 권장.
- 인증/권한(로그인)은 포함하지 않았습니다. 회사 내부망/역할 기반 접근 제어 필요시 미들웨어 추가.

## 라이선스
- 예시 코드이므로 필요에 맞게 수정/사용하세요.
