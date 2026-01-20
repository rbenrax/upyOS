
// State
const state = {
    currentPath: '/',
    currentFile: null,
    files: [],
    view: 'status'
};


let terminalRenderer = null;

class TerminalRenderer {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.reset();
    }

    reset() {
        if (!this.container) return;
        this.container.textContent = "";
        this.classes = new Set();
        this.cursorX = 0;
        this.activeLineNodes = []; // Nodes that belong to the current line (since last \n)
    }

    commitLine() {
        // Clear cursor marks from current nodes before forgetting them
        this.activeLineNodes.forEach(n => n.classList.remove('term-cursor-active'));
        this.activeLineNodes = [];
        this.cursorX = 0;
    }

    append(text) {
        if (!this.container) return;

        let i = 0;
        while (i < text.length) {
            if (text[i] === '\x1b' && text[i + 1] === '[') {
                let j = i + 2;
                let seq = "";
                while (j < text.length && !/[a-zA-Z]/.test(text[j])) {
                    seq += text[j];
                    j++;
                }

                if (j < text.length) {
                    const command = text[j];
                    this.handleSequence(command, seq);
                    i = j + 1;
                    continue;
                }
            }

            const char = text[i];
            if (char === '\b') {
                this.cursorX = Math.max(0, this.cursorX - 1);
            } else if (char === '\r') {
                this.cursorX = 0;
            } else if (char === '\n') {
                this.addRawText("\n");
                this.commitLine();
            } else {
                this.writeChar(char);
            }
            i++;
        }

        this.renderCursor();
        this.container.scrollTop = this.container.scrollHeight;
    }

    writeChar(char) {
        if (this.cursorX < this.activeLineNodes.length) {
            // Overwrite existing character
            const node = this.activeLineNodes[this.cursorX];
            node.textContent = char;
            this.applyClasses(node);
        } else {
            // Append new character
            this.addRawText(char);
        }
        this.cursorX++;
    }

    getActiveLineText() {
        return this.activeLineNodes.map(n => n.textContent).join('');
    }

    addRawText(text) {
        const span = document.createElement('span');
        this.applyClasses(span);
        span.textContent = text;
        this.container.appendChild(span);
        if (text !== "\n") {
            this.activeLineNodes.push(span);
        }
    }

    applyClasses(node) {
        if (this.classes.size > 0) {
            node.className = Array.from(this.classes).map(c => `ansi-${c}`).join(' ');
        } else {
            node.className = "";
        }
    }

    clearFromCursor() {
        // Remove nodes from current position to end of active line
        const toRemove = this.activeLineNodes.splice(this.cursorX);
        toRemove.forEach(n => n.remove());
    }

    renderCursor() {
        // Clear previous cursor marks
        this.container.querySelectorAll('.term-cursor-active').forEach(el => el.classList.remove('term-cursor-active'));
        const oldTrailing = document.getElementById('term-cursor-el');
        if (oldTrailing) oldTrailing.remove();

        if (this.cursorX < this.activeLineNodes.length) {
            // Highlight the character under the cursor
            this.activeLineNodes[this.cursorX].classList.add('term-cursor-active');
        } else {
            // Show trailing cursor at the end
            const cursor = document.createElement('span');
            cursor.id = 'term-cursor-el';
            cursor.className = 'term-cursor-trailing';
            this.container.appendChild(cursor);
        }
    }

    handleSequence(command, params) {
        if (command === 'm') {
            const codes = params.split(';').map(p => parseInt(p) || 0);
            codes.forEach(code => {
                if (code === 0) this.classes.clear();
                else if (code === 1) this.classes.add('1');
                else if (code >= 30 && code <= 37) {
                    for (let c = 30; c <= 37; c++) this.classes.delete(c.toString());
                    for (let c = 90; c <= 97; c++) this.classes.delete(c.toString());
                    this.classes.add(code.toString());
                } else if (code >= 90 && code <= 97) {
                    for (let c = 30; c <= 37; c++) this.classes.delete(c.toString());
                    for (let c = 90; c <= 97; c++) this.classes.delete(c.toString());
                    this.classes.add(code.toString());
                }
            });
        } else if (command === 'J') {
            if (params === '2' || params === '3' || params === '') this.reset();
        } else if (command === 'H' || command === 'f') {
            this.reset();
        } else if (command === 'K') {
            this.clearFromCursor();
        } else if (command === 'D') { // Left
            const move = parseInt(params) || 1;
            this.cursorX = Math.max(0, this.cursorX - move);
        } else if (command === 'C') { // Right
            const move = parseInt(params) || 1;
            this.cursorX = Math.min(this.activeLineNodes.length, this.cursorX + move);
        }
    }
}

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
        if (viewId === 'terminal') loadTerminal();
        if (viewId === 'status') loadStatus();
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
                    <p><strong>CPU Temp:</strong> ${data.sys.cpu_temp ? data.sys.cpu_temp.toFixed(1) + ' °C' : 'N/A'}</p>
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
                    <h3 style="color: var(--accent); margin-bottom: 10px;">Configuration</h3>
                    <div style="max-height: 300px; overflow-y: auto; padding-right: 5px;">
                        ${(() => {
                if (!data.config || Object.keys(data.config).length === 0)
                    return '<p style="color: var(--text-secondary); font-style: italic;">No configuration data available.</p>';

                const entries = Object.entries(data.config);

                // Buckets for sorting
                const bools = [], texts = [], complex = [], nums = [], others = [];

                entries.forEach(([key, val]) => {
                    const type = typeof val;
                    if (type === 'boolean') bools.push([key, val]);
                    else if (type === 'string') texts.push([key, val]);
                    else if (type === 'number') nums.push([key, val]);
                    else if (Array.isArray(val) || (type === 'object' && val !== null)) complex.push([key, val]);
                    else others.push([key, val]);
                });

                // Sort within buckets by key
                const sortFn = (a, b) => a[0].localeCompare(b[0]);
                bools.sort(sortFn);
                texts.sort(sortFn);
                complex.sort(sortFn);
                nums.sort(sortFn);
                others.sort(sortFn);

                // Combined order: Bool -> Text -> Complex -> Number -> Others
                const sortedEntries = [...bools, ...texts, ...complex, ...nums, ...others];

                return `
                            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px;">
                                ${sortedEntries.map(([key, val]) => {
                    let displayVal = val;
                    try {
                        if (typeof val === 'boolean') {
                            displayVal = val ? '<span style="color:var(--success)">Available</span>' : '<span style="color:var(--text-secondary)">Not Available</span>';
                        } else if (Array.isArray(val)) {
                            if (val.length === 0) displayVal = '<span style="color:var(--text-secondary)">[]</span>';
                            else {
                                displayVal = val.map((item, idx) => {
                                    if (typeof item === 'object' && item !== null) {
                                        return `<div style="margin-left:10px; font-size: 0.85em; color: var(--text-secondary); border-left: 2px solid #45475a; padding-left: 5px; margin-top: 2px;">
                                                            ${Object.entries(item).map(([k, v]) => `${k}=${v}`).join(', ')}
                                                        </div>`;
                                    }
                                    return `<div>${item}</div>`;
                                }).join('');
                            }
                        } else if (typeof val === 'object' && val !== null) {
                            displayVal = `<div style="font-size: 0.85em;">${JSON.stringify(val)}</div>`;
                        }
                    } catch (e) {
                        displayVal = '<span style="color:var(--error)">Error rendering</span>';
                    }

                    return `
                                        <div style="background: rgba(0,0,0,0.2); padding: 8px; border-radius: 4px; overflow: hidden;">
                                            <div style="font-weight: bold; font-size: 0.9em; margin-bottom: 4px; color: var(--text-primary); text-transform: uppercase;">${key}</div>
                                            <div style="font-size: 0.9em; word-break: break-all;">${displayVal}</div>
                                        </div>
                                    `;
                }).join('')}
                            </div>`;
            })()}
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
                        <button class="btn-small btn-off" style="padding: 4px 8px; font-size: 0.8rem; border-radius: 4px; cursor: pointer;">Off</button>
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
// --- Terminal (Full REPL) ---

