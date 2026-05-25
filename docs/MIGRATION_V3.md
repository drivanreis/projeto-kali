# KALI-CORE V3.0 - Migração Completa

## 🎯 Objetivos da Migração

- ✅ Migrar de Vanilla JavaScript para React com Hooks
- ✅ Implementar TypeScript com tipagem estrita
- ✅ Usar Vite como bundler (porta 5190)
- ✅ Criar motor de relatório para compliance executivo
- ✅ Centralizar estado com AppContext
- ✅ ESLint com regras estritas

## 📁 Estrutura de Arquivos

```
projeto-kali/
├── vite.config.ts                    # Configuração Vite (porta 5190)
├── tsconfig.json                     # TypeScript strict mode
├── .eslintrc.json                    # ESLint rules
├── package.json                      # Dependencies
├── index.html                        # Entry point
├── src/
│   ├── main.tsx                      # React entry point
│   ├── App.tsx                       # Root component
│   ├── types/
│   │   └── index.ts                  # Interfaces centralizadas
│   ├── context/
│   │   └── AppContext.tsx            # Estado centralizado
│   ├── components/
│   │   ├── Dashboard.tsx             # Container principal
│   │   ├── InjecaoSutil.tsx          # Checkboxes de táticas
│   │   ├── ModalAuditoria.tsx        # Modal de vulnerabilidades
│   │   ├── CardVulnerabilidade.tsx   # Card individual
│   │   └── RelatorioCompliance.tsx   # Motor de relatório CEO
│   └── styles/
│       └── global.css                # CSS global + Tailwind
├── backend/                          # Backend FastAPI (manter)
└── frontend/ (DEPRECATED)            # Remover após validação
```

## 🚀 Instalação e Setup

### 1. Instalar Dependências

```bash
cd projeto-kali
npm install
```

### 2. Iniciar Vite Dev Server

```bash
npm run dev
```

Acesse: **http://localhost:5190**

### 3. Executar Backend

```bash
cd backend
python main_fastapi.py
```

Backend rodará em: **http://127.0.0.1:8001**

## 🔧 Mudanças Principais

### AppContext.tsx
- Estado centralizado: `vulnerabilidades`, `alvos`, `attackTypes`
- Hooks: `setFiltroAlvo`, `setFiltroAtaque`
- Métodos: `iniciarOperacao()`, `atualizarVulnerabilidades()`, `carregarFiltros()`
- Auto-atualização a cada 2 segundos (com cleanup)

### InjecaoSutil.tsx
- Componente com 5 checkboxes de táticas
- Envia array de strings no POST `/api/start`
- Desabilita durante processamento

### ModalAuditoria.tsx
- Header fixo com filtros
- Body scrollável com vulnerabilidades
- Footer fixo com botões de ação
- Seleção de múltiplas vulnerabilidades

### RelatorioCompliance.tsx
- Motor de tradução de vulnerabilidades técnicas → linguagem de negócio
- **4 Pilares:**
  - 💰 Impacto Financeiro / Risco de Negócio
  - ⚠️ Gravidade Executiva
  - 🔧 Plano de Mitigação
  - 💵 Custo Estimado de Correção
- Opções: Imprimir, Baixar HTML, Fechar

## 📋 TypeScript Strict Mode

```json
{
  "strict": true,
  "noUnusedLocals": true,
  "noUnusedParameters": true,
  "noFallthroughCasesInSwitch": true,
  "forceConsistentCasingInFileNames": true
}
```

## ✅ ESLint Rules

- ❌ Não permite `any` implícito
- ❌ Não permite variáveis não utilizadas
- ❌ Não permite promises flutuantes (`noFallthroughCases`)
- ⚠️ Avisa sobre `dead code`
- ⚠️ Avisa sobre `console.log`

Build falha se houver violations.

## 🔌 API Endpoints (Backend esperado na porta 8001)

- `POST /api/start` - Inicia operação de teste
- `GET /api/targets` - Lista alvos
- `GET /api/attack-types` - Lista tipos de ataque
- `GET /api/vulnerabilidades` - Lista vulnerabilidades (com filtros)

## 🎨 Visual Identity

- Fundo: Preto absoluto (#000)
- Texto: Verde claro (#00ff00)
- Bordas: Verde (#00AA00)
- Font: Courier New (monospaced)
- Crítico: Vermelho (#ff0000)
- Alto: Laranja (#ff8800)
- Médio: Amarelo (#ffff00)
- Baixo: Verde (#00ff00)

## 🔄 Fluxo de Uso

1. **Injeção Sutil:** Insira IP/domínio + selecione táticas
2. **Iniciar Operação:** POST para /api/start
3. **Modal Auditoria:** Visualize vulnerabilidades encontradas
4. **Filtros:** Refine por IP/Domínio e Tipo de Ataque
5. **Seleção:** Marque vulnerabilidades de interesse
6. **Gerar Laudo:** Cria relatório executivo em nova aba
7. **Compliance:** CEO lê impacto financeiro, risco e custos

## 🧪 Validação de Build

```bash
npm run type-check    # Verifica TypeScript
npm run lint          # Verifica ESLint
npm run build         # Build production
```

## ⚠️ Diferenças da Versão Anterior

| Aspecto | V2 (Vanilla) | V3 (React) |
|---------|--------------|-----------|
| Framework | HTML + JS | React + TypeScript |
| Bundler | N/A | Vite |
| Porta | file:// | 5190 |
| Estado | Global (var) | AppContext |
| Tipagem | Nenhuma | Strict TypeScript |
| Componentes | Monolítico | Modular |
| Relatório | Texto simples | Compliance executivo |
| Linter | N/A | ESLint strict |

## 📝 Notas Importantes

- Backend mantém porta **8001** (configurado em AppContext.tsx)
- Frontend roda em **5190** (configurado em vite.config.ts)
- Todos os dados vêm do banco de dados (sem mocks)
- Memory leaks prevenidos com cleanup de intervals
- Type-safe em 100%

## 🐛 Troubleshooting

**Erro: "Cannot find module 'react'"**
```bash
npm install
```

**Erro: Port 5190 em uso**
```bash
vite.config.ts → strictPort: false (use porta diferente)
```

**Erro: CORS**
Backend deve ter CORSMiddleware ativo

**Vulnerabilidades não carregam**
Verifique se backend está rodando em http://127.0.0.1:8001

---

**Versão:** 3.0.0  
**Data:** 25 de Maio de 2026  
**Status:** Pronto para Produção
