const API_URL = 'http://localhost:5000/execute';

const ABI_NAMES = [
    'zero','ra','sp','gp','tp',
    't0','t1','t2',
    's0','s1',
    'a0','a1','a2','a3','a4','a5','a6','a7',
    's2','s3','s4','s5','s6','s7','s8','s9','s10','s11',
    't3','t4','t5','t6'
];

let previousRegisters = new Array(32).fill(0);

let allInstructions = [];
let currentStep = 0;

function initRegisterTable() {
    const tbody = document.getElementById('register-body');
    tbody.innerHTML = '';

    for (let i = 0; i < 32; i++) {
        const row = document.createElement('tr');
        row.id = `reg-row-${i}`;

        row.innerHTML = `
            <td>x${i}</td>
            <td>${ABI_NAMES[i]}</td>
            <td id="reg-val-${i}">0x00000000</td>
        `;
        tbody.appendChild(row);
    }
}

document.getElementById('btn-run').addEventListener('click', async () => {
    const code = document.getElementById('code-editor').value;

    if (!code.trim()) return;

    hideError();
    clearLog();

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code: code })
        });

        const data = await response.json();

        if (data.error) {
            showError(data.error);
            return;
        }

        updateRegisters(data.registers);
        renderLog(data.log);
        renderBinary(data.binary);

        allInstructions = data.log;
        currentStep = allInstructions.length;

    } catch (err) {
        showError('Could not connect to backend. Is Flask running on port 5000?');
    }
});

document.getElementById('btn-step').addEventListener('click', async () => {
    const code = document.getElementById('code-editor').value;
    if (!code.trim()) return;

    if (currentStep === 0 || allInstructions.length === 0) {
        hideError();

        try {
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ code: code })
            });

            const data = await response.json();

            if (data.error) {
                showError(data.error);
                return;
            }

            allInstructions = data.log;
            renderBinary(data.binary);
            currentStep = 0;

            previousRegisters = new Array(32).fill(0);
            updateRegisters(new Array(32).fill(0));
            clearLog();

        } catch (err) {
            showError('Could not connect to backend. Is Flask running on port 5000?');
            return;
        }
    }

    if (currentStep < allInstructions.length) {
        const entry = allInstructions[currentStep];
        appendLogEntry(entry);
        currentStep++;
    } else {
        appendLogEntry({ source: '--- end of program ---', rd: '', result: null });
    }
});

document.getElementById('btn-clear').addEventListener('click', () => {
    clearLog();
    previousRegisters = new Array(32).fill(0);
    updateRegisters(new Array(32).fill(0));
    document.getElementById('binary-output').innerHTML = '';
    allInstructions = [];
    currentStep = 0;
    hideError();
});

function updateRegisters(registers) {
    for (let i = 0; i < 32; i++) {
        const cell = document.getElementById(`reg-val-${i}`);
        const row = document.getElementById(`reg-row-${i}`);
        const val = registers[i] ?? 0;

        cell.textContent = '0x' + val.toString(16).padStart(8, '0').toUpperCase();

        if (val !== previousRegisters[i]) {
            row.classList.add('reg-changed');
            setTimeout(() => row.classList.remove('reg-changed'), 1500);
        }
    }
    previousRegisters = [...registers];
}

function renderLog(log) {
    clearLog();
    log.forEach(entry => appendLogEntry(entry));
}

function appendLogEntry(entry) {
    const logOutput = document.getElementById('log-output');
    const div = document.createElement('div');
    div.className = 'log-entry';

    const pc = entry.pc !== undefined
        ? `[0x${entry.pc.toString(16).padStart(4,'0')}]` : '';

    const result = entry.result !== null && entry.result !== undefined
        ? `→ ${entry.rd} = 0x${entry.result.toString(16).padStart(8,'0').toUpperCase()}`
        : '';

    div.innerHTML = `
        <span class="log-pc">${pc}</span>
        <span class="log-instr">${entry.source}</span>
        <span class="log-result">${result}</span>
    `;

    logOutput.appendChild(div);
    logOutput.scrollTop = logOutput.scrollHeight;
}

function renderBinary(binary) {
    const output = document.getElementById('binary-output');
    output.innerHTML = '';

    binary.forEach(instr => {
        const bits = instr.binary.toString(2).padStart(32, '0');
        const formatted = `${bits.slice(0,7)} ${bits.slice(7,12)} ${bits.slice(12,17)} ${bits.slice(17,20)} ${bits.slice(20,25)} ${bits.slice(25)}`;

        const line = document.createElement('div');
        line.textContent = `${instr.source.padEnd(20)} →  ${formatted}`;
        output.appendChild(line);
    });
}

function showError(msg) {
    document.getElementById('error-message').textContent = msg;
    document.getElementById('error-banner').classList.remove('hidden');
}

function hideError() {
    document.getElementById('error-banner').classList.add('hidden');
}

function clearLog() {
    document.getElementById('log-output').innerHTML = '';
}

document.querySelectorAll('.tab[data-tab]').forEach(tab => {
    tab.addEventListener('click', () => {
        tab.closest('nav').querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
    });
});

initRegisterTable();