let termWs = null;
let termLineBuffer = ""; // To detect "clear"
const termStatus = document.getElementById('term-status');
const termContainer = document.getElementById('terminal-container');
const termInputProxy = document.getElementById('term-input-proxy');
const btnTermConnect = document.getElementById('btn-term-connect');

function logTerm(msg, isError = false) {
    if (isError && termContainer) {
        termContainer.textContent += `[ERROR] ${msg}\n`;
        termContainer.scrollTop = termContainer.scrollHeight;
    }
    console.log(`[TERM] ${msg}`);
}

function loadTerminal() {
    if (termInputProxy) termInputProxy.focus();
}

function connectTerminal() {
    if (termWs) {
        termWs.close();
        termWs = null;
        updateTermUI(false);
        return;
    }

    const proto = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const url = `${proto}://${window.location.host}/ws`;

    termStatus.textContent = "Connecting...";
    termStatus.style.color = "var(--text-secondary)";

    try {
        termWs = new WebSocket(url);

        termWs.onopen = () => {
            termStatus.textContent = "Connected";
            termStatus.style.color = "var(--success)";
            updateTermUI(true);
            if (termInputProxy) termInputProxy.focus();
        };

        termWs.onmessage = (e) => {
            if (!terminalRenderer) {
                terminalRenderer = new TerminalRenderer('terminal-container');
            }
            terminalRenderer.append(e.data);
        };

        termWs.onclose = (e) => {
            termStatus.textContent = "Disconnected";
            termStatus.style.color = "var(--error)";
            const cursor = document.getElementById('term-cursor-el');
            if (cursor) cursor.remove();
            termWs = null;
            updateTermUI(false);
        };

        termWs.onerror = (e) => {
            termStatus.textContent = "Error";
            termStatus.style.color = "var(--error)";
            logTerm("WebSocket Error", true);
        };

    } catch (e) {
        logTerm(`Exception: ${e.message}`, true);
    }
}

