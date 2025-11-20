"""
Configuração do banco de dados usando SQLAlchemy
"""
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

db = SQLAlchemy()

# Modelo para dados do site (armazenado como JSON no banco)
class SiteData(db.Model):
    __tablename__ = 'site_data'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.JSON, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<SiteData {self.key}>'

# Modelo para usuários administrativos
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        """Define a senha com hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifica se a senha está correta"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Converte o usuário para dicionário"""
        return {
            'id': self.id,
            'username': self.username,
            'name': self.name,
            'email': self.email,
            'active': self.active,
            'created_at': self.created_at.strftime('%Y-%m-%d') if self.created_at else None
        }
    
    def __repr__(self):
        return f'<User {self.username}>'


def init_default_data():
    """Inicializa dados padrão do site"""
    default_data = {
        'logo': {
            'filename': 'logo.png',
            'alt': 'CASS - Congá de Aruanda São Sebastião'
        },
        'menu': {
            'items': [
                {'name': 'Início', 'url': '/', 'active': True},
                {'name': 'Sobre', 'url': '/sobre', 'active': True},
                {'name': 'Atividades', 'url': '/atividades', 'active': True},
                {'name': 'Consultas', 'url': '/consultas', 'active': True},
                {'name': 'Contato', 'url': '/contato', 'active': True}
            ]
        },
        'welcome': {
            'title': 'Bem-vindo ao CASS',
            'subtitle': 'Congá de Aruanda São Sebastião',
            'description': 'Um espaço dedicado à preservação, estudo e difusão das tradições culturais e espirituais afro-brasileiras, promovendo o respeito, a diversidade e o conhecimento ancestral.'
        },
        'valores': {
            'title': 'Nossos Valores',
            'items': []
        },
        'agenda': {
            'title': 'Agenda',
            'events': []
        },
        'videos': {
            'title': 'Vídeos',
            'items': []
        },
        'footer': {
            'name': 'CASS',
            'subtitle': 'Congá de Aruanda São Sebastião',
            'description': 'Preservando e difundindo as tradições afro-brasileiras.',
            'email': 'contato@cass.org.br',
            'phone': '(11) 99999-9999',
            'address': 'Endereço do CASS\nSão Paulo, SP',
            'hours': 'Segunda a Sexta: 9h às 18h\nSábado: 9h às 13h',
            'copyright': '© 2025 CASS. Todos os direitos reservados.',
            'social_media': {
                'whatsapp': '',
                'instagram': '',
                'facebook': '',
                'youtube': ''
            }
        },
        'whatsapp': {
            'number': '',
            'message': 'Olá! Gostaria de agendar uma consulta.'
        },
        'pages': {
            'sobre': {
                'title': 'Sobre o CASS',
                'subtitle': 'Conheça nossa história e missão',
                'historia': {
                    'paragraphs': []
                },
                'missao': {
                    'intro': '',
                    'items': []
                },
                'valores': {
                    'items': []
                },
                'visao': {
                    'content': ''
                }
            },
            'atividades': {
                'title': 'Nossas Atividades',
                'subtitle': 'Conheça o que oferecemos',
                'items': []
            },
            'consultas': {
                'title': 'Consultas',
                'subtitle': 'Agende sua consulta',
                'intro': '',
                'functioning': '',
                'hours': '',
                'values': '',
                'notes': ''
            },
            'contato': {
                'title': 'Contato',
                'subtitle': 'Entre em contato conosco',
                'content': ''
            }
        }
    }
    
    for key, value in default_data.items():
        site_data = SiteData(key=key, value=value)
        db.session.add(site_data)
    
    db.session.commit()

