#!/usr/bin/env python3
"""
Modelos de Banco de Dados - Sistema de Inteligência de Logs
Histórico de Ataques para Fine-Tuning do Professor Kali
"""

import os
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import json

Base = declarative_base()

class Alvo(Base):
    """Tabela 1: Alvos únicos"""
    __tablename__ = 'alvos'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ip_dominio = Column(String(255), unique=True, nullable=False)
    data_criacao = Column(DateTime, default=datetime.now)
    
    # Relacionamentos
    config_ataques = relationship("ConfigAtaque", back_populates="alvo")
    operacoes = relationship("HistoricoOperacoes", back_populates="alvo")


class ConfigAtaque(Base):
    """Tabela 2: Configurações técnicas de ataque"""
    __tablename__ = 'config_ataque'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    alvo_id = Column(Integer, ForeignKey('alvos.id'), nullable=False)
    porta = Column(Integer)
    protocolo = Column(String(50))
    servico_detectado = Column(String(100))
    timestamp = Column(DateTime, default=datetime.now)
    
    # Relacionamento
    alvo = relationship("Alvo", back_populates="config_ataques")
    operacoes = relationship("HistoricoOperacoes", back_populates="config")


class HistoricoOperacoes(Base):
    """Tabela 3: Histórico de operações e fases de ataque"""
    __tablename__ = 'historico_operacoes'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    alvo_id = Column(Integer, ForeignKey('alvos.id'), nullable=False)
    config_id = Column(Integer, ForeignKey('config_ataque.id'))
    
    # Informações da operação
    attack_phase = Column(String(50))  # Fase 1-8
    attack_type = Column(String(100))  # nikto, gobuster, dnsrecon, etc
    payload = Column(Text)
    
    # Resultados
    success = Column(Boolean, default=False)
    response_code = Column(Integer)
    response_data = Column(Text)  # JSON
    
    # Metadados
    status_fase = Column(String(50))  # pendente, em_progresso, concluido, falhou
    timestamp = Column(DateTime, default=datetime.now)
    duration_ms = Column(Float)
    error_message = Column(Text)
    lesson_learned = Column(Text)
    confidence_score = Column(Float, default=0.5)
    
    # Relacionamentos
    alvo = relationship("Alvo", back_populates="operacoes")
    config = relationship("ConfigAtaque", back_populates="operacoes")
    analises = relationship("AnaliseEstrategica", back_populates="operacao")
    vulnerabilidades = relationship("VulnerabilidadesOcorrencias", back_populates="operacao")


class AnaliseEstrategica(Base):
    """Tabela 4: Motor de análise estratégica"""
    __tablename__ = 'analise_estrategica'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    operacao_id = Column(Integer, ForeignKey('historico_operacoes.id'), nullable=False)
    
    # Inteligência consolidada
    tempo_estimado_invasao = Column(Integer)  # em segundos
    criticidade = Column(String(20))  # baixa, media, alta, critica
    flags_detectadas = Column(Text)  # JSON list de flags
    recomendacao_invisibilidade = Column(Text)  # Recomendações para evasão
    timestamp = Column(DateTime, default=datetime.now)
    
    # Relacionamento
    operacao = relationship("HistoricoOperacoes", back_populates="analises")


