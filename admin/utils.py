import json
import os
from datetime import datetime

DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'site_data.json')
USERS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'users.json')

def load_data():
    """Carrega os dados do site do arquivo JSON"""
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_data(data):
    """Salva os dados do site no arquivo JSON"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def get_section_data(section):
    """Obtém dados de uma seção específica"""
    data = load_data()
    return data.get(section, {})

def update_section(section, new_data):
    """Atualiza uma seção específica"""
    data = load_data()
    data[section] = new_data
    save_data(data)
    return data

# Funções para gerenciar usuários
def load_users():
    """Carrega os usuários do arquivo JSON"""
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {'users': []}

def save_users(users_data):
    """Salva os usuários no arquivo JSON"""
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users_data, f, ensure_ascii=False, indent=4)

def get_user_by_username(username):
    """Busca um usuário pelo nome de usuário"""
    users_data = load_users()
    for user in users_data.get('users', []):
        if user.get('username') == username and user.get('active', True):
            return user
    return None

def verify_user(username, password):
    """Verifica se o usuário e senha estão corretos"""
    user = get_user_by_username(username)
    if user and user.get('password') == password:
        return user
    return None

def get_all_users():
    """Retorna todos os usuários"""
    users_data = load_users()
    return users_data.get('users', [])

def get_user_by_id(user_id):
    """Busca um usuário pelo ID"""
    users_data = load_users()
    for user in users_data.get('users', []):
        if user.get('id') == int(user_id):
            return user
    return None

def create_user(username, password, name, email):
    """Cria um novo usuário"""
    users_data = load_users()
    users = users_data.get('users', [])
    
    # Verificar se o username já existe
    if any(u.get('username') == username for u in users):
        return None
    
    # Gerar novo ID
    new_id = max([u.get('id', 0) for u in users], default=0) + 1
    
    new_user = {
        'id': new_id,
        'username': username,
        'password': password,
        'name': name,
        'email': email,
        'active': True,
        'created_at': datetime.now().strftime('%Y-%m-%d')
    }
    
    users.append(new_user)
    users_data['users'] = users
    save_users(users_data)
    return new_user

def update_user(user_id, username, password, name, email, active):
    """Atualiza um usuário existente"""
    users_data = load_users()
    users = users_data.get('users', [])
    
    for i, user in enumerate(users):
        if user.get('id') == int(user_id):
            # Verificar se o username já existe em outro usuário
            if username != user.get('username'):
                if any(u.get('username') == username and u.get('id') != int(user_id) for u in users):
                    return None
            
            users[i]['username'] = username
            if password:  # Só atualiza senha se fornecida
                users[i]['password'] = password
            users[i]['name'] = name
            users[i]['email'] = email
            users[i]['active'] = active
            
            users_data['users'] = users
            save_users(users_data)
            return users[i]
    
    return None

def delete_user(user_id):
    """Remove um usuário"""
    users_data = load_users()
    users = users_data.get('users', [])
    
    users = [u for u in users if u.get('id') != int(user_id)]
    users_data['users'] = users
    save_users(users_data)
    return True

