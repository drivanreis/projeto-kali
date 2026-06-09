#!/usr/bin/env python3
"""
AGENTE FORENSE - KALI-CORE V3.0
Servidor embutido para investigação forense de discos
Roda localmente como API e permite leitura de blocos brutos
"""

import platform
import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

# Inicializa FastAPI
app = FastAPI(title="Agente Forense KALI-CORE", version="1.0.0")

# CORS para permitir requisições do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos Pydantic
class ScanRequest(BaseModel):
    disk_number: int

class RecoverRequest(BaseModel):
    disk_number: int
    offset: int
    size: int

class DiskInfo(BaseModel):
    number: int
    path: str
    size: Optional[int] = None
    type: Optional[str] = None

class RecoveredFile(BaseModel):
    name: str
    size: int
    offset: int
    type: Optional[str] = None

def obter_caminho_hardware(numero_disco: int) -> str:
    """
    Retorna o caminho do disco físico baseado no sistema operacional
    """
    sistema = platform.system()
    if sistema == "Windows":
        # No Windows, acessamos o barramento físico direto pelo kernel
        return f"\\\\.\\PhysicalDrive{numero_disco}"
    elif sistema == "Linux":
        # No Linux, tudo é arquivo dentro do diretório /dev/
        return f"/dev/sd{chr(97 + numero_disco)}"  # ex: 0 -> sda, 1 -> sdb
    else:
        raise ValueError(f"Sistema operacional não suportado: {sistema}")

def listar_discos_disponiveis() -> List[DiskInfo]:
    """
    Lista discos físicos disponíveis no sistema
    """
    sistema = platform.system()
    discos = []
    
    if sistema == "Windows":
        # No Windows, tenta PhysicalDrive0 até PhysicalDrive9
        for i in range(10):
            caminho = f"\\\\.\\PhysicalDrive{i}"
            try:
                with open(caminho, "rb") as f:
                    # Tenta ler o primeiro setor para verificar se existe
                    f.read(512)
                    discos.append(DiskInfo(number=i, path=caminho, type="PhysicalDrive"))
            except (PermissionError, FileNotFoundError, OSError):
                continue
    elif sistema == "Linux":
        # No Linux, lista dispositivos em /dev/sd*
        for i in range(26):
            letra = chr(97 + i)  # a, b, c, ...
            caminho = f"/dev/sd{letra}"
            if os.path.exists(caminho):
                try:
                    size = os.path.getsize(caminho)
                    discos.append(DiskInfo(number=i, path=caminho, size=size, type="BlockDevice"))
                except:
                    discos.append(DiskInfo(number=i, path=caminho, type="BlockDevice"))
    
    return discos

def ler_bloco_bruto(caminho_disco: str, offset: int, tamanho: int) -> bytes:
    """
    Lê blocos brutos do disco físico
    """
    try:
        with open(caminho_disco, "rb") as disco:
            disco.seek(offset)
            return disco.read(tamanho)
    except PermissionError:
        raise HTTPException(
            status_code=403,
            detail="Permissão negada. Execute como Administrador (Windows) ou root (Linux)"
        )
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Disco não encontrado: {caminho_disco}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao ler disco: {str(e)}"
        )

def analisar_assinaturas_arquivos(dados: bytes) -> List[RecoveredFile]:
    """
    Analisa magic bytes para identificar tipos de arquivos
    """
    arquivos = []
    
    # Assinaturas de arquivos comuns (magic bytes)
    magic_bytes = {
        b'\xFF\xD8\xFF': ('jpg', 'image/jpeg'),
        b'\x89PNG': ('png', 'image/png'),
        b'GIF8': ('gif', 'image/gif'),
        b'%PDF': ('pdf', 'application/pdf'),
        b'PK\x03\x04': ('zip', 'application/zip'),
        b'\x50\x4B\x03\x04': ('zip', 'application/zip'),
        b'\x7fELF': ('elf', 'application/x-executable'),
        b'MZ': ('exe', 'application/x-executable'),
        b'RIFF': ('riff', 'audio/x-wav'),
    }
    
    # Varre os dados procurando assinaturas
    for i in range(len(dados) - 4):
        chunk = dados[i:i+4]
        for magic, (ext, mime) in magic_bytes.items():
            if chunk.startswith(magic):
                # Encontrou um arquivo
                nome = f"recuperado_{i}.{ext}"
                arquivos.append(RecoveredFile(
                    name=nome,
                    size=1024,  # Tamanho estimado
                    offset=i,
                    type=mime
                ))
                break
    
    return arquivos

@app.get("/")
async def root():
    """Endpoint raiz"""
    return {
        "servico": "Agente Forense KALI-CORE",
        "versao": "1.0.0",
        "sistema": platform.system(),
        "status": "operacional"
    }

@app.get("/status")
async def get_status():
    """Retorna status do agente"""
    return {
        "status": "online",
        "sistema": platform.system(),
        "arquitetura": platform.machine(),
        "python_version": sys.version
    }

@app.get("/disks")
async def get_disks():
    """Lista discos físicos disponíveis"""
    try:
        discos = listar_discos_disponiveis()
        return {
            "success": True,
            "disks": [d.dict() for d in discos],
            "total": len(discos)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "disks": []
        }

@app.post("/scan")
async def scan_disk(request: ScanRequest):
    """
    Inicia varredura forense do disco
    Analisa magic bytes para identificar arquivos
    """
    try:
        caminho = obter_caminho_hardware(request.disk_number)
        
        # Lê os primeiros 10MB para análise rápida
        dados = ler_bloco_bruto(caminho, 0, 10 * 1024 * 1024)
        
        # Analisa assinaturas de arquivos
        arquivos = analisar_assinaturas_arquivos(dados)
        
        return {
            "success": True,
            "disk_number": request.disk_number,
            "disk_path": caminho,
            "bytes_analyzed": len(dados),
            "files_found": len(arquivos),
            "files": [f.dict() for f in arquivos]
        }
    except HTTPException:
        raise
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/recover")
async def recover_file(request: RecoverRequest):
    """
    Recupera um arquivo específico do disco
    """
    try:
        caminho = obter_caminho_hardware(request.disk_number)
        dados = ler_bloco_bruto(caminho, request.offset, request.size)
        
        # Converte para base64 para transporte via JSON
        import base64
        dados_base64 = base64.b64encode(dados).decode('utf-8')
        
        return {
            "success": True,
            "disk_number": request.disk_number,
            "offset": request.offset,
            "size": len(dados),
            "data": dados_base64
        }
    except HTTPException:
        raise
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def main():
    """Inicia o servidor do agente forense"""
    print("=" * 60)
    print("AGENTE FORENSE - KALI-CORE V3.0")
    print("=" * 60)
    print(f"Sistema: {platform.system()}")
    print(f"Arquitetura: {platform.machine()}")
    print(f"Python: {sys.version}")
    print("=" * 60)
    print("AVISO: Execute como Administrador (Windows) ou root (Linux)")
    print("        para ter permissão de ler discos físicos")
    print("=" * 60)
    print("Servidor iniciando em http://localhost:8888")
    print("=" * 60)
    
    uvicorn.run(app, host="127.0.0.1", port=8888, log_level="info")

if __name__ == "__main__":
    main()
