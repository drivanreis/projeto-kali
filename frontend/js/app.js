// KALI-CORE Frontend Application

// Navegação entre telas
function mostrarTelaArsenal() {
    document.getElementById('tela-home').classList.add('hidden');
    document.getElementById('tela-arsenal').classList.remove('hidden');
}

function mostrarTelaHome() {
    document.getElementById('tela-arsenal').classList.add('hidden');
    document.getElementById('tela-home').classList.remove('hidden');
}

// Iniciar operação com alvo dinâmico
async function iniciarOperacao() {
    const target = document.getElementById('target-input').value;
    if (!target) {
        alert('Por favor, digite um alvo válido');
        return;
    }
    
    try {
        const response = await fetch('http://localhost:8000/api/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ target: target })
        });
        
        const resultado = await response.json();
        
        if (resultado.sucesso) {
            alert(`Operação iniciada para ${target}`);
            // Atualiza alvo no display
            document.getElementById('hw-target').textContent = target;
            // Inicia atualizações
            loadFases();
            loadBandeiras();
            // Abre conexão WebSocket
            conectarWebSocket();
        } else {
            alert('Erro ao iniciar operação: ' + resultado.erro);
        }
    } catch (error) {
        console.error('Erro ao iniciar operação:', error);
        alert('Erro ao iniciar operação');
    }
}

// WebSocket para logs em tempo real
let ws = null;
let logContainer = null;

function conectarWebSocket() {
    if (ws && ws.readyState === WebSocket.OPEN) {
        return; // Já conectado
    }
    
    ws = new WebSocket('ws://localhost:8000/ws/logs');
    logContainer = document.getElementById('log-container');
    
    ws.onmessage = function(event) {
        const logEntry = document.createElement('div');
        logEntry.className = 'log-entry text-green-400';
        logEntry.textContent = event.data;
        logContainer.appendChild(logEntry);
        logContainer.scrollTop = logContainer.scrollHeight;
        
        // Limita a 100 logs
        while (logContainer.children.length > 100) {
            logContainer.removeChild(logContainer.firstChild);
        }
    };
    
    ws.onerror = function(error) {
        console.error('WebSocket error:', error);
    };
    
    ws.onclose = function() {
        console.log('WebSocket closed');
        ws = null;
    };
}

// Carrega status das fases
async function loadFases() {
    try {
        const response = await fetch('http://localhost:8000/api/fases');
        const fases = await response.json();
        
        const container = document.getElementById('fases-container');
        container.innerHTML = '';
        
        Object.keys(fases).forEach(key => {
            const fase = fases[key];
            const div = document.createElement('div');
            div.className = `text-xs p-2 border border-green-500 ${fase.status === 'concluido' ? 'phase-concluido' : 'phase-pending'}`;
            div.innerHTML = `
                <div class="font-bold">${key.toUpperCase()}</div>
                <div class="text-xs mt-1">${fase.nome}</div>
                <div class="text-xs mt-1">STATUS: ${fase.status.toUpperCase()}</div>
            `;
            container.appendChild(div);
        });
    } catch (error) {
        console.error('Erro ao carregar fases:', error);
    }
}

// Carrega bandeiras
async function loadBandeiras() {
    try {
        const response = await fetch('http://localhost:8000/api/bandeiras');
        const bandeiras = await response.json();
        
        const container = document.getElementById('bandeiras-container');
        container.innerHTML = '';
        
        if (bandeiras.bandeiras && bandeiras.bandeiras.length > 0) {
            bandeiras.bandeiras.forEach(bandeira => {
                const div = document.createElement('div');
                div.className = 'text-xs p-2 border border-green-500 bg-green-900';
                div.innerHTML = `
                    <div class="font-bold text-green-400">🏴‍☠️ ${bandeira.tipo.toUpperCase()}</div>
                    <div class="text-xs mt-1">${bandeira.prova}</div>
                    <div class="text-xs mt-1 text-gray-500">${bandeira.timestamp}</div>
                `;
                container.appendChild(div);
            });
        } else {
            container.innerHTML = '<div class="text-xs text-gray-500">Nenhuma bandeira encontrada</div>';
        }
    } catch (error) {
        console.error('Erro ao carregar bandeiras:', error);
    }
}

// Carrega status do sistema
async function loadStatus() {
    try {
        const response = await fetch('http://localhost:8000/api/status');
        const status = await response.json();
        
        document.getElementById('cpu-usage').textContent = status.uso_cpu + '%';
        document.getElementById('mem-usage').textContent = status.uso_memoria + '%';
        document.getElementById('temp-cpu').textContent = status.temperatura_cpu + '°C';
        
        document.getElementById('hw-cpu').textContent = status.uso_cpu + '%';
        document.getElementById('hw-mem').textContent = status.uso_memoria + '%';
        document.getElementById('hw-temp').textContent = status.temperatura_cpu + '°C';
        
        document.getElementById('system-status').textContent = status.running ? '● OPERACIONAL' : '● PARADO';
        document.getElementById('system-status').className = status.running ? 'text-green-400 pulse' : 'text-red-400';
    } catch (error) {
        console.error('Erro ao carregar status:', error);
    }
}

// Injeção sutil
async function injetar(tipo) {
    const caminho = prompt(`Digite o caminho para injeção ${tipo}:`);
    if (!caminho) return;
    
    try {
        const response = await fetch(`http://localhost:8000/api/injecao/${tipo}?caminho=${encodeURIComponent(caminho)}`, {
            method: 'POST'
        });
        const resultado = await response.json();
        alert(resultado.sucesso ? 'Injeção executada com sucesso!' : 'Erro na injeção');
    } catch (error) {
        console.error('Erro na injeção:', error);
        alert('Erro na injeção');
    }
}

// Modal de Auditoria de Segurança
function abrirModalAuditoria() {
    document.getElementById('modal-auditoria').style.display = 'flex';
}

function fecharModalAuditoria() {
    document.getElementById('modal-auditoria').style.display = 'none';
}

// Fechar modal ao clicar fora
document.addEventListener('click', function(event) {
    const modal = document.getElementById('modal-auditoria');
    if (event.target === modal) {
        fecharModalAuditoria();
    }
});

// Atualiza dados periodicamente
setInterval(() => {
    loadFases();
    loadBandeiras();
    loadStatus();
}, 5000);

// Carrega dados iniciais
loadFases();
loadBandeiras();
loadStatus();
