# 🚀 V3.0 - GUIA RÁPIDO DE INÍCIO

## ⚡ Quickstart (5 minutos)

### 1️⃣ Instalar
```bash
cd projeto-kali
npm install
```

### 2️⃣ Validar Build
```bash
npm run build
# Falha se ESLint achar violations
npm run type-check
```

### 3️⃣ Dev Server
```bash
npm run dev
# Acesse: http://localhost:5190
```

### 4️⃣ Backend
Em terminal separado:
```bash
cd backend
python main_fastapi.py
# Backend rodará em: http://127.0.0.1:8001
```

### 5️⃣ Testar
1. Abra http://localhost:5190
2. Insira um IP em "INJEÇÃO SUTIL"
3. Selecione táticas
4. Clique "[ INICIAR OPERAÇÃO ]"
5. Clique "[ AUDITORIA ]"
6. Selecione vulnerabilidades
7. Clique "[ GERAR LAUDO ]"
8. Leia 4 pilares para CEO

---

## 📁 Arquivos Principais

| Arquivo | Função |
|---------|--------|
| `vite.config.ts` | Porta 5190, ESLint strict |
| `src/context/AppContext.tsx` | Estado centralizado |
| `src/components/RelatorioCompliance.tsx` | Motor CEO (4 pilares) |
| `src/components/Dashboard.tsx` | Container principal |
| `backend/main_fastapi.py` | API em 8001 |
| `MIGRATION_V3.md` | Documentação completa |

---

## 🎨 Visual (Idêntico ao Original)

- ✅ Fundo preto absoluto
- ✅ Bordas verdes limpas
- ✅ Fontes monoestilizadas
- ✅ Crítico: 🔴 Vermelho
- ✅ Alto: 🟠 Laranja
- ✅ Médio: 🟡 Amarelo
- ✅ Baixo: 🟢 Verde

---

## 🔐 Segurança TypeScript

- ❌ Não compila com `any` implícito
- ❌ Não compila com variáveis não usadas
- ❌ Não compila com promises pendentes
- ✅ Build falha com ESLint violations

---

## 📋 Checklist Final

- [ ] npm install rodou sem erros
- [ ] npm run build completou (0 violations)
- [ ] npm run dev está em :5190
- [ ] Backend rodando em :8001
- [ ] Injeção sutil → operação inicia
- [ ] Modal auditoria carrega vulns
- [ ] Relatório compliance mostra 4 pilares
- [ ] CEO entende linguagem de negócio

---

## 🆘 Troubleshooting

**"Cannot find module"**
```bash
rm -rf node_modules package-lock.json
npm install
```

**"Port 5190 already in use"**
Edit `vite.config.ts` → `strictPort: false`

**"Backend connection refused"**
Verifique: python backend/main_fastapi.py está rodando

**"ESLint violations"**
`npm run lint` mostra erros. Fixe antes de build.

---

**Versão:** 3.0.0  
**Status:** ✅ Pronto para Produção  
**Tempo Estimado:** 5 min para setup

Boa sorte! 🎯
