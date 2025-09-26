# Transcriber App (FastAPI + faster-whisper)

간단한 웹 인터페이스에서 오디오 파일을 업로드하면 백그라운드로 한국어 전사를 수행하고
완료된 결과를 `.txt`, `.srt`, `.json`으로 내려받을 수 있습니다. 드래그앤드롭 드롭존에서
파일명·용량을 즉시 확인할 수 있어 업로드 상태를 쉽게 파악할 수 있습니다.

## 주요 특징

- **한국어 특화 모델 기본 적용**: Hugging Face의 `ghost613/faster-whisper-large-v3-turbo-korean` 모델을 사용해 어색한 문장을 줄였습니다. 첫 실행 시 약 5GB 모델을 내려받습니다.
- **자동 진행률 모니터링**: 업로드와 동시에 작업 카드가 생성되고 진행률·언어·모델 정보를 표시합니다.
- **멀티 포맷 결과물**: 타임스탬프가 포함된 `transcript.txt`, `subtitles.srt`, `segments.json`을 생성합니다.
- **한국어 강제 인식**: `WHISPER_LANGUAGE=ko`를 기본 적용해 언어 감지 오류를 최소화합니다.

## 빠른 시작 (로컬 개발)

1. **사전 요구사항**
   - Python 3.10+
   - `ffmpeg`
   - (선택) NVIDIA GPU — 없는 경우 CPU로 자동 전환됩니다.

2. **설치**
   ```bash
   git clone https://github.com/haragu/audio2text-web.git
   cd audio2text-web
   python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **환경 변수**
   - `WHISPER_MODEL` (기본: `ghost613/faster-whisper-large-v3-turbo-korean`)
   - `WHISPER_LANGUAGE` (기본: `ko`)
   - `WHISPER_DEVICE` (`cuda`/`cpu`, 기본은 자동 감지)
   - `DATA_DIR` (기본: `./data`)

4. **실행**
   ```bash
   uvicorn main:app --reload
   ```
   브라우저에서 http://127.0.0.1:8000 접속 후 오디오 파일을 업로드합니다.

> ℹ️ 처음 실행할 때 Hugging Face 모델이 다운로드됩니다. 네트워크 속도에 따라 수 분이 걸릴 수 있으며, 모델 저장 공간으로 최소 6GB 이상을 확보하세요.

## Docker 사용

1. Docker Desktop 또는 Docker Engine 28+ 설치
2. (선택) 모델을 미리 내려받으려면 `docker compose build` 실행
3. 서비스 실행
   ```bash
   docker compose up -d
   ```
4. 종료
   ```bash
   docker compose down
   ```

도커 환경에서도 `WHISPER_MODEL`, `WHISPER_LANGUAGE`, `DATA_DIR` 등은 `docker-compose.yml`의 `environment` 블록에서 변경할 수 있습니다.

## 모델 변경 팁

- 다국어가 필요하면 `WHISPER_MODEL=openai/whisper-large-v3` 등 기본 Whisper 체크포인트로 바꿀 수 있습니다.
- 리소스가 부족한 경우 `WHISPER_MODEL=base` 또는 `small` 같은 경량 모델을 설정하세요.
- Hugging Face의 private 모델을 사용할 때는 토큰이 필요하므로 컨테이너/환경에 `HF_HOME` 또는 토큰 파일을 미리 구성합니다.

## 한계 및 로드맵

- 화자 분리(diarization)는 지원하지 않습니다. `pyannote.audio` 또는 `whisperx` 연동으로 확장 가능합니다.
- 현재는 인메모리 잡 스토어를 사용합니다. Redis가 연결되면 자동으로 사용하지만 지속성은 직접 관리해야 합니다.
- 대용량 파일 업로드를 위해서는 프론트엔드 청크 업로드나 오브젝트 스토리지 연동을 검토하세요.
- 인증이 없으므로 사내망 등 신뢰 가능한 네트워크에서 사용하거나 Reverse Proxy 레벨에서 접근 제어를 적용해야 합니다.

## 라이선스

프로젝트 용도에 맞게 자유롭게 수정해 사용하세요.