class VulnerabilidadesOcorrencias(Base):
    """Tabela 5: Ocorrências de vulnerabilidades detectadas"""
    __tablename__ = 'vulnerabilidades_ocorrencias'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    operacao_id = Column(Integer, ForeignKey('historico_operacoes.id'), nullable=False)
    
    # Detalhes da vulnerabilidade
    criticidade = Column(String(20))  # critica, alta, media, baixa
    titulo = Column(String(255), nullable=False)
    descricao = Column(Text)
    correcao = Column(Text)
    
    # Metadados
    timestamp = Column(DateTime, default=datetime.now)
    
    # Relacionamento
    operacao = relationship("HistoricoOperacoes", back_populates="vulnerabilidades")
    
    def to_dict(self):
        """Converte para dicionário"""
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
    """Modelo legado para compatibilidade - compatibilidade com dados antigos"""
    __tablename__ = 'attack_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.now)
    
    # Informações do Alvo
    target_ip = Column(String(45))  # IPv4 ou IPv6
    target_port = Column(Integer)
    target_service = Column(String(50))
    
    # Informações do Ataque
    attack_phase = Column(String(50))  # Fase 1-8
    attack_type = Column(String(100))  # Tipo de ataque (nikto, gobuster, etc)
    payload = Column(Text)  # Payload utilizado
    
    # Resultados
    success = Column(Boolean, default=False)
    response_code = Column(Integer)
    response_data = Column(Text)  # Resposta do sistema em JSON
    
    # Metadados
    duration_ms = Column(Float)  # Duração em milissegundos
    error_message = Column(Text)
    
    # Para Fine-Tuning
    lesson_learned = Column(Text)  # Lição aprendida (para IA)
    confidence_score = Column(Float)  # Score de confiança (0-1)
    
    def to_dict(self):
        """Converte para dicionário"""
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
    
    def to_training_format(self):
        """Converte para formato de treinamento (JSONL para fine-tuning)"""
        return {
            'instruction': f"Análise de ataque {self.attack_type} na fase {self.attack_phase} contra {self.target_ip}:{self.target_port}",
            'input': {
                'target_ip': self.target_ip,
                'target_port': self.target_port,
                'target_service': self.target_service,
                'attack_phase': self.attack_phase,
                'attack_type': self.attack_type,
                'payload': self.payload
            },
            'output': {
                'success': self.success,
                'response_code': self.response_code,
                'response_data': json.loads(self.response_data) if self.response_data else None,
                'lesson_learned': self.lesson_learned or self._generate_lesson(),
                'confidence_score': self.confidence_score
            }
        }
    
    def _generate_lesson(self):
        """Gera lição aprendida automaticamente"""
        if self.success:
            return f"Ataque {self.attack_type} bem-sucedido na fase {self.attack_phase}. Payload eficaz: {self.payload[:100]}..."
        else:
            return f"Ataque {self.attack_type} falhou na fase {self.attack_phase}. Erro: {self.error_message or 'Desconhecido'}"


