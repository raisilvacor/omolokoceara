from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from functools import wraps
import os

# Tentar usar banco de dados se DATABASE_URL estiver configurado, senão usar JSON
if os.environ.get('DATABASE_URL'):
    from database import db
    from admin.utils_db import (
        load_data, save_data, get_section_data, update_section,
        verify_user, get_all_users, get_user_by_id,
        create_user, update_user, delete_user
    )
    USE_DATABASE = True
else:
    from admin.utils import (
        load_data, save_data, get_section_data, update_section,
        verify_user, get_all_users, get_user_by_id,
        create_user, update_user, delete_user
    )
    USE_DATABASE = False

app = Flask(__name__)
# Usar variável de ambiente para secret_key em produção, ou gerar uma nova
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24).hex())

# Configurar banco de dados se disponível
if USE_DATABASE:
    # Configurar SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Inicializar banco de dados (será chamado na primeira requisição)
    db.init_app(app)
    
    # Flag para garantir inicialização única
    _db_initialized = False
    
    def init_database():
        """Inicializa o banco de dados e migra dados se necessário"""
        global _db_initialized
        if _db_initialized:
            return
        
        with app.app_context():
            try:
                db.create_all()
                
                # Tentar migrar dados dos arquivos JSON primeiro (preserva dados existentes)
                from migrate_data import migrate_json_to_database
                migration_result = migrate_json_to_database(app)
                
                # Se não houve migração e o banco está vazio, inicializar com dados padrão
                from database import SiteData, User
                if SiteData.query.count() == 0:
                    from database import init_default_data
                    init_default_data()
                    app.logger.info("Dados padrão inicializados no banco de dados")
                
                # Verificar se já existe usuário admin (apenas se não houver usuários)
                if User.query.count() == 0:
                    admin_user = User(
                        username='admin',
                        name='Administrador',
                        email='admin@cass.org.br',
                        active=True
                    )
                    admin_user.set_password('admin123')
                    db.session.add(admin_user)
                    db.session.commit()
                    app.logger.info("Usuário admin padrão criado")
                
                _db_initialized = True
            except Exception as e:
                app.logger.error(f"Erro ao inicializar banco de dados: {e}")
                import traceback
                app.logger.error(traceback.format_exc())
    
    # Inicializar banco na primeira requisição
    @app.before_request
    def ensure_database_initialized():
        if USE_DATABASE and not _db_initialized:
            init_database()

@app.context_processor
def inject_data():
    """Injeta dados globais em todos os templates"""
    data = load_data()
    return dict(data=data)

