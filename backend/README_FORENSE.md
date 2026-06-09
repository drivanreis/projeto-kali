# AGENTE FORENSE - KALI-CORE V3.0

## Descrição

O Agente Forense é um servidor embutido de API que permite investigação forense de discos físicos. Ele roda localmente na máquina do usuário e se comunica com a interface web do KALI-CORE através de requisições HTTP para localhost.

## Arquitetura

- **Frontend**: Interface web unificada (5ª guia) em React que mostra gráficos, lista de arquivos recuperados, progresso da varredura e botões de ação
- **Agente Local**: Script Python leve que roda em background como servidor FastAPI
- **Comunicação**: JavaScript faz requisições para localhost:8888 onde o agente Python está rodando

## Requisitos

- Python 3.8 ou superior
- FastAPI
- Uvicorn
- PyInstaller (para compilação)

## Instalação de Dependências

```bash
pip install fastapi uvicorn pyinstaller
```

## Execução em Modo Desenvolvimento

### Windows
```bash
# Execute como Administrador
python forense_agent.py
```

### Linux
```bash
# Execute como root
sudo python forense_agent.py
```

O servidor iniciará em `http://localhost:8888`

## Compilação com PyInstaller

### Windows

Para criar um executável único para Windows:

```bash
# Execute como Administrador
pyinstaller --onefile --name forense_agent --icon=icon.ico forense_agent.py
```

O executável será gerado em `dist/forense_agent.exe`

### Linux

Para criar um executável único para Linux:

```bash
# Execute como root
sudo pyinstaller --onefile --name forense_agent forense_agent.py
```

O executável será gerado em `dist/forense_agent`

### Opções Adicionais do PyInstaller

```bash
# Com janela de console (recomendado para ver logs)
pyinstaller --onefile --console --name forense_agent forense_agent.py

# Sem janela de console (modo silencioso)
pyinstaller --onefile --noconsole --name forense_agent forense_agent.py

# Adicionar ícone
pyinstaller --onefile --icon=icon.ico --name forense_agent forense_agent.py
```

## Uso do Executável Compilado

### Windows
1. Baixe o `forense_agent.exe`
2. Clique com botão direito e selecione "Executar como Administrador"
3. O agente iniciará em background na porta 8888
4. Acesse a 5ª guia "Investigação Forense" no KALI-CORE

### Linux
1. Baixe o executável `forense_agent`
2. Dê permissão de execução: `chmod +x forense_agent`
3. Execute como root: `sudo ./forense_agent`
4. O agente iniciará em background na porta 8888
5. Acesse a 5ª guia "Investigação Forense" no KALI-CORE

## API Endpoints

### GET `/`
Retorna informações do agente

### GET `/status`
Retorna status do agente (online/offline)

### GET `/disks`
Lista discos físicos disponíveis

### POST `/scan`
Inicia varredura forense do disco
- Body: `{"disk_number": 0}`

### POST `/recover`
Recupera arquivo específico do disco
- Body: `{"disk_number": 0, "offset": 0, "size": 1024}`

## Detecção de Sistema Operacional

O agente detecta automaticamente o sistema operacional usando `platform.system()`:

- **Windows**: Acessa barramento físico direto pelo kernel (`\\.\PhysicalDrive{numero_disco}`)
- **Linux**: Acessa dispositivos como arquivos em `/dev/` (`/dev/sda`, `/dev/sdb`, etc.)

## Permissões Necessárias

- **Windows**: Execute como Administrador para ter permissão de ler PhysicalDrive
- **Linux**: Execute como root para ter permissão de ler dispositivos em /dev/

## Segurança

- O agente roda apenas em localhost (127.0.0.1)
- Não expõe portas para rede externa
- Requer privilégios elevados apenas para leitura de discos físicos

## Troubleshooting

### Erro: "Permissão negada"
- Windows: Execute como Administrador
- Linux: Execute com sudo

### Erro: "Disco não encontrado"
- Verifique se o número do disco está correto
- Use o endpoint `/disks` para listar discos disponíveis

### Erro: "Agente não conectado"
- Verifique se o agente está rodando na porta 8888
- Verifique se o firewall não está bloqueando localhost

## Estrutura de Arquivos

```
backend/
├── forense_agent.py          # Script principal do agente
├── README_FORENSE.md         # Este arquivo
├── dist/                     # Executáveis compilados
│   ├── forense_agent.exe     # Windows
│   └── forense_agent         # Linux
└── build/                    # Arquivos temporários de build
```

## Suporte

Para problemas ou dúvidas, consulte a documentação do KALI-CORE ou abra uma issue no repositório.
