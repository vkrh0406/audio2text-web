# Repository Guidelines

## Project Structure & Module Organization
- `main.py`: FastAPI application that manages endpoints, background jobs, and file writers.
- `templates/index.html`: Jinja-powered upload UI; add new views here and keep context small.
- `static/app.js` and `static/styles.css`: Vanilla JS and CSS for front-end behavior and layout.
- `data/`: Generated at runtime for uploads and transcripts; keep untracked and prune stale jobs.
- New Python modules should live beside `main.py`, while supplementary assets belong in `templates/` or `static/`.

## Build, Test, and Development Commands
- `python -m venv .venv && source .venv/bin/activate`: create and activate an isolated environment.
- `pip install -r requirements.txt`: install FastAPI, uvicorn, faster-whisper, and related tooling.
- `uvicorn main:app --reload`: run the development server with auto-reload on http://127.0.0.1:8000.
- `uvicorn main:app --host 0.0.0.0 --port 8000`: expose the app to other devices on your network.
- `WHISPER_MODEL=small uvicorn main:app --reload`: example of overriding the transcription model per session.

## Coding Style & Naming Conventions
- Target Python 3.10+, four-space indentation, and PEP 8 naming (`snake_case` functions, `SCREAMING_SNAKE_CASE` env vars).
- Use type hints and descriptive variable names; mirror the `run_transcription_job` pattern for new services.
- Keep templates lightweight and prefer `data-js-*` attributes when wiring frontend hooks.
- Name static assets in lower-kebab-case and colocate feature-specific files.

## Testing Guidelines
- No automated suite yet; validate endpoints manually or via `curl -F file=@sample.wav http://127.0.0.1:8000/api/upload`.
- When adding features, introduce `tests/` with `pytest`, use temporary data directories, and guard for missing GPU support.
- Confirm long-running jobs by exercising small audio clips and verifying `.txt`, `.srt`, and `.json` outputs in `data/<job_id>/`.

## Commit & Pull Request Guidelines
- Keep commit subjects short and imperative (e.g., `Add job retention cleanup`, `Update README`).
- Rebase before opening PRs; include purpose, testing evidence, and any new environment variables or defaults.
- Attach UI screenshots or terminal snippets for UX/API changes and link related issues.

## Security & Configuration Tips
- Never commit audio uploads or artifacts under `data/`; `.gitignore` already excludes transient assets.
- Document non-default env vars (`WHISPER_DEVICE`, `DATA_DIR`) in PRs and ensure code creates fallback directories with `Path(...).mkdir(exist_ok=True)`.

## Web Search
- 작업 시 최신 정보가 필요하면 웹검색 기능을 즉시 활성화하고 활용한다.
- 웹검색 결과를 기반으로 한 변경 사항은 출처와 최신 버전을 검증한 뒤 적용한다.
