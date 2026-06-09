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
    """Tabela Legada 1: Clientes únicos"""
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
    
    # Informações do Cliente
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
    response_data = Column(JSONB)  # Alterado de Text para JSONB para payloads dinâmicos
    
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
# ALIASES PARA COMPATIBILIDADE (Manter nome Cliente, ConfigAtaque, etc)
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
            # Trata response_data: pode ser dict ou string (json.dumps)
            response_data = attack_data.get('response_data')
            if isinstance(response_data, dict):
                response_data = response_data
            elif isinstance(response_data, str):
                try:
                    response_data = json.loads(response_data)
                except:
                    response_data = {}
            else:
                response_data = {}
            
            attack = AttackHistory(
                target_ip=attack_data.get('target_ip'),
                target_port=attack_data.get('target_port'),
                target_service=attack_data.get('target_service'),
                attack_phase=attack_data.get('attack_phase'),
                attack_type=attack_data.get('attack_type'),
                payload=attack_data.get('payload'),
                success=attack_data.get('success', False),
                response_code=attack_data.get('response_code'),
                response_data=response_data,
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
    
    def save_alvo(self, target: str) -> int:
        """
        Salva um alvo no banco de dados (compatibilidade com main_fastapi.py)
        
        Args:
            target: IP ou domínio do alvo
            
        Returns:
            ID do alvo salvo
        """
        try:
            # Verifica se cliente já existe
            alvo_existente = self.session.query(AlvoLegado).filter(
                AlvoLegado.ip_dominio == target
            ).first()
            
            if alvo_existente:
                return alvo_existente.id
            
            # Cria novo cliente
            alvo = AlvoLegado(ip_dominio=target)
            self.session.add(alvo)
            self.session.commit()
            self.session.refresh(alvo)
            
            return alvo.id
        except Exception as e:
            self.session.rollback()
            print(f"Erro ao salvar alvo: {e}")
            raise
    
    def save_operacao(self, alvo_id: int, attack_type: str, attack_phase: str, 
                     payload: str, success: bool, response_code: int, 
                     response_data: str) -> int:
        """
        Salva uma operação de ataque no banco de dados (compatibilidade com main_fastapi.py)
        
        Args:
            alvo_id: ID do alvo
            attack_type: Tipo de ataque
            attack_phase: Fase do ataque
            payload: Payload do ataque
            success: Sucesso da operação
            response_code: Código de resposta
            response_data: Dados de resposta (JSON string)
            
        Returns:
            ID da operação salva
        """
        try:
            operacao = HistoricoOperacoesLegado(
                alvo_id=alvo_id,
                config_id=None,
                attack_phase=attack_phase,
                attack_type=attack_type,
                payload=payload,
                success=success,
                response_code=response_code,
                response_data=response_data,
                status_fase='concluido' if success else 'falhou',
                duration_ms=0.0,
                error_message=None if success else 'Operação falhou',
                lesson_learned=f'Operação {attack_type} {"bem-sucedida" if success else "falhou"}',
                confidence_score=0.8 if success else 0.3
            )
            
            self.session.add(operacao)
            self.session.commit()
            self.session.refresh(operacao)
            
            return operacao.id
        except Exception as e:
            self.session.rollback()
            print(f"Erro ao salvar operação: {e}")
            raise
    
    def save_vulnerabilidade(self, operacao_id: int, criticidade: str, 
                           titulo: str, descricao: str, correcao: str) -> int:
        """
        Salva uma vulnerabilidade no banco de dados (compatibilidade com main_fastapi.py)
        
        Args:
            operacao_id: ID da operação
            criticidade: Criticidade da vulnerabilidade
            titulo: Título da vulnerabilidade
            descricao: Descrição da vulnerabilidade
            correcao: Correção recomendada
            
        Returns:
            ID da vulnerabilidade salva
        """
        try:
            vuln = VulnerabilidadesOcorrenciasLegado(
                operacao_id=operacao_id,
                criticidade=criticidade,
                titulo=titulo,
                descricao=descricao,
                correcao=correcao
            )
            
            self.session.add(vuln)
            self.session.commit()
            self.session.refresh(vuln)
            
            return vuln.id
        except Exception as e:
            self.session.rollback()
            print(f"Erro ao salvar vulnerabilidade: {e}")
            raise
    
    def get_attack_history(self, limit: int = 100, phase: str = None) -> list:
        """
        Recupera histórico de ataques do banco de dados
        
        Args:
            limit: Limite de registros
            phase: Filtro por fase de ataque
            
        Returns:
            Lista de ataques em formato de dicionário
        """
        try:
            query = self.session.query(AttackHistory)
            
            if phase:
                query = query.filter(AttackHistory.attack_phase == phase)
            
            attacks = query.order_by(AttackHistory.timestamp.desc()).limit(limit).all()
            
            return [attack.to_dict() for attack in attacks]
        except Exception as e:
            self.session.rollback()
            print(f"Erro ao recuperar histórico: {e}")
            return []
    
    def get_alvos_unicos(self) -> list:
        """
        Recupera lista de alvos únicos do histórico de ataques
        
        Returns:
            Lista de IPs únicos
        """
        try:
            alvos = self.session.query(AttackHistory.target_ip).distinct().all()
            return [alvo[0] for alvo in alvos if alvo[0]]
        except Exception as e:
            self.session.rollback()
            print(f"Erro ao recuperar alvos únicos: {e}")
            return []
    
    def get_attack_types_unicos(self) -> list:
        """
        Recupera lista de tipos de ataque únicos do histórico
        
        Returns:
            Lista de tipos de ataque únicos
        """
        try:
            tipos = self.session.query(AttackHistory.attack_type).distinct().all()
            return [tipo[0] for tipo in tipos if tipo[0]]
        except Exception as e:
            self.session.rollback()
            print(f"Erro ao recuperar tipos de ataque: {e}")
            return []
    
    def get_vulnerabilidades_filtradas(self, alvo_ip: str = None, attack_type: str = None) -> list:
        """
        Recupera vulnerabilidades filtradas por alvo e tipo de ataque
        
        Args:
            alvo_ip: Filtro por IP do alvo
            attack_type: Filtro por tipo de ataque
            
        Returns:
            Lista de vulnerabilidades em formato de dicionário
        """
        try:
            query = self.session.query(VulnerabilidadesOcorrenciasLegado)
            
            if alvo_ip or attack_type:
                # Join com operações para filtrar
                query = query.join(HistoricoOperacoesLegado)
                
                if alvo_ip:
                    # Filtra por cliente através de operações
                    operacoes_alvo = self.session.query(HistoricoOperacoesLegado.id).join(
                        AlvoLegado
                    ).filter(AlvoLegado.ip_dominio == alvo_ip).all()
                    op_ids = [op[0] for op in operacoes_alvo]
                    query = query.filter(VulnerabilidadesOcorrenciasLegado.operacao_id.in_(op_ids))
                
                if attack_type:
                    operacoes_tipo = self.session.query(HistoricoOperacoesLegado.id).filter(
                        HistoricoOperacoesLegado.attack_type == attack_type
                    ).all()
                    op_ids = [op[0] for op in operacoes_tipo]
                    query = query.filter(VulnerabilidadesOcorrenciasLegado.operacao_id.in_(op_ids))
            
            vulns = query.all()
            return [vuln.to_dict() for vuln in vulns]
        except Exception as e:
            self.session.rollback()
            print(f"Erro ao recuperar vulnerabilidades: {e}")
            return []
    
    def get_operacoes_por_filtros(self, alvo_ip: str = None, attack_type: str = None) -> list:
        """
        Recupera operações filtradas por alvo e tipo de ataque
        """
        try:
            query = self.session.query(HistoricoOperacoesLegado)
            if alvo_ip:
                query = query.join(AlvoLegado).filter(AlvoLegado.ip_dominio == alvo_ip)
            if attack_type:
                query = query.filter(HistoricoOperacoesLegado.attack_type == attack_type)
            operacoes = query.all()
            return [{
                'id': op.id,
                'alvo_id': op.alvo_id,
                'attack_phase': op.attack_phase,
                'attack_type': op.attack_type,
                'payload': op.payload,
                'success': op.success,
                'response_code': op.response_code,
                'response_data': op.response_data,
                'status_fase': op.status_fase,
                'timestamp': op.timestamp.isoformat() if op.timestamp else None,
                'duration_ms': op.duration_ms,
                'error_message': op.error_message,
                'lesson_learned': op.lesson_learned,
                'confidence_score': op.confidence_score
            } for op in operacoes]
        except Exception as e:
            self.session.rollback()
            print(f"Erro ao recuperar operacoes por filtros: {e}")
            return []

    def get_statistics(self) -> dict:
        """
        Calcula estatísticas do histórico de ataques
        
        Returns:
            Dicionário com estatísticas
        """
        try:
            total_attacks = self.session.query(AttackHistory).count()
            successful_attacks = self.session.query(AttackHistory).filter(
                AttackHistory.success == True
            ).count()
            failed_attacks = total_attacks - successful_attacks
            
            # Ataques por tipo
            attacks_by_type = {}
            tipos = self.get_attack_types_unicos()
            for tipo in tipos:
                count = self.session.query(AttackHistory).filter(
                    AttackHistory.attack_type == tipo
                ).count()
                attacks_by_type[tipo] = count
            
            # Ataques por fase
            attacks_by_phase = {}
            fases = ['fase_1', 'fase_2', 'fase_3', 'fase_4', 'fase_5', 'fase_6', 'fase_7', 'fase_8']
            for fase in fases:
                count = self.session.query(AttackHistory).filter(
                    AttackHistory.attack_phase == fase
                ).count()
                if count > 0:
                    attacks_by_phase[fase] = count
            
            return {
                'total_attacks': total_attacks,
                'successful_attacks': successful_attacks,
                'failed_attacks': failed_attacks,
                'success_rate': (successful_attacks / total_attacks * 100) if total_attacks > 0 else 0,
                'attacks_by_type': attacks_by_type,
                'attacks_by_phase': attacks_by_phase,
                'unique_targets': len(self.get_alvos_unicos())
            }
        except Exception as e:
            self.session.rollback()
            print(f"Erro ao calcular estatísticas: {e}")
            return {}
    
    def export_training_dataset(self, output_path: str) -> int:
        """
        Exporta dataset para fine-tuning do Professor Kali
        
        Args:
            output_path: Caminho do arquivo de saída
            
        Returns:
            Número de registros exportados
        """
        try:
            attacks = self.get_attack_history(limit=10000)
            
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, 'w') as f:
                for attack in attacks:
                    f.write(json.dumps(attack) + '\n')
            
            return len(attacks)
        except Exception as e:
            print(f"Erro ao exportar dataset: {e}")
            return 0


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
# TABELA: CLIENTE - Cadastro puritano de clientes
# ═════════════════════════════════════════════════════════════════════════════

class Cliente(Base):
    """Cadastro simples de clientes com IP e nome"""
    __tablename__ = "cliente"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome_cliente = Column(String(255), nullable=False)
    ip = Column(String(50), nullable=False)
    criado_em = Column(DateTime, default=datetime.utcnow, nullable=False)


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
    # Cadastro de clientes
    "Cliente",
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
