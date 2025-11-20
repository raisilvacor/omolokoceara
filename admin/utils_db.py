"""
Funções utilitárias para gerenciar dados do site e usuários usando banco de dados
"""
from database import db, SiteData, User
from flask import current_app

def load_data():
    """Carrega os dados do site do banco de dados"""
    try:
        data = {}
        site_data_list = SiteData.query.all()
        for item in site_data_list:
            data[item.key] = item.value
        return data
    except Exception as e:
        current_app.logger.error(f"Erro ao carregar dados: {e}")
        return {}

def save_data(data):
    """Salva os dados do site no banco de dados"""
    try:
        for key, value in data.items():
            site_data = SiteData.query.filter_by(key=key).first()
            if site_data:
                site_data.value = value
            else:
                site_data = SiteData(key=key, value=value)
                db.session.add(site_data)
        db.session.commit()
        return True
    except Exception as e:
        current_app.logger.error(f"Erro ao salvar dados: {e}")
        db.session.rollback()
        return False

def get_section_data(section):
    """Obtém dados de uma seção específica"""
    try:
        site_data = SiteData.query.filter_by(key=section).first()
        if site_data:
            return site_data.value
        return {}
    except Exception as e:
        current_app.logger.error(f"Erro ao obter seção {section}: {e}")
        return {}

def update_section(section, new_data):
    """Atualiza uma seção específica"""
    try:
        site_data = SiteData.query.filter_by(key=section).first()
        if site_data:
            site_data.value = new_data
        else:
            site_data = SiteData(key=section, value=new_data)
            db.session.add(site_data)
        db.session.commit()
        return True
    except Exception as e:
        current_app.logger.error(f"Erro ao atualizar seção {section}: {e}")
        db.session.rollback()
        return False

# Funções para gerenciar usuários
def get_user_by_username(username):
    """Busca um usuário pelo nome de usuário"""
    try:
        user = User.query.filter_by(username=username, active=True).first()
        if user:
            return user.to_dict()
        return None
    except Exception as e:
        current_app.logger.error(f"Erro ao buscar usuário: {e}")
        return None

def verify_user(username, password):
    """Verifica se o usuário e senha estão corretos"""
    try:
        user = User.query.filter_by(username=username, active=True).first()
        if user and user.check_password(password):
            return user.to_dict()
        return None
    except Exception as e:
        current_app.logger.error(f"Erro ao verificar usuário: {e}")
        return None

def get_all_users():
    """Retorna todos os usuários"""
    try:
        users = User.query.all()
        return [user.to_dict() for user in users]
    except Exception as e:
        current_app.logger.error(f"Erro ao listar usuários: {e}")
        return []

def get_user_by_id(user_id):
    """Busca um usuário pelo ID"""
    try:
        user = User.query.get(int(user_id))
        if user:
            return user.to_dict()
        return None
    except Exception as e:
        current_app.logger.error(f"Erro ao buscar usuário por ID: {e}")
        return None

def create_user(username, password, name, email):
    """Cria um novo usuário"""
    try:
        # Verificar se o username já existe
        if User.query.filter_by(username=username).first():
            return None
        
        new_user = User(
            username=username,
            name=name,
            email=email,
            active=True
        )
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        return new_user.to_dict()
    except Exception as e:
        current_app.logger.error(f"Erro ao criar usuário: {e}")
        db.session.rollback()
        return None

def update_user(user_id, username, password, name, email, active):
    """Atualiza um usuário existente"""
    try:
        user = User.query.get(int(user_id))
        if not user:
            return None
        
        # Verificar se o username já existe em outro usuário
        existing_user = User.query.filter_by(username=username).first()
        if existing_user and existing_user.id != int(user_id):
            return None
        
        user.username = username
        if password:  # Só atualiza senha se fornecida
            user.set_password(password)
        user.name = name
        user.email = email
        user.active = active
        
        db.session.commit()
        return user.to_dict()
    except Exception as e:
        current_app.logger.error(f"Erro ao atualizar usuário: {e}")
        db.session.rollback()
        return None

def delete_user(user_id):
    """Remove um usuário"""
    try:
        user = User.query.get(int(user_id))
        if user:
            db.session.delete(user)
            db.session.commit()
            return True
        return False
    except Exception as e:
        current_app.logger.error(f"Erro ao deletar usuário: {e}")
        db.session.rollback()
        return False

