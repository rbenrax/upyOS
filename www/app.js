
// State
const state = {
    currentPath: '/',
    currentFile: null,
    files: [],
    view: 'status'
};

// API Helpers
async function apiCall(endpoint, method = 'POST', body = {}) {
    try {
        const options = {
            method,
            headers: { 'Content-Type': 'application/json' }
        };

        if (method !== 'GET' && method !== 'HEAD') {
            options.body = JSON.stringify(body);
        }

        const response = await fetch(endpoint, options);

        if (response.status === 401) {
            window.location.href = 'login.html';
            throw new Error("Unauthorized");
        }

        const data = await response.json();
        if (data.error) throw new Error(data.error);
        return data;
    } catch (err) {
        alert('Error: ' + err.message);
        throw err;
    }
}

// Navigation
document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.view-section').forEach(v => v.classList.remove('active'));

        btn.classList.add('active');
        const viewId = btn.dataset.view;
        document.getElementById(`view-${viewId}`).classList.add('active');
        state.view = viewId;

        // Auto close sidebar on mobile
        if (window.innerWidth <= 768) {
            document.getElementById('sidebar').classList.remove('open');
            document.getElementById('sidebar-overlay').classList.remove('active');
        }

        if (viewId === 'files') loadFiles();
        if (viewId === 'gpio') loadGPIO();
        if (viewId === 'status') loadStatus();
        if (viewId === 'run') document.getElementById('cmd-input').focus();
    });
});

// Mobile Sidebar Toggle
document.getElementById('menu-toggle').addEventListener('click', () => {
    document.getElementById('sidebar').classList.toggle('open');
    document.getElementById('sidebar-overlay').classList.toggle('active');
});

document.getElementById('sidebar-overlay').addEventListener('click', () => {
    document.getElementById('sidebar').classList.remove('open');
    document.getElementById('sidebar-overlay').classList.remove('active');
});

// --- Run Command ---

document.getElementById('btn-run-cmd').addEventListener('click', async () => {
    const input = document.getElementById('cmd-input');
    const output = document.getElementById('cmd-output');
    const cmd = input.value.trim();

    if (!cmd) return;

    try {
        const data = await apiCall('/api/cmd/run', 'POST', { cmd });
        // Strip ANSI escape codes
        const cleanOutput = data.output.replace(/[\u001b\u009b][[()#;?]*(?:[0-9]{1,4}(?:;[0-9]{0,4})*)?[0-z]/g, '');
        output.textContent += `${data.cwd || '/'} $: ${cmd}\n${cleanOutput}\n\n`;
        input.value = '';
    } catch (e) {
        output.textContent += `Error: ${e.message}\n\n`;
    }

    // Auto scroll to bottom
    output.scrollTop = output.scrollHeight;
});

// Allow Enter key to run
document.getElementById('cmd-input').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        document.getElementById('btn-run-cmd').click();
    }
});

document.getElementById('btn-stop-cmd').addEventListener('click', async () => {
    try {
        await apiCall('/api/cmd/interrupt', 'POST');
        document.getElementById('cmd-output').textContent += `\n[Interrupt signal sent]\n`;
    } catch (e) {
        console.error('Stop command failed:', e);
    }
});

document.getElementById('btn-clear-output').addEventListener('click', () => {
    document.getElementById('cmd-output').textContent = '';
});



// --- Status ---

