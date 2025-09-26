const form = document.getElementById('upload-form');
const fileInput = document.getElementById('file-input');
const dropzone = document.getElementById('dropzone');
const jobsContainer = document.getElementById('jobs');

dropzone.addEventListener('click', () => fileInput.click());

dropzone.addEventListener('dragover', (e) => {
  e.preventDefault();
  dropzone.classList.add('dragover');
});
dropzone.addEventListener('dragleave', () => {
  dropzone.classList.remove('dragover');
});
dropzone.addEventListener('drop', (e) => {
  e.preventDefault();
  dropzone.classList.remove('dragover');
  if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
    fileInput.files = e.dataTransfer.files;
  }
});

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  if (!fileInput.files || fileInput.files.length === 0) return;

  const fd = new FormData();
  fd.append('file', fileInput.files[0]);
  const btn = form.querySelector('button');
  btn.disabled = true;

  try {
    const res = await fetch('/api/upload', { method: 'POST', body: fd });
    const data = await res.json();
    addJobCard(data.job_id);
    pollJob(data.job_id);
  } catch (err) {
    alert('업로드 실패: ' + err.message);
  } finally {
    btn.disabled = false;
    form.reset();
  }
});

function addJobCard(jobId) {
  const card = document.createElement('div');
  card.className = 'job-card';
  card.id = `job-${jobId}`;
  card.innerHTML = `
    <div class="job-header">
      <div><strong>Job:</strong> ${jobId}</div>
      <div class="job-meta" id="meta-${jobId}">대기 중...</div>
    </div>
    <div class="progress"><div id="bar-${jobId}"></div></div>
    <div class="links" id="links-${jobId}" style="margin-top:8px;"></div>
    <div class="error" id="error-${jobId}"></div>
  `;
  jobsContainer.prepend(card);
}

async function pollJob(jobId) {
  const meta = document.getElementById(`meta-${jobId}`);
  const bar = document.getElementById(`bar-${jobId}`);
  const links = document.getElementById(`links-${jobId}`);
  const errBox = document.getElementById(`error-${jobId}`);

  const timer = setInterval(async () => {
    try {
      const res = await fetch(`/api/jobs/${jobId}`);
      const j = await res.json();
      meta.textContent = `${j.status.toUpperCase()} • ${(j.progress * 100).toFixed(0)}% • ${j.model || ''} ${j.language ? '• ' + j.language : ''}`;
      bar.style.width = `${Math.max(0, Math.min(100, j.progress * 100))}%`;

      if (j.status === 'done') {
        links.innerHTML = `
          <a href="/api/jobs/${jobId}/download?format=txt">TXT 다운로드</a>
          <a href="/api/jobs/${jobId}/download?format=srt">SRT 다운로드</a>
          <a href="/api/jobs/${jobId}/download?format=json">JSON 다운로드</a>
        `;
        clearInterval(timer);
      } else if (j.status === 'error') {
        errBox.textContent = j.error || '알 수 없는 오류';
        clearInterval(timer);
      }
    } catch (e) {
      errBox.textContent = e.message;
      clearInterval(timer);
    }
  }, 1500);
}