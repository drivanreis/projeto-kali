#!/usr/bin/env python3
"""
Modelos de Banco de Dados - Sistema de Inteligência de Logs
Histórico de Ataques para Fine-Tuning do Professor Kali
"""

import os
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json

Base = declarative_base()

class AttackHistory(Base):
    """Modelo para histórico de ataques"""
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
    
    def close(self):
        """Fecha conexão com banco de dados"""
        self.session.close()
