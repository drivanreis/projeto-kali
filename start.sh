#!/bin/bash
# Script de inicialização unificado V1 - KALI-CORE

echo "🟢 Iniciando o Backend FastAPI..."
cd backend && uvicorn main:app --reload &

echo "🔵 Abrindo o Frontend no navegador..."
sleep 2
xdg-open ../frontend/index.html

echo "🚀 Aplicação V1 rodando!"
