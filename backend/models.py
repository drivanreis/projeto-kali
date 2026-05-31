#!/usr/bin/env python3
"""
Modelos de Banco de Dados - KALI-CORE V3.0
Arquitetura completa para inventário e análise de ativos.

NOVO SCHEMA (7 tabelas):
1. ATIVOS - Inventário de equipamentos/dispositivos
2. IDENTIFICADORES - Múltiplos IDs por ativo (IP, MAC, IMEI, etc)
3. INTERFACES_DE_REDE - Meios de comunicação
4. COLETAS - Histórico de coletas de informações
5. DADOS_BRUTOS - Dados flexíveis em JSONB
6. EVENTOS - Histórico de mudanças
7. TAGS - Classificação e agrupamento

LEGADO (4 tabelas - compatibilidade):
- Alvo, ConfigAtaque, HistoricoOperacoes, VulnerabilidadesOcorrencias
- AttackHistory
"""

import os
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    UUID,
    JSON,
    Table,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import uuid
import json

Base = declarative_base()

# ═════════════════════════════════════════════════════════════════════════════
# TABELA ASSOCIATIVA: ATIVO <-> TAG (Many-to-Many)
# ═════════════════════════════════════════════════════════════════════════════
ativo_tag_association = Table(
    "ativo_tag_association",
    Base.metadata,
    Column("ativo_id", UUID(as_uuid=True), ForeignKey("ativos.id")),
    Column("tag_id", UUID(as_uuid=True), ForeignKey("tags.id")),
)


# ═════════════════════════════════════════════════════════════════════════════
# NOVO SCHEMA: INVENTÁRIO DE ATIVOS (7 TABELAS)
# ═════════════════════════════════════════════════════════════════════════════


class Ativo(Base):
    """1. TABELA: ATIVOS - Inventário de equipamentos"""
    __tablename__ = "ativos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tipo = Column(String(50), nullable=False)  # PC, Notebook, Celular, Impressora, IoT, Servidor, etc
    nome = Column(String(255), nullable=False)
    descricao = Column(Text)
    status = Column(String(50), default="ativo")  # ativo, inativo, descomissionado
    
    criado_em = Column(DateTime, default=datetime.utcnow, nullable=False)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    identificadores = relationship("Identificador", back_populates="ativo", cascade="all, delete-orphan")
    interfaces = relationship("InterfaceDeRede", back_populates="ativo", cascade="all, delete-orphan")
    coletas = relationship("Coleta", back_populates="ativo", cascade="all, delete-orphan")
    eventos = relationship("Evento", back_populates="ativo", cascade="all, delete-orphan")
    tags = relationship("Tag", secondary=ativo_tag_association, back_populates="ativos")


class Identificador(Base):
    """2. TABELA: IDENTIFICADORES - Múltiplos IDs por ativo"""
    __tablename__ = "identificadores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ativo_id = Column(UUID(as_uuid=True), ForeignKey("ativos.id"), nullable=False)
    
    tipo = Column(String(50), nullable=False)  # IP, MAC, IMEI, Hostname, Serial, SSID, UUID
    valor = Column(Text, nullable=False)
    
    criado_em = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relacionamento
    ativo = relationship("Ativo", back_populates="identificadores")


class InterfaceDeRede(Base):
    """3. TABELA: INTERFACES_DE_REDE - Meios de comunicação"""
    __tablename__ = "interfaces_de_rede"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ativo_id = Column(UUID(as_uuid=True), ForeignKey("ativos.id"), nullable=False)
    
    tipo = Column(String(50), nullable=False)  # Ethernet, Wi-Fi, Bluetooth, LTE, 5G, Satélite, IR, Rádio
    mac = Column(String(17))  # XX:XX:XX:XX:XX:XX
    ip = Column(String(45))  # IPv4 ou IPv6
    ativo = Column(Boolean, default=True)
    
    criado_em = Column(DateTime, default=datetime.utcnow, nullable=False)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamento
    ativo = relationship("Ativo", back_populates="interfaces")


class Coleta(Base):
    """4. TABELA: COLETAS - Histórico de coletas de informações"""
    __tablename__ = "coletas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ativo_id = Column(UUID(as_uuid=True), ForeignKey("ativos.id"), nullable=False)
    
    coletado_em = Column(DateTime, nullable=False)
    origem = Column(String(100), nullable=False)  # Agente Windows, Frontend, Importação TXT/JSON, API
    versao_agente = Column(String(50))
    
    criado_em = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relacionamentos
    ativo = relationship("Ativo", back_populates="coletas")
    dados_brutos = relationship("DadosBrutos", back_populates="coleta", cascade="all, delete-orphan")


class DadosBrutos(Base):
    """5. TABELA: DADOS_BRUTOS - Dados flexíveis em JSONB"""
    __tablename__ = "dados_brutos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    coleta_id = Column(UUID(as_uuid=True), ForeignKey("coletas.id"), nullable=False)
    
    json_dados = Column(JSONB, nullable=False)  # JSONB do PostgreSQL
    
    criado_em = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relacionamento
    coleta = relationship("Coleta", back_populates="dados_brutos")