class DatabaseManager:
    """Gerenciador de banco de dados"""
    
    def __init__(self, db_path='backend/data/attack_history.db'):
        self.db_path = db_path
        # Cria diretório se não existir
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
    
    def save_attack(self, attack_data: dict) -> int:
        """Salva um registro de ataque"""
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
                response_data=json.dumps(attack_data.get('response_data')) if attack_data.get('response_data') else None,
                duration_ms=attack_data.get('duration_ms'),
                error_message=attack_data.get('error_message'),
                lesson_learned=attack_data.get('lesson_learned'),
                confidence_score=attack_data.get('confidence_score', 0.5)
            )
            
            self.session.add(attack)
            self.session.commit()
            
            attack_id = attack.id
            print(f"[DATABASE] Ataque salvo: ID {attack_id} - {attack.attack_type} contra {attack.target_ip}")
            
            return attack_id
        except Exception as e:
            self.session.rollback()
            print(f"[DATABASE] Erro ao salvar ataque: {e}")
            raise
    
    def get_attack_history(self, limit: int = 100, phase: str = None) -> list:
        """Recupera histórico de ataques"""
        try:
            query = self.session.query(AttackHistory)
            
            if phase:
                query = query.filter(AttackHistory.attack_phase == phase)
            
            attacks = query.order_by(AttackHistory.timestamp.desc()).limit(limit).all()
            
            return [attack.to_dict() for attack in attacks]
        except Exception as e:
            print(f"[DATABASE] Erro ao recuperar histórico: {e}")
            return []
    
    def export_training_dataset(self, output_path: str = 'backend/data/training_dataset.jsonl'):
        """Exporta dataset para fine-tuning (formato JSONL)"""
        try:
            attacks = self.session.query(AttackHistory).all()
            
            with open(output_path, 'w') as f:
                for attack in attacks:
                    training_entry = attack.to_training_format()
                    f.write(json.dumps(training_entry) + '\n')
            
            print(f"[DATABASE] Dataset exportado: {len(attacks)} registros em {output_path}")
            return len(attacks)
        except Exception as e:
            print(f"[DATABASE] Erro ao exportar dataset: {e}")
            raise
    
    def get_statistics(self) -> dict:
        """Retorna estatísticas do histórico"""
        try:
            total_attacks = self.session.query(AttackHistory).count()
            successful_attacks = self.session.query(AttackHistory).filter(AttackHistory.success == True).count()
            
            # Ataques por fase
            attacks_by_phase = {}
            for phase in ['fase_1', 'fase_2', 'fase_3', 'fase_4', 'fase_5', 'fase_6', 'fase_7', 'fase_8']:
                count = self.session.query(AttackHistory).filter(AttackHistory.attack_phase == phase).count()
                attacks_by_phase[phase] = count
            
            # Ataques por tipo (vetor de ataque)
            attacks_by_type = {}
            success_by_type = {}
            all_attacks = self.session.query(AttackHistory).all()
            for attack in all_attacks:
                attack_type = attack.attack_type or 'unknown'
                attacks_by_type[attack_type] = attacks_by_type.get(attack_type, 0) + 1
                if attack.success:
                    success_by_type[attack_type] = success_by_type.get(attack_type, 0) + 1
            
            # Taxa de sucesso por vetor de ataque
            success_rate_by_type = {}
            for attack_type in attacks_by_type:
                total = attacks_by_type[attack_type]
                successful = success_by_type.get(attack_type, 0)
                success_rate_by_type[attack_type] = successful / total if total > 0 else 0
            
            # Ataques por alvo (target_ip)
            attacks_by_target = {}
            success_by_target = {}
            for attack in all_attacks:
                target_ip = attack.target_ip or 'unknown'
                attacks_by_target[target_ip] = attacks_by_target.get(target_ip, 0) + 1
                if attack.success:
                    success_by_target[target_ip] = success_by_target.get(target_ip, 0) + 1
            
            # Taxa de sucesso por alvo
            success_rate_by_target = {}
            for target_ip in attacks_by_target:
                total = attacks_by_target[target_ip]
                successful = success_by_target.get(target_ip, 0)
                success_rate_by_target[target_ip] = successful / total if total > 0 else 0
            
            return {
                'total_attacks': total_attacks,
                'successful_attacks': successful_attacks,
                'success_rate': successful_attacks / total_attacks if total_attacks > 0 else 0,
                'attacks_by_phase': attacks_by_phase,
                'attacks_by_type': attacks_by_type,
                'success_rate_by_type': success_rate_by_type,
                'attacks_by_target': attacks_by_target,
                'success_rate_by_target': success_rate_by_target
            }
        except Exception as e:
            print(f"[DATABASE] Erro ao calcular estatísticas: {e}")
            return {}
    
    def get_alvos_unicos(self) -> list:
        """Retorna lista de alvos únicos da tabela Alvos"""
        try:
            alvos = self.session.query(Alvo.ip_dominio).distinct().all()
            return [alvo[0] for alvo in alvos if alvo[0]]
        except Exception as e:
            print(f"[DATABASE] Erro ao recuperar alvos únicos: {e}")
            # Fallback para tabela legada
            try:
                ips = self.session.query(AttackHistory.target_ip).distinct().all()
                return [ip[0] for ip in ips if ip[0]]
            except:
                return []
    
    def get_attack_types_unicos(self) -> list:
        """Retorna lista de tipos de ataque únicos"""
        try:
            tipos = self.session.query(HistoricoOperacoes.attack_type).distinct().all()
            result = [tipo[0] for tipo in tipos if tipo[0]]
            if not result:
                raise Exception("Nenhum tipo encontrado na nova tabela")
            return result
        except Exception as e:
            print(f"[DATABASE] Erro ao recuperar tipos de ataque: {e}")
            # Fallback para tabela legada
            try:
                tipos = self.session.query(AttackHistory.attack_type).distinct().all()
                return [tipo[0] for tipo in tipos if tipo[0]]
            except:
                return []
    
    def get_operacoes_por_filtros(self, alvo_ip: str = None, attack_type: str = None, limit: int = 9999) -> list:
        """Recupera operações com filtros"""
        try:
            query = self.session.query(HistoricoOperacoes)
            
            if alvo_ip:
                query = query.join(Alvo).filter(Alvo.ip_dominio == alvo_ip)
            if attack_type:
                query = query.filter(HistoricoOperacoes.attack_type == attack_type)
            
            operacoes = query.order_by(HistoricoOperacoes.timestamp.desc()).limit(limit).all()
            
            return [{
                'id': op.id,
                'alvo_ip': op.alvo.ip_dominio if op.alvo else None,
                'attack_type': op.attack_type,
                'attack_phase': op.attack_phase,
                'success': op.success,
                'timestamp': op.timestamp.isoformat() if op.timestamp else None,
                'status_fase': op.status_fase,
                'lesson_learned': op.lesson_learned
            } for op in operacoes]
        except Exception as e:
            print(f"[DATABASE] Erro ao recuperar operações: {e}")
            return []
    
    def get_vulnerabilidades_filtradas(self, alvo_ip: str = None, attack_type: str = None) -> list:
        """Retorna vulnerabilidades filtradas por alvo e tipo de ataque"""
        try:
            query = self.session.query(VulnerabilidadesOcorrencias).join(
                HistoricoOperacoes, VulnerabilidadesOcorrencias.operacao_id == HistoricoOperacoes.id
            ).join(
                Alvo, HistoricoOperacoes.alvo_id == Alvo.id
            )
            
            if alvo_ip:
                query = query.filter(Alvo.ip_dominio == alvo_ip)
            if attack_type:
                query = query.filter(HistoricoOperacoes.attack_type == attack_type)
            
            vulns = query.order_by(VulnerabilidadesOcorrencias.timestamp.desc()).all()
            
            return [vuln.to_dict() for vuln in vulns]
        except Exception as e:
            print(f"[DATABASE] Erro ao recuperar vulnerabilidades: {e}")
            return []
    
    def save_vulnerabilidade(self, operacao_id: int, criticidade: str, titulo: str, descricao: str, correcao: str) -> int:
        """Salva uma ocorrência de vulnerabilidade"""
        try:
            vuln = VulnerabilidadesOcorrencias(
                operacao_id=operacao_id,
                criticidade=criticidade,
                titulo=titulo,
                descricao=descricao,
                correcao=correcao
            )
            self.session.add(vuln)
            self.session.commit()
            
            print(f"[DATABASE] Vulnerabilidade salva: ID {vuln.id} na operação {operacao_id}")
            return vuln.id
        except Exception as e:
            self.session.rollback()
            print(f"[DATABASE] Erro ao salvar vulnerabilidade: {e}")
            raise
    
    def save_alvo(self, ip_dominio: str) -> int:
        """Salva ou recupera um alvo (IP/domínio)"""
        try:
            # Verifica se alvo já existe
            alvo_existente = self.session.query(Alvo).filter(Alvo.ip_dominio == ip_dominio).first()
            if alvo_existente:
                return alvo_existente.id
            
            # Cria novo alvo
            alvo = Alvo(ip_dominio=ip_dominio)
            self.session.add(alvo)
            self.session.commit()
            
            print(f"[DATABASE] Alvo salvo: ID {alvo.id} - {ip_dominio}")
            return alvo.id
        except Exception as e:
            self.session.rollback()
            print(f"[DATABASE] Erro ao salvar alvo: {e}")
            raise
    
    def save_operacao(self, alvo_id: int, attack_type: str, attack_phase: str, 
                     payload: str = None, success: bool = False, 
                     response_code: int = None, response_data: str = None) -> int:
        """Salva uma nova operação de ataque"""
        try:
            operacao = HistoricoOperacoes(
                alvo_id=alvo_id,
                attack_type=attack_type,
                attack_phase=attack_phase,
                payload=payload,
                success=success,
                response_code=response_code,
                response_data=response_data,
                status_fase='concluido' if success else 'falhou',
                timestamp=datetime.now()
            )
            self.session.add(operacao)
            self.session.commit()
            
            print(f"[DATABASE] Operação salva: ID {operacao.id} - {attack_type} contra alvo {alvo_id}")
            return operacao.id
        except Exception as e:
            self.session.rollback()
            print(f"[DATABASE] Erro ao salvar operação: {e}")
            raise
    
    def close(self):
        """Fecha conexão com banco de dados"""
        self.session.close()