async function loadStatus() {
    try {
        const data = await apiCall('/api/status', 'GET');
        const container = document.getElementById('status-container');

        container.innerHTML = `
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                <div class="card" style="background: var(--sidebar-bg); padding: 20px; border-radius: 8px;">
                    <h3 style="color: var(--accent); margin-bottom: 10px;">Board</h3>
                    <p><strong>System ID:</strong> ${data.sys.id || 'N/A'}</p>
                    <p><strong>Board:</strong> ${data.board.name || 'N/A'}</p>
                    <p><strong>Vendor:</strong> ${data.board.vendor || 'N/A'}</p>
                    <p><strong>MCU:</strong> ${data.mcu.type || 'N/A'} (${data.mcu.arch || 'N/A'})</p>
                    <p><strong>CPU Speed:</strong> ${data.sys.cpu_freq ? (data.sys.cpu_freq / 1000000).toFixed(0) + ' MHz' : 'N/A'}</p>
                    <p><strong>OS:</strong> ${data.sys.name || 'upyOS'} ${data.sys.version || ''}</p>
                </div>
                
                <div class="card" style="background: var(--sidebar-bg); padding: 20px; border-radius: 8px;">
                    <h3 style="color: var(--accent); margin-bottom: 10px;">Resources</h3>
                    <p><strong>Memory:</strong> ${formatBytes(data.memory.free)} free / ${formatBytes(data.memory.total)} total</p>
                    <div style="background: #313244; height: 10px; border-radius: 5px; margin-top: 5px;">
                        <div style="background: var(--success); width: ${(data.memory.free / data.memory.total * 100) || 0}%; height: 100%; border-radius: 5px;"></div>
                    </div>
                    <br>
                    <p><strong>Storage:</strong> ${formatBytes(data.storage.free)} free / ${formatBytes(data.storage.total)} total</p>
                    <div style="background: #313244; height: 10px; border-radius: 5px; margin-top: 5px;">
                        <div style="background: var(--success); width: ${(data.storage.free / data.storage.total * 100) || 0}%; height: 100%; border-radius: 5px;"></div>
                    </div>
                </div>

                <div class="card" style="background: var(--sidebar-bg); padding: 20px; border-radius: 8px; grid-column: span 2;">
                    <h3 style="color: var(--accent); margin-bottom: 10px;">Services</h3>
                    <div style="display: flex; gap: 30px; flex-wrap: wrap;">
                        ${Object.entries(data.services || {}).map(([name, running]) => `
                            <div style="display: flex; align-items: center; gap: 8px;">
                                <div style="width: 10px; height: 10px; border-radius: 50%; background: ${running ? 'var(--success)' : '#45475a'}"></div>
                                <span>${name}</span>
                                <span style="font-size: 0.8rem; color: var(--text-secondary)">(${running ? 'Running' : 'Stopped'})</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;
    } catch (e) {
        console.error(e);
    }
}

document.getElementById('btn-refresh-status').addEventListener('click', loadStatus);

document.getElementById('btn-reset-mcu').addEventListener('click', async () => {
    if (confirm("Are you sure you want to reset the MCU?")) {
        try {
            await apiCall('/api/system/reset', 'POST');
            alert("Reset signal sent. The connection will be lost as the device reboots.");
            setTimeout(() => {
                window.location.reload();
            }, 2000);
        } catch (e) {
            console.error('Reset failed:', e);
        }
    }
});

// --- File Manager ---

async function loadFiles(path = state.currentPath) {
    try {
        const data = await apiCall('/api/fs/list', 'POST', { path });
        state.currentPath = data.path;
        state.files = data.entries;
        renderFiles();
        document.getElementById('current-path').textContent = state.currentPath;
    } catch (e) {
        console.error(e);
    }
}

function renderFiles() {
    const list = document.getElementById('file-list');
    list.innerHTML = '';

    // Sort directories first
    state.files.sort((a, b) => {
        if (a.is_dir === b.is_dir) return a.name.localeCompare(b.name);
        return a.is_dir ? -1 : 1;
    });

    state.files.forEach(file => {
        const el = document.createElement('div');
        el.className = 'file-item';
        el.innerHTML = `
            <div class="file-icon">${file.is_dir ? '📁' : '📄'}</div>
            <div class="file-name">${file.name}</div>
            <div class="file-size">${file.is_dir ? '-' : formatBytes(file.size)}</div>
            <div class="file-actions">
                ${!file.is_dir ? '<button class="btn-icon btn-download" title="Download">📥</button>' : ''}
                <button class="btn-icon btn-rename">✏️</button>
                <button class="btn-icon btn-delete">🗑️</button>
            </div>
        `;

        // Click to navigate or edit
        el.querySelector('.file-name').addEventListener('click', () => {
            const fullPath = (state.currentPath === '/' ? '' : state.currentPath) + '/' + file.name;
            if (file.is_dir) {
                loadFiles(fullPath);
            } else {
                openEditor(fullPath);
            }
        });

        // Actions
        if (!file.is_dir) {
            el.querySelector('.btn-download').addEventListener('click', (e) => {
                e.stopPropagation();
                const fullPath = (state.currentPath === '/' ? '' : state.currentPath) + '/' + file.name;
                downloadFile(fullPath);
            });
        }

        el.querySelector('.btn-rename').addEventListener('click', (e) => {
            e.stopPropagation();
            renameFile(file.name);
        });

        el.querySelector('.btn-delete').addEventListener('click', (e) => {
            e.stopPropagation();
            deleteFile(file.name);
        });

        list.appendChild(el);
    });
}