def login_required(f):
    """Decorator para proteger rotas administrativas"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# Rotas públicas
@app.route('/')
def index():
    data = load_data()
    return render_template('index.html', data=data)

@app.route('/sobre')
def sobre():
    data = load_data()
    sobre_data = data.get('pages', {}).get('sobre', {})
    return render_template('sobre.html', data=data, sobre=sobre_data)

@app.route('/atividades')
def atividades():
    data = load_data()
    return render_template('atividades.html', data=data)

@app.route('/contato')
def contato():
    data = load_data()
    return render_template('contato.html', data=data)

@app.route('/consultas')
def consultas():
    data = load_data()
    return render_template('consultas.html', data=data)

# Rotas administrativas
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = verify_user(username, password)
        if user:
            session['admin_logged_in'] = True
            session['admin_user_id'] = user.get('id')
            session['admin_username'] = user.get('username')
            session['admin_name'] = user.get('name')
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Usuário ou senha incorretos!', 'error')
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('admin_login'))

@app.route('/admin')
@login_required
def admin_dashboard():
    data = load_data()
    return render_template('admin/dashboard.html', data=data)

@app.route('/admin/edit/<section>', methods=['GET', 'POST'])
@login_required
def admin_edit(section):
    data = load_data()
    
    if request.method == 'POST':
        if section == 'welcome':
            update_section('welcome', {
                'title': request.form.get('title'),
                'subtitle': request.form.get('subtitle'),
                'description': request.form.get('description'),
                'button_text': request.form.get('button_text'),
                'button_url': request.form.get('button_url')
            })
        elif section == 'valores':
            valores = []
            for i in range(4):
                valores.append({
                    'icon': request.form.get(f'icon_{i}'),
                    'title': request.form.get(f'title_{i}'),
                    'description': request.form.get(f'description_{i}')
                })
            update_section('valores', {'title': request.form.get('title'), 'items': valores})
        elif section == 'agenda':
            events = []
            event_count = int(request.form.get('event_count', 0))
            for i in range(event_count):
                events.append({
                    'day': request.form.get(f'day_{i}'),
                    'month': request.form.get(f'month_{i}'),
                    'title': request.form.get(f'title_{i}'),
                    'time': request.form.get(f'time_{i}'),
                    'description': request.form.get(f'description_{i}')
                })
            update_section('agenda', {
                'title': request.form.get('title'),
                'description': request.form.get('description'),
                'events': events
            })
        elif section == 'videos':
            videos = []
            video_count = int(request.form.get('video_count', 0))
            for i in range(video_count):
                videos.append({
                    'id': request.form.get(f'video_id_{i}'),
                    'title': request.form.get(f'video_title_{i}')
                })
            update_section('videos', {
                'title': request.form.get('title'),
                'description': request.form.get('description'),
                'videos': videos
            })
        elif section == 'footer':
            update_section('footer', {
                'name': request.form.get('name'),
                'subtitle': request.form.get('subtitle'),
                'description': request.form.get('description'),
                'email': request.form.get('email'),
                'phone': request.form.get('phone'),
                'address': request.form.get('address'),
                'hours': request.form.get('hours'),
                'copyright': request.form.get('copyright'),
                'social_media': {
                    'whatsapp': request.form.get('whatsapp_url', ''),
                    'instagram': request.form.get('instagram_url', ''),
                    'facebook': request.form.get('facebook_url', ''),
                    'youtube': request.form.get('youtube_url', '')
                }
            })
        elif section == 'whatsapp':
            update_section('whatsapp', {
                'number': request.form.get('number'),
                'message': request.form.get('message')
            })
        elif section == 'consultas':
            # Processar dados da página Consultas
            consultas_data = data.get('pages', {}).get('consultas', {})
            
            # Introdução - parágrafos
            intro_paragraphs = []
            intro_count = int(request.form.get('intro_paragraph_count', 0))
            for i in range(intro_count):
                para = request.form.get(f'intro_para_{i}')
                if para:
                    intro_paragraphs.append(para)
            
            # Como Funciona - lista
            functioning_items = []
            functioning_count = int(request.form.get('functioning_list_count', 0))
            for i in range(functioning_count):
                item = request.form.get(f'functioning_item_{i}')
                if item:
                    functioning_items.append(item)
            
            # Observações - lista
            notes_items = []
            notes_count = int(request.form.get('notes_list_count', 0))
            for i in range(notes_count):
                item = request.form.get(f'notes_item_{i}')
                if item:
                    notes_items.append(item)
            
            # Atualizar dados da página consultas
            pages_data = data.get('pages', {})
            pages_data['consultas'] = {
                'title': request.form.get('page_title'),
                'subtitle': request.form.get('page_subtitle'),
                'intro': {
                    'title': request.form.get('intro_title'),
                    'paragraphs': intro_paragraphs
                },
                'functioning': {
                    'title': request.form.get('functioning_title'),
                    'description': request.form.get('functioning_description'),
                    'items': functioning_items
                },
                'hours': {
                    'title': request.form.get('hours_title'),
                    'description': request.form.get('hours_description'),
                    'content': request.form.get('hours_content')
                },
                'values': {
                    'title': request.form.get('values_title'),
                    'content': request.form.get('values_content')
                },
                'cta': {
                    'title': request.form.get('cta_title'),
                    'description': request.form.get('cta_description')
                },
                'notes': {
                    'title': request.form.get('notes_title'),
                    'items': notes_items
                }
            }
            update_section('pages', pages_data)
            flash('Página Consultas atualizada com sucesso!', 'success')
            return redirect(url_for('admin_edit', section='consultas'))
        elif section == 'sobre':
            # Processar dados da página Sobre
            sobre_data = data.get('pages', {}).get('sobre', {})
            
            # História
            historia_paragraphs = []
            historia_count = int(request.form.get('historia_paragraph_count', 0))
            for i in range(historia_count):
                para = request.form.get(f'historia_para_{i}')
                if para:
                    historia_paragraphs.append(para)
            
            # Missão
            missao_list = []
            missao_count = int(request.form.get('missao_list_count', 0))
            for i in range(missao_count):
                item = request.form.get(f'missao_item_{i}')
                if item:
                    missao_list.append(item)
            
            # Valores
            valores_items = []
            for i in range(4):
                valores_items.append({
                    'title': request.form.get(f'valor_title_{i}'),
                    'description': request.form.get(f'valor_desc_{i}')
                })
            
            sobre_data = {
                'title': request.form.get('page_title'),
                'subtitle': request.form.get('page_subtitle'),
                'historia': {
                    'title': request.form.get('historia_title'),
                    'paragraphs': historia_paragraphs
                },
                'missao': {
                    'title': request.form.get('missao_title'),
                    'intro': request.form.get('missao_intro'),
                    'list': missao_list
                },
                'valores': {
                    'title': request.form.get('valores_title'),
                    'items': valores_items
                },
                'visao': {
                    'title': request.form.get('visao_title'),
                    'content': request.form.get('visao_content')
                }
            }
            
            # Salvar na estrutura correta
            if 'pages' not in data:
                data['pages'] = {}
            data['pages']['sobre'] = sobre_data
            save_data(data)
        elif section == 'atividades':
            # Esta seção ainda não tem formulário completo
            pass
        
        flash('Dados atualizados com sucesso!', 'success')
        return redirect(url_for('admin_edit', section=section))
    
    # Carregar dados da seção
    if section == 'sobre':
        section_data = data.get('pages', {}).get('sobre', {})
    elif section == 'consultas':
        section_data = data.get('pages', {}).get('consultas', {})
    else:
        section_data = get_section_data(section)
    return render_template(f'admin/edit_{section}.html', section=section, data=section_data)

# Rotas de gerenciamento de usuários
@app.route('/admin/users')
@login_required
def admin_users():
    users = get_all_users()
    return render_template('admin/users.html', users=users)

@app.route('/admin/users/new', methods=['GET', 'POST'])
@login_required
def admin_user_new():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        name = request.form.get('name')
        email = request.form.get('email')
        
        if not username or not password or not name or not email:
            flash('Todos os campos são obrigatórios!', 'error')
            return redirect(url_for('admin_user_new'))
        
        user = create_user(username, password, name, email)
        if user:
            flash('Usuário criado com sucesso!', 'success')
            return redirect(url_for('admin_users'))
        else:
            flash('Nome de usuário já existe!', 'error')
            return redirect(url_for('admin_user_new'))
    
    return render_template('admin/user_edit.html', user=None)

@app.route('/admin/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def admin_user_edit(user_id):
    user = get_user_by_id(user_id)
    if not user:
        flash('Usuário não encontrado!', 'error')
        return redirect(url_for('admin_users'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')  # Pode ser vazio (não altera)
        name = request.form.get('name')
        email = request.form.get('email')
        active = request.form.get('active') == 'on'
        
        if not username or not name or not email:
            flash('Todos os campos são obrigatórios!', 'error')
            return redirect(url_for('admin_user_edit', user_id=user_id))
        
        updated_user = update_user(user_id, username, password, name, email, active)
        if updated_user:
            flash('Usuário atualizado com sucesso!', 'success')
            return redirect(url_for('admin_users'))
        else:
            flash('Nome de usuário já existe!', 'error')
            return redirect(url_for('admin_user_edit', user_id=user_id))
    
    return render_template('admin/user_edit.html', user=user)

@app.route('/admin/users/delete/<int:user_id>', methods=['POST'])
@login_required
def admin_user_delete(user_id):
    # Não permitir deletar o próprio usuário
    if session.get('admin_user_id') == user_id:
        flash('Você não pode deletar seu próprio usuário!', 'error')
        return redirect(url_for('admin_users'))
    
    user = get_user_by_id(user_id)
    if not user:
        flash('Usuário não encontrado!', 'error')
        return redirect(url_for('admin_users'))
    
    delete_user(user_id)
    flash('Usuário removido com sucesso!', 'success')
    return redirect(url_for('admin_users'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)

