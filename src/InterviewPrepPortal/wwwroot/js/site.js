/* ============================================================
   INTERVIEW PREP PORTAL — site.js
   Handles: accordion, AJAX saves, mobile sidebar, toasts
   ============================================================ */

// ─── TOAST ─────────────────────────────────────────────────────────
function showToast(msg, isError = false) {
    const container = document.getElementById('toast-container') || (() => {
        const d = document.createElement('div');
        d.id = 'toast-container';
        document.body.appendChild(d);
        return d;
    })();

    const toast = document.createElement('div');
    toast.className = 'toast-msg' + (isError ? ' error' : '');
    toast.textContent = msg;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

// ─── CSRF TOKEN HELPER ──────────────────────────────────────────────
function getAntiForgeryToken() {
    const el = document.querySelector('input[name="__RequestVerificationToken"]');
    return el ? el.value : '';
}

// ─── AJAX POST ──────────────────────────────────────────────────────
async function ajaxPost(url, data) {
    const body = new URLSearchParams(data);
    body.append('__RequestVerificationToken', getAntiForgeryToken());

    const resp = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body
    });

    return resp.json();
}

// ─── QUESTION ACCORDION ─────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {

    // Accordion toggle
    document.querySelectorAll('.q-header').forEach(header => {
        header.addEventListener('click', (e) => {
            // Don't toggle when clicking control buttons
            if (e.target.closest('.q-icons') || e.target.closest('.status-controls')) return;

            const card = header.closest('.q-card');
            card.classList.toggle('open');
        });
    });

    // ─── STATUS UPDATE ──────────────────────────────────────────────
    document.querySelectorAll('.status-btn').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.stopPropagation();
            const card = btn.closest('.q-card') || btn.closest('[data-question-id]');
            const questionId = card.dataset.questionId;
            const source = card.dataset.source || 'category';

            const status = btn.dataset.status; // "1"=Learning, "2"=Mastered, "0"=NotStarted
            const confidence = card.querySelector('.confidence-select')?.value || '0';
            const revisionNeeded = card.querySelector('.revision-toggle')?.classList.contains('active-revision') ? 'true' : 'false';
            const isFavorite = card.querySelector('.fav-toggle')?.classList.contains('fav-active') ? 'true' : 'false';

            try {
                const res = await ajaxPost('/Question/UpdateProgress', {
                    questionId, source, status, confidence, revisionNeeded, isFavorite
                });

                if (res.success) {
                    // Update card border
                    card.classList.remove('status-mastered', 'status-learning', 'status-not-started');
                    if (status === '2') card.classList.add('status-mastered');
                    else if (status === '1') card.classList.add('status-learning');

                    // Update button active state
                    card.querySelectorAll('.status-btn').forEach(b => b.classList.remove('active-mastered', 'active-learning'));
                    if (status === '2') btn.classList.add('active-mastered');
                    else if (status === '1') btn.classList.add('active-learning');

                    showToast('Progress saved ✓');
                } else {
                    showToast(res.message || 'Failed to save', true);
                }
            } catch (err) {
                showToast('Network error', true);
            }
        });
    });

    // ─── REVISION TOGGLE ────────────────────────────────────────────
    document.querySelectorAll('.revision-toggle').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.stopPropagation();
            btn.classList.toggle('active-revision');
            await saveProgress(btn);
        });
    });

    // ─── FAVORITE TOGGLE ────────────────────────────────────────────
    document.querySelectorAll('.fav-toggle').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.stopPropagation();
            btn.classList.toggle('fav-active');
            const isFavorite = btn.classList.contains('fav-active');
            btn.title = isFavorite ? 'Remove favorite' : 'Add favorite';

            const card = btn.closest('[data-question-id]');
            try {
                await ajaxPost('/Question/ToggleFavorite', {
                    questionId: card.dataset.questionId,
                    source: card.dataset.source || 'category',
                    isFavorite: String(isFavorite)
                });
                showToast(isFavorite ? '⭐ Added to favorites' : 'Removed from favorites');
            } catch { showToast('Network error', true); }
        });
    });

    // ─── SAVE CUSTOM ANSWER ─────────────────────────────────────────
    document.querySelectorAll('.save-answer-btn').forEach(btn => {
        btn.addEventListener('click', async () => {
            const card = btn.closest('[data-question-id]');
            const textarea = card.querySelector('.answer-textarea');
            const feedback = btn.nextElementSibling;

            try {
                const res = await ajaxPost('/Question/SaveCustomAnswer', {
                    questionId: card.dataset.questionId,
                    source: card.dataset.source || 'category',
                    answerText: textarea.value
                });

                if (res.success) {
                    feedback.classList.add('show');
                    setTimeout(() => feedback.classList.remove('show'), 2500);
                } else {
                    showToast(res.message || 'Failed to save answer', true);
                }
            } catch { showToast('Network error', true); }
        });
    });

    // ─── SAVE NOTE ──────────────────────────────────────────────────
    document.querySelectorAll('.save-note-btn').forEach(btn => {
        btn.addEventListener('click', async () => {
            const card = btn.closest('[data-question-id]');
            const textarea = card.querySelector('.note-textarea');
            const feedback = btn.nextElementSibling;

            try {
                const res = await ajaxPost('/Question/SaveNote', {
                    questionId: card.dataset.questionId,
                    source: card.dataset.source || 'category',
                    noteText: textarea.value
                });

                if (res.success) {
                    feedback.classList.add('show');
                    setTimeout(() => feedback.classList.remove('show'), 2500);
                } else {
                    showToast(res.message || 'Failed to save note', true);
                }
            } catch { showToast('Network error', true); }
        });
    });

    // ─── MOBILE SIDEBAR ─────────────────────────────────────────────
    const hamburger = document.querySelector('.hamburger');
    const sidebar = document.querySelector('.sidebar');

    if (hamburger && sidebar) {
        let backdrop = document.querySelector('.sidebar-backdrop');
        if (!backdrop) {
            backdrop = document.createElement('div');
            backdrop.className = 'sidebar-backdrop';
            document.body.appendChild(backdrop);
        }

        hamburger.addEventListener('click', () => {
            sidebar.classList.add('mobile-open');
            backdrop.style.display = 'block';
        });

        backdrop.addEventListener('click', () => {
            sidebar.classList.remove('mobile-open');
            backdrop.style.display = 'none';
        });
    }
});

// ─── SHARED SAVE PROGRESS HELPER ────────────────────────────────────
async function saveProgress(triggerEl) {
    const card = triggerEl.closest('[data-question-id]');
    if (!card) return;

    const questionId = card.dataset.questionId;
    const source = card.dataset.source || 'category';
    const statusBtn = card.querySelector('.status-btn.active-mastered') || card.querySelector('.status-btn.active-learning');
    const status = statusBtn?.dataset.status || '0';
    const confidence = card.querySelector('.confidence-select')?.value || '0';
    const revisionNeeded = card.querySelector('.revision-toggle')?.classList.contains('active-revision') ? 'true' : 'false';
    const isFavorite = card.querySelector('.fav-toggle')?.classList.contains('fav-active') ? 'true' : 'false';

    try {
        await ajaxPost('/Question/UpdateProgress', { questionId, source, status, confidence, revisionNeeded, isFavorite });
        showToast('Saved ✓');
    } catch { showToast('Network error', true); }
}