class Evento(Base):
    """6. TABELA: EVENTOS - Histórico e auditoria de mudanças"""
    __tablename__ = "eventos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ativo_id = Column(UUID(as_uuid=True), ForeignKey("ativos.id"), nullable=False)
    
    tipo = Column(String(100), nullable=False)  # descoberta, ip_alterado, firmware_alterado, online, offline
    descricao = Column(Text)
    dados_anteriores = Column(JSONB)  # Snapshot do antes
    dados_novos = Column(JSONB)  # Snapshot do depois
    
    criado_em = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relacionamento
    ativo = relationship("Ativo", back_populates="eventos")


class Tag(Base):
    """7. TABELA: TAGS - Classificação e agrupamento de ativos"""
    __tablename__ = "tags"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(String(100), unique=True, nullable=False)
    cor = Column(String(7), default="#808080")  # Código hex
    descricao = Column(Text)
    
    criado_em = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relacionamento
    ativos = relationship("Ativo", secondary=ativo_tag_association, back_populates="tags")


# ═════════════════════════════════════════════════════════════════════════════
# LEGADO: SCHEMA ANTIGO (Compatibilidade com versões anteriores)
# ═════════════════════════════════════════════════════════════════════════════


class AlvoLegado(Base):
    """Tabela Legada 1: Alvos únicos"""
    __tablename__ = 'alvos'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ip_dominio = Column(String(255), unique=True, nullable=False)
    data_criacao = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    config_ataques = relationship("ConfigAtaqueLegado", back_populates="alvo")
    operacoes = relationship("HistoricoOperacoesLegado", back_populates="alvo")


class ConfigAtaqueLegado(Base):
    """Tabela Legada 2: Configurações técnicas de ataque"""
    __tablename__ = 'config_ataque'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    alvo_id = Column(Integer, ForeignKey('alvos.id'), nullable=False)
    porta = Column(Integer)
    protocolo = Column(String(50))
    servico_detectado = Column(String(100))
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamento
    alvo = relationship("AlvoLegado", back_populates="config_ataques")
    operacoes = relationship("HistoricoOperacoesLegado", back_populates="config")


class HistoricoOperacoesLegado(Base):
    """Tabela Legada 3: Histórico de operações e fases de ataque"""
    __tablename__ = 'historico_operacoes'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    alvo_id = Column(Integer, ForeignKey('alvos.id'), nullable=False)
    config_id = Column(Integer, ForeignKey('config_ataque.id'))
    
    attack_phase = Column(String(50))
    attack_type = Column(String(100))
    payload = Column(Text)
    
    success = Column(Boolean, default=False)
    response_code = Column(Integer)
    response_data = Column(Text)
    
    status_fase = Column(String(50))
    timestamp = Column(DateTime, default=datetime.utcnow)
    duration_ms = Column(Float)
    error_message = Column(Text)
    lesson_learned = Column(Text)
    confidence_score = Column(Float, default=0.5)
    
    # Relacionamentos
    alvo = relationship("AlvoLegado", back_populates="operacoes")
    config = relationship("ConfigAtaqueLegado", back_populates="operacoes")
    vulnerabilidades = relationship("VulnerabilidadesOcorrenciasLegado", back_populates="operacao")


class VulnerabilidadesOcorrenciasLegado(Base):
    """Tabela Legada 4: Vulnerabilidades encontradas"""
    __tablename__ = 'vulnerabilidades_ocorrencias'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    operacao_id = Column(Integer, ForeignKey('historico_operacoes.id'), nullable=False)
    
    criticidade = Column(String(20))
    titulo = Column(String(255), nullable=False)
    descricao = Column(Text)
    correcao = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamento
    operacao = relationship("HistoricoOperacoesLegado", back_populates="vulnerabilidades")
    
    def to_dict(self):
        return {
            'id': self.id,
            'operacao_id': self.operacao_id,
            'criticidade': self.criticidade,
            'titulo': self.titulo,
            'descricao': self.descricao,
            'correcao': self.correcao,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }


class AttackHistory(Base):
    """Modelo legado para compatibilidade com dados antigos"""
    __tablename__ = 'attack_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Informações do Alvo
    target_ip = Column(String(45))
    target_port = Column(Integer)
    target_service = Column(String(50))
    
    # Informações do Ataque
    attack_phase = Column(String(50))
    attack_type = Column(String(100))
    payload = Column(Text)
    
    # Resultados
    success = Column(Boolean, default=False)
    response_code = Column(Integer)
    response_data = Column(Text)
    
    # Metadados
    duration_ms = Column(Float)
    error_message = Column(Text)
    lesson_learned = Column(Text)
    confidence_score = Column(Float)
    
    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'target_ip': self.target_ip,
            'target_port': self.target_port,
            'target_service': self.target_service,
            'attack_phase': self.attack_phase,
            'attack_type': self.attack_type,
            'payload': self.payload,
            'success': self.success,
            'response_code': self.response_code,
            'response_data': json.loads(self.response_data) if self.response_data else None,
            'duration_ms': self.duration_ms,
            'error_message': self.error_message,
            'lesson_learned': self.lesson_learned,
            'confidence_score': self.confidence_score
        }


