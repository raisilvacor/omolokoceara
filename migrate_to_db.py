"""
Script para migrar dados dos arquivos JSON para o banco de dados PostgreSQL
Execute este script uma vez após configurar o banco de dados no Render
"""
import json
import os
from database import db, SiteData, User
from app import app

def migrate_json_to_db():
    """Migra dados dos arquivos JSON para o banco de dados"""
    
    with app.app_context():
        # Migrar dados do site
        data_file = os.path.join('data', 'site_data.json')
        if os.path.exists(data_file):
            print("Migrando dados do site...")
            with open(data_file, 'r', encoding='utf-8') as f:
                site_data = json.load(f)
            
            for key, value in site_data.items():
                existing = SiteData.query.filter_by(key=key).first()
                if existing:
                    existing.value = value
                    print(f"  Atualizado: {key}")
                else:
                    new_data = SiteData(key=key, value=value)
                    db.session.add(new_data)
                    print(f"  Adicionado: {key}")
            
            db.session.commit()
            print("✓ Dados do site migrados com sucesso!")
        else:
            print("⚠ Arquivo site_data.json não encontrado. Usando dados padrão.")
        
        # Migrar usuários
        users_file = os.path.join('data', 'users.json')
        if os.path.exists(users_file):
            print("\nMigrando usuários...")
            with open(users_file, 'r', encoding='utf-8') as f:
                users_data = json.load(f)
            
            from werkzeug.security import generate_password_hash
            
            for user_data in users_data.get('users', []):
                # Verificar se o usuário já existe
                existing = User.query.filter_by(username=user_data['username']).first()
                if existing:
                    print(f"  Usuário {user_data['username']} já existe, pulando...")
                    continue
                
                # Criar novo usuário
                new_user = User(
                    username=user_data['username'],
                    name=user_data.get('name', ''),
                    email=user_data.get('email', ''),
                    active=user_data.get('active', True)
                )
                
                # Se a senha não está em hash, criar hash
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
                print(f"  Migrado: {user_data['username']}")
            
            db.session.commit()
            print("✓ Usuários migrados com sucesso!")
        else:
            print("⚠ Arquivo users.json não encontrado.")
        
        print("\n✅ Migração concluída!")

if __name__ == '__main__':
    migrate_json_to_db()

