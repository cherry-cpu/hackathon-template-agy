// Main JavaScript for AI Content Creator Marketplace

// Format error details safely so [object Object] is never shown
function formatErrorMessage(detail) {
    if (!detail) return 'An error occurred. Please try again.';
    if (typeof detail === 'string') return detail;
    if (Array.isArray(detail)) {
        return detail.map(d => {
            if (typeof d === 'string') return d;
            if (d && typeof d === 'object') {
                if (d.msg) {
                    const field = Array.isArray(d.loc) ? d.loc.filter(x => x !== 'body').join(' ') : '';
                    return field ? `${field}: ${d.msg}` : d.msg;
                }
                return JSON.stringify(d);
            }
            return String(d);
        }).join('; ');
    }
    if (typeof detail === 'object') {
        if (detail.msg) return detail.msg;
        if (detail.message) return detail.message;
        if (detail.detail) return formatErrorMessage(detail.detail);
        return JSON.stringify(detail);
    }
    return String(detail);
}

// Universal Auth Headers Helper for API calls
function getAuthHeaders(extraHeaders = {}) {
    const headers = { ...extraHeaders };
    const token = localStorage.getItem('access_token');
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    return headers;
}

// Global Toast Notifications
function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) return;

    const formattedMessage = formatErrorMessage(message);

    const bgClass = type === 'success' ? 'text-bg-success' : (type === 'danger' ? 'text-bg-danger' : 'text-bg-primary');
    const toastEl = document.createElement('div');
    toastEl.className = `toast align-items-center ${bgClass} border-0 show mb-2 shadow`;
    toastEl.setAttribute('role', 'alert');
    toastEl.setAttribute('aria-live', 'assertive');
    toastEl.setAttribute('aria-atomic', 'true');
    
    toastEl.innerHTML = `
        <div class="d-flex">
            <div class="toast-body fw-medium">${formattedMessage}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;

    toastContainer.appendChild(toastEl);
    setTimeout(() => {
        toastEl.remove();
    }, 5000);
}

// Media Preview Modal Handler
function openMediaModal(title, filePath, contentType, description, format, aspectRatio, tools, skills) {
    const modalTitle = document.getElementById('mediaModalTitle');
    const modalBody = document.getElementById('mediaModalBody');
    const modalMeta = document.getElementById('mediaModalMeta');

    if (!modalTitle || !modalBody) return;

    modalTitle.textContent = title;

    let mediaHtml = '';
    const ext = filePath.split('.').pop().toLowerCase();

    if (['mp4', 'webm', 'mov'].includes(ext)) {
        mediaHtml = `<video controls autoplay class="w-100 rounded" style="max-height: 500px; background: #000;">
            <source src="${filePath}" type="video/${ext === 'mov' ? 'mp4' : ext}">
            Your browser does not support the video tag.
        </video>`;
    } else {
        mediaHtml = `<img src="${filePath}" alt="${title}" class="img-fluid rounded mx-auto d-block" style="max-height: 500px; object-fit: contain;">`;
    }

    modalBody.innerHTML = mediaHtml;

    if (modalMeta) {
        modalMeta.innerHTML = `
            <div class="mt-3 text-start">
                <p class="text-secondary small mb-2">${description || 'No description provided.'}</p>
                <div class="d-flex flex-wrap gap-2">
                    <span class="badge bg-primary">${contentType}</span>
                    ${aspectRatio ? `<span class="badge bg-secondary">${aspectRatio}</span>` : ''}
                    ${format ? `<span class="badge bg-light text-dark border">${format}</span>` : ''}
                </div>
                ${tools ? `<div class="mt-2"><strong class="small text-muted">Tools:</strong> <span class="small">${tools}</span></div>` : ''}
                ${skills ? `<div><strong class="small text-muted">Skills:</strong> <span class="small">${skills}</span></div>` : ''}
            </div>
        `;
    }

    const modal = new bootstrap.Modal(document.getElementById('mediaPreviewModal'));
    modal.show();
}

// Logout handler
async function handleLogout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_role');
    try {
        await fetch('/api/auth/logout', { method: 'POST' });
    } catch (e) {}
    window.location.href = '/';
}
