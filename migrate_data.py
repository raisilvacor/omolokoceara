"""
Script de migração automática de dados JSON para PostgreSQL
Preserva todos os dados existentes sem perda de informação
"""
import json
import os
import shutil
from datetime import datetime
from database import db, SiteData, User
from werkzeug.security import generate_password_hash

def backup_json_files():
    """Cria backup dos arquivos JSON antes da migração"""
    backup_dir = os.path.join('data', 'backups')
    os.makedirs(backup_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    files_to_backup = ['site_data.json', 'users.json']
    backed_up = []
    
    for filename in files_to_backup:
        source = os.path.join('data', filename)
        if os.path.exists(source):
            backup_filename = f"{filename}.backup_{timestamp}"
            backup_path = os.path.join(backup_dir, backup_filename)
            shutil.copy2(source, backup_path)
            backed_up.append(backup_path)
            print(f"  💾 Backup criado: {backup_filename}")
    
    return backed_up

def migrate_json_to_database(app):
    """
    Migra todos os dados dos arquivos JSON para o banco de dados
    Preserva todas as informações existentes
    """
    with app.app_context():
        try:
            # Verificar se já existe dados no banco
            existing_data_count = SiteData.query.count()
            existing_users_count = User.query.count()
            
            if existing_data_count > 0 and existing_users_count > 0:
                print("✓ Dados já existem no banco. Pulando migração.")
                return False
            
            # Criar backup antes de migrar
            print("💾 Criando backup dos arquivos JSON...")
            backup_json_files()
            print()
            
            migrated = False
            
            # 1. Migrar dados do site (site_data.json)
            data_file = os.path.join('data', 'site_data.json')
            if os.path.exists(data_file):
                print("📦 Migrando dados do site...")
                with open(data_file, 'r', encoding='utf-8') as f:
                    site_data = json.load(f)
                
                for key, value in site_data.items():
                    # Verificar se a chave já existe no banco
                    existing = SiteData.query.filter_by(key=key).first()
                    if existing:
                        # Atualizar apenas se o banco estiver vazio (primeira migração)
                        if existing_data_count == 0:
                            existing.value = value
                            print(f"  ✓ Atualizado: {key}")
                            migrated = True
                        else:
                            print(f"  ⊘ Mantido (já existe): {key}")
                    else:
                        # Criar novo registro
                        new_data = SiteData(key=key, value=value)
                        db.session.add(new_data)
                        print(f"  ✓ Adicionado: {key}")
                        migrated = True
                
                if migrated:
                    db.session.commit()
                    print("✅ Dados do site migrados com sucesso!")
                else:
                    print("ℹ️  Dados do site já estão no banco.")
            else:
                print("⚠️  Arquivo site_data.json não encontrado.")
            
            # 2. Migrar usuários (users.json)
            users_file = os.path.join('data', 'users.json')
            if os.path.exists(users_file):
                print("\n👥 Migrando usuários...")
                with open(users_file, 'r', encoding='utf-8') as f:
                    users_data = json.load(f)
                
                users_migrated = False
                for user_data in users_data.get('users', []):
                    username = user_data.get('username')
                    if not username:
                        continue
                    
                    # Verificar se o usuário já existe
                    existing_user = User.query.filter_by(username=username).first()
                    if existing_user:
                        print(f"  ⊘ Usuário '{username}' já existe, mantendo...")
                        continue
                    
                    # Criar novo usuário
                    new_user = User(
                        username=username,
                        name=user_data.get('name', ''),
                        email=user_data.get('email', ''),
                        active=user_data.get('active', True)
                    )
                    
                    # Converter senha para hash (se ainda não estiver em hash)
                    password = user_data.get('password', '')
                    if password:
                        new_user.set_password(password)
                    
                    # Definir data de criação se disponível
                    if 'created_at' in user_data:
                        try:
                            from datetime import datetime
                            new_user.created_at = datetime.strptime(user_data['created_at'], '%Y-%m-%d')
                        except:
                            pass
                    
                    db.session.add(new_user)
                    print(f"  ✓ Migrado: {username}")
                    users_migrated = True
                
                if users_migrated:
                    db.session.commit()
                    print("✅ Usuários migrados com sucesso!")
                else:
                    print("ℹ️  Usuários já estão no banco.")
            else:
                print("⚠️  Arquivo users.json não encontrado.")
            
            return migrated or users_migrated
            
        except Exception as e:
            print(f"❌ Erro durante migração: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return False