function formatBytes(bytes, decimals = 2) {
    if (!+bytes) return '0 B';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`;
}

async function renameFile(name) {
    const newName = prompt("New name:", name);
    if (newName && newName !== name) {
        const fullOld = (state.currentPath === '/' ? '' : state.currentPath) + '/' + name;
        const fullNew = (state.currentPath === '/' ? '' : state.currentPath) + '/' + newName;
        await apiCall('/api/fs/rename', 'POST', { old_path: fullOld, new_path: fullNew });
        loadFiles();
    }
}

async function deleteFile(name) {
    if (confirm(`Delete ${name}?`)) {
        const fullPath = (state.currentPath === '/' ? '' : state.currentPath) + '/' + name;
        await apiCall('/api/fs/delete', 'POST', { path: fullPath });
        loadFiles();
    }
}

document.getElementById('btn-refresh').addEventListener('click', () => loadFiles());

document.getElementById('btn-up').addEventListener('click', () => {
    let p = state.currentPath.split('/');
    p.pop();
    let newPath = p.join('/');
    if (newPath === '') newPath = '/';
    loadFiles(newPath);
});

document.getElementById('btn-mkdir').addEventListener('click', async () => {
    const name = prompt("Folder name:");
    if (name) {
        const fullPath = (state.currentPath === '/' ? '' : state.currentPath) + '/' + name;
        await apiCall('/api/fs/mkdir', 'POST', { path: fullPath });
        loadFiles();
    }
});

document.getElementById('btn-newfile').addEventListener('click', async () => {
    const name = prompt("File name:");
    if (name) {
        const fullPath = (state.currentPath === '/' ? '' : state.currentPath) + '/' + name;
        // Create empty file using raw fetch to match backend expectation
        try {
            const response = await fetch(`/api/fs/write?path=${encodeURIComponent(fullPath)}`, {
                method: 'POST',
                body: ''
            });

            if (response.ok) {
                loadFiles();
            } else {
                const data = await response.json().catch(() => ({}));
                alert('Error creating file: ' + (data.error || response.statusText));
            }
        } catch (err) {
            alert('Error creating file: ' + err.message);
        }
    }
});

async function downloadFile(path) {
    // We use a direct link to the download API
    window.location.href = `/api/fs/download?path=${encodeURIComponent(path)}`;
}

document.getElementById('btn-upload').addEventListener('click', () => {
    document.getElementById('file-input').click();
});

document.getElementById('file-input').addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const fullPath = (state.currentPath === '/' ? '' : state.currentPath) + '/' + file.name;

    // We check if file exists
    if (state.files.find(f => f.name === file.name)) {
        if (!confirm(`File ${file.name} already exists. Overwrite?`)) {
            e.target.value = '';
            return;
        }
    }

    try {
        const response = await fetch(`/api/fs/upload?path=${encodeURIComponent(fullPath)}`, {
            method: 'POST',
            body: file // Browser handles streaming for large files automatically when body is a File/Blob
        });

        if (response.ok) {
            alert('Upload successful!');
            loadFiles();
        } else {
            const data = await response.json();
            alert('Upload failed: ' + (data.error || response.statusText));
        }
    } catch (err) {
        alert('Upload error: ' + err.message);
    }
    e.target.value = ''; // Reset input
});

// --- Editor ---

async function openEditor(path) {
    state.currentFile = path;
    const response = await fetch(`/api/fs/read?path=${encodeURIComponent(path)}`);
    const content = await response.text();

    document.getElementById('editor-filename').textContent = path;
    const editor = document.getElementById('code-editor');
    editor.value = content;
    updateEditorHighlight();
    document.getElementById('editor-overlay').classList.remove('hidden');
    editor.focus();
}

document.getElementById('btn-close-editor').addEventListener('click', () => {
    document.getElementById('editor-overlay').classList.add('hidden');
    state.currentFile = null;
});

document.getElementById('btn-save').addEventListener('click', async () => {
    if (state.currentFile) {
        const content = document.getElementById('code-editor').value;
        const response = await fetch(`/api/fs/write?path=${encodeURIComponent(state.currentFile)}`, {
            method: 'POST',
            body: content
        });
        if (response.ok) {
            alert('Saved!');
        } else {
            const data = await response.json().catch(() => ({}));
            alert('Save failed: ' + (data.error || response.statusText));
        }
    }
});


// --- GPIO ---

async function loadGPIO() {
    try {
        const data = await apiCall('/api/gpio/status', 'GET');
        const list = document.getElementById('gpio-list');
        list.innerHTML = '';

        const createSection = (title) => {
            const h = document.createElement('h3');
            h.textContent = title;
            h.style.gridColumn = '1 / -1';
            h.style.margin = '20px 0 10px 0';
            h.style.color = 'var(--accent)';
            h.style.borderBottom = '1px solid #313244';
            h.style.paddingBottom = '5px';
            list.appendChild(h);
        };

        // Standard GPIOs
        if (data.pins && data.pins.length > 0) {
            createSection('Standard GPIOs');
            data.pins.forEach(pin => {
                const card = document.createElement('div');
                card.className = 'gpio-card';
                card.innerHTML = `
                    <div class="gpio-id" style="font-size: 0.9rem;">
                        GPIO ${pin.gpio} <br>
                        <small style="color: var(--text-secondary);">(Pin ${pin.pin})</small>
                    </div>
                    <label class="gpio-switch">
                        <input type="checkbox" ${pin.val ? 'checked' : ''} data-pin="${pin.gpio}">
                        <span class="slider"></span>
                    </label>
                `;

                card.querySelector('input').addEventListener('change', async (e) => {
                    const val = e.target.checked ? 1 : 0;
                    await apiCall('/api/gpio/set', 'POST', { pin: pin.gpio, val });
                });

                list.appendChild(card);
            });
        }

        // Board LEDs
        if (data.leds && data.leds.length > 0) {
            createSection('Board LEDs');
            data.leds.forEach(led => {
                const card = document.createElement('div');
                card.className = 'gpio-card led-card';
                card.innerHTML = `
                    <div class="gpio-id" style="font-size: 0.9rem;">
                        LED ${led.label} <br>
                        <small style="color: var(--text-secondary);">(GPIO ${led.gpio})</small>
                    </div>
                    <label class="gpio-switch">
                        <input type="checkbox" ${led.val ? 'checked' : ''} data-pin="${led.gpio}">
                        <span class="slider"></span>
                    </label>
                `;

                card.querySelector('input').addEventListener('change', async (e) => {
                    const val = e.target.checked ? 1 : 0;
                    await apiCall('/api/gpio/set', 'POST', { pin: led.gpio, val });
                });

                list.appendChild(card);
            });
        }

        // RGB LED
        if (data.rgb && data.rgb.length > 0) {
            createSection('RGB Control (WS2812B)');
            data.rgb.forEach(rgb => {
                const card = document.createElement('div');
                card.className = 'gpio-card rgb-card';
                card.style.display = 'block';
                card.innerHTML = `
                    <div class="gpio-id" style="margin-bottom: 10px; font-size: 0.9rem;">
                        ${rgb.label} <small style="color: var(--text-secondary);">(GPIO ${rgb.gpio})</small>
                    </div>
                    <div style="display: flex; gap: 10px; align-items: center;">
                        <input type="color" value="#000000" style="width: 40px; height: 30px; border: none; background: none; cursor: pointer;">
                        <button class="btn-small" style="padding: 4px 8px; font-size: 0.8rem; background: var(--accent); color: white; border: none; border-radius: 4px; cursor: pointer;">Set</button>
                        <button class="btn-small btn-off" style="padding: 4px 8px; font-size: 0.8rem; background: #f38ba8; color: white; border: none; border-radius: 4px; cursor: pointer;">Off</button>
                    </div>
                `;

                const setRgb = async (color) => {
                    const r = parseInt(color.substr(1, 2), 16);
                    const g = parseInt(color.substr(3, 2), 16);
                    const b = parseInt(color.substr(5, 2), 16);
                    await apiCall('/api/rgb/set', 'POST', { gpio: rgb.gpio, r, g, b });
                };

                const buttons = card.querySelectorAll('button');
                buttons[0].addEventListener('click', () => setRgb(card.querySelector('input').value));
                buttons[1].addEventListener('click', () => {
                    card.querySelector('input').value = '#000000';
                    setRgb('#000000');
                });

                list.appendChild(card);
            });
        }
    } catch (e) {
        console.error('GPIO Load Error:', e);
    }
}

document.getElementById('btn-refresh-gpio').addEventListener('click', loadGPIO);

// --- Syntax Highlighting ---

function highlightPython(text) {
    // Escape HTML
    text = text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

    // Order: Strings, Comments, Keywords, Numbers
    const regex = /(".*?"|'.*?'|#.*|\b(?:def|class|if|else|elif|for|while|try|except|finally|import|from|as|return|yield|break|continue|pass|lambda|global|nonlocal|assert|with|del|in|is|and|or|not|True|False|None)\b|\d+)/g;

    return text.replace(regex, (match) => {
        if (match.startsWith('"') || match.startsWith("'")) return `<span class="hl-str">${match}</span>`;
        if (match.startsWith('#')) return `<span class="hl-cmt">${match}</span>`;
        if (/\d+/.test(match)) return `<span class="hl-num">${match}</span>`;
        return `<span class="hl-kw">${match}</span>`;
    });
}

function updateEditorHighlight() {
    const editor = document.getElementById('code-editor');
    const highlightLayer = document.getElementById('highlight-layer');
    if (!editor || !highlightLayer) return;

    const ext = state.currentFile ? state.currentFile.split('.').pop().toLowerCase() : '';
    if (ext === 'py') {
        highlightLayer.innerHTML = highlightPython(editor.value) + (editor.value.endsWith('\n') ? ' ' : '');
    } else {
        highlightLayer.textContent = editor.value + (editor.value.endsWith('\n') ? ' ' : '');
    }
}

// Editor synchronization
const editorEl = document.getElementById('code-editor');
const highlightEl = document.getElementById('highlight-layer');
if (editorEl && highlightEl) {
    editorEl.addEventListener('input', updateEditorHighlight);

    // Use requestAnimationFrame for smoother scroll sync on mobile
    let isSyncing = false;
    editorEl.addEventListener('scroll', () => {
        if (!isSyncing) {
            window.requestAnimationFrame(() => {
                highlightEl.scrollTop = editorEl.scrollTop;
                highlightEl.scrollLeft = editorEl.scrollLeft;
                isSyncing = false;
            });
            isSyncing = true;
        }
    });
}

// Init
loadStatus();
document.getElementById('cmd-output').textContent = '';

// Logout
document.getElementById('btn-logout').addEventListener('click', async () => {
    if (confirm('Are you sure you want to logout?')) {
        try {
            await apiCall('/api/logout', 'GET');
            window.location.href = 'login.html';
        } catch (e) {
            console.error('Logout failed:', e);
            // Fallback: just redirect
            window.location.href = 'login.html';
        }
    }
});