function updateTermUI(connected) {
    if (btnTermConnect) {
        btnTermConnect.textContent = connected ? "Disconnect" : "Connect";
    }
}

if (btnTermConnect) {
    btnTermConnect.addEventListener('click', connectTerminal);
}

// Handle inputs for REPL (char by char)
if (termInputProxy) {
    termInputProxy.addEventListener('input', (e) => {
        if (!termWs) return;
        if (e.data) {
            termWs.send(e.data);
            termLineBuffer += e.data;
        }
        termInputProxy.value = '';
    });

    termInputProxy.addEventListener('keydown', (e) => {
        if (!termWs) return;
        const key = e.key;

        if (key === 'Enter') {
            e.preventDefault();
            const cmd = termLineBuffer.trim().toLowerCase();
            if (cmd === 'exit') {
                if (terminalRenderer) {
                    terminalRenderer.append("\r\n\x1b[93m[Warning: The 'exit' command is restricted in the Web Terminal to avoid system shutdown.]\x1b[0m\r\n");
                }
                termWs.send('\x03');
                termLineBuffer = "";
                return;
            }
            termWs.send('\r');
            termLineBuffer = "";
        } else if (key === 'Backspace') {
            e.preventDefault();
            termWs.send('\x08');
            termLineBuffer = termLineBuffer.slice(0, -1);
        } else if (key === 'Tab') {
            e.preventDefault();
            termWs.send('\t');
        } else if (key === 'ArrowUp') {
            e.preventDefault();
            termWs.send('\x1b[A');
        } else if (key === 'ArrowDown') {
            e.preventDefault();
            termWs.send('\x1b[B');
        } else if (key === 'ArrowRight') {
            e.preventDefault();
            termWs.send('\x1b[C');
        } else if (key === 'ArrowLeft') {
            e.preventDefault();
            termWs.send('\x1b[D');
        } else if (key === 'Delete') {
            e.preventDefault();
            termWs.send('\x1b[3~');
        } else if (e.ctrlKey) {
            if (key.toLowerCase() === 'c') {
                e.preventDefault();
                apiCall('/api/cmd/interrupt', 'POST').catch(err => console.error("Interrupt failed:", err));
            } else if (key.length === 1 && /[a-z]/i.test(key)) {
                e.preventDefault();
                const code = key.toUpperCase().charCodeAt(0) - 64;
                if (code > 0 && code <= 26) {
                    termWs.send(String.fromCharCode(code));
                }
            }
        }
    });
}

// Paste support
const btnTermPaste = document.getElementById('btn-term-paste');
if (btnTermPaste) {
    btnTermPaste.addEventListener('click', async () => {
        try {
            const text = await navigator.clipboard.readText();
            if (text && termWs) {
                termWs.send(text);
            }
        } catch (err) {
            const text = prompt("Paste command content:");
            if (text && termWs) {
                termWs.send(text);
            }
        }
        if (termInputProxy) termInputProxy.focus();
    });
}

if (termContainer) {
    termContainer.addEventListener('paste', (e) => {
        e.preventDefault();
        const text = (e.clipboardData || window.clipboardData).getData('text');
        if (text && termWs) {
            termWs.send(text);
        }
    });
}

// Support clicking on the black box
if (termContainer) {
    termContainer.addEventListener('click', () => {
        if (termInputProxy) termInputProxy.focus();
    });
}


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