# ═════════════════════════════════════════════════════════════════════════════
# ALIASES PARA COMPATIBILIDADE (Manter nome Alvo, ConfigAtaque, etc)
# ═════════════════════════════════════════════════════════════════════════════

# Exports para manter compatibilidade com código existente
Alvo = AlvoLegado
ConfigAtaque = ConfigAtaqueLegado
HistoricoOperacoes = HistoricoOperacoesLegado
VulnerabilidadesOcorrencias = VulnerabilidadesOcorrenciasLegado


# ═════════════════════════════════════════════════════════════════════════════
# GERENCIADOR DE BANCO DE DADOS
# ═════════════════════════════════════════════════════════════════════════════


class DatabaseManager:
    """Gerenciador de banco de dados centralizado para KALI-CORE"""
    
    def __init__(self):
        """Inicializa o gerenciador de banco de dados"""
        self.engine = create_engine_from_env()
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.session = self.SessionLocal()
        
    def get_session(self):
        """Retorna uma nova sessão"""
        return self.SessionLocal()
    
    def close(self):
        """Fecha a sessão atual"""
        if self.session:
            self.session.close()
    
    def save_attack(self, attack_data: dict) -> int:
        """
        Salva um registro de ataque no banco de dados
        
        Args:
            attack_data: Dicionário com dados do ataque
            
        Returns:
            ID do ataque salvo
        """
        try:
            attack = AttackHistory(
                target_ip=attack_data.get('target_ip'),
                target_port=attack_data.get('target_port'),
                target_service=attack_data.get('target_service'),
                attack_phase=attack_data.get('attack_phase'),
                attack_type=attack_data.get('attack_type'),
                payload=attack_data.get('payload'),
                success=attack_data.get('success', False),
                response_code=attack_data.get('response_code'),
                response_data=json.dumps(attack_data.get('response_data', {})) if attack_data.get('response_data') else None,
                duration_ms=attack_data.get('duration_ms'),
                error_message=attack_data.get('error_message'),
                lesson_learned=attack_data.get('lesson_learned'),
                confidence_score=attack_data.get('confidence_score', 0.5)
            )
            
            self.session.add(attack)
            self.session.commit()
            self.session.refresh(attack)
            
            return attack.id
        except Exception as e:
            self.session.rollback()
            print(f"Erro ao salvar ataque: {e}")
            raise


# ═════════════════════════════════════════════════════════════════════════════
# UTILITÁRIOS DE BANCO DE DADOS
# ═════════════════════════════════════════════════════════════════════════════


def get_database_url():
    """Retorna a URL do banco de dados"""
    env_url = os.getenv("DATABASE_URL")
    if env_url:
        return env_url
    
    # Padrão: PostgreSQL (produção)
    postgres_default = "postgresql://kali:kali@kali_postgres:5432/kali_core"
    
    # Se não conseguir conectar em PostgreSQL, usa SQLite (desenvolvimento)
    try:
        engine = create_engine(postgres_default, connect_args={"timeout": 3})
        engine.connect()
        return postgres_default
    except:
        sqlite_path = os.getenv("SQLITE_PATH", "backend/data/kali_core.db")
        os.makedirs(os.path.dirname(sqlite_path), exist_ok=True)
        return f"sqlite:///{sqlite_path}"


def create_engine_from_env():
    """Cria engine SQLAlchemy"""
    database_url = get_database_url()
    return create_engine(database_url, echo=False, pool_pre_ping=True)


def init_db():
    """Inicializa o banco de dados criando todas as tabelas"""
    engine = create_engine_from_env()
    Base.metadata.create_all(bind=engine)
    print(f"✅ Banco de dados inicializado: {get_database_url()}")
    return engine


def get_session_factory():
    """Retorna factory de sessões"""
    engine = create_engine_from_env()
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ═════════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Novo schema
    "Ativo",
    "Identificador",
    "InterfaceDeRede",
    "Coleta",
    "DadosBrutos",
    "Evento",
    "Tag",
    # Legado (compatibilidade)
    "AlvoLegado",
    "ConfigAtaqueLegado",
    "HistoricoOperacoesLegado",
    "VulnerabilidadesOcorrenciasLegado",
    "AttackHistory",
    # Aliases (compatibilidade)
    "Alvo",
    "ConfigAtaque",
    "HistoricoOperacoes",
    "VulnerabilidadesOcorrencias",
    # Gerenciador de banco de dados
    "DatabaseManager",
    # Utilidades
    "Base",
    "ativo_tag_association",
    "init_db",
    "get_session_factory",
    "get_database_url",
    "create_engine_from_env",
]
