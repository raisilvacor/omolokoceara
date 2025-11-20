# Guia de Deploy no Render

## 📋 Configuração do Banco de Dados PostgreSQL

### 1. Criar Banco de Dados no Render

1. Acesse https://render.com
2. Clique em **"New"** → **"PostgreSQL"**
3. Configure:
   - **Name**: `cass-db` (ou outro nome)
   - **Database**: `cass_db`
   - **User**: `cass_user`
   - **Region**: Escolha a mais próxima ao seu Web Service
   - **Plan**: Free (ou outro conforme necessário)
4. Clique em **"Create Database"**

### 2. Anotar Credenciais

Após criar o banco, anote:
- **Internal Database URL**: `postgresql://user:password@host:port/database`
  - Esta URL é usada dentro do Render (Web Service → Database)
  - Exemplo: `postgresql://cass_user:abc123@dpg-xxxxx-a.oregon-postgres.render.com/cass_db`

### 3. Configurar Web Service

No seu Web Service no Render:

1. Vá em **"Environment"** → **"Environment Variables"**
2. Adicione:
   - **Key**: `DATABASE_URL`
   - **Value**: Cole a **Internal Database URL** do banco de dados
   - **Key**: `SECRET_KEY` (opcional, mas recomendado)
   - **Value**: Gere uma chave secreta forte:
     ```bash
     python -c "import secrets; print(secrets.token_hex(32))"
     ```

### 4. Configurações do Web Service

- **Start Command**: `gunicorn app:app`
- **Build Command**: (deixe vazio, o Render faz automaticamente)
- **Python Version**: 3.11 ou 3.12

## 🔄 Migração de Dados (Opcional)

Se você já tem dados nos arquivos JSON (`data/site_data.json` e `data/users.json`), pode migrá-los:

### Opção 1: Migração Automática (Recomendado)

O sistema detecta automaticamente se há dados JSON e os migra na primeira inicialização.

### Opção 2: Migração Manual

Se preferir migrar manualmente, execute o script de migração:

```bash
python migrate_to_db.py
```

**Nota**: Este script deve ser executado localmente com acesso ao banco de dados, ou via Render Shell.

## 🔐 Segurança

### Senhas

- As senhas são automaticamente hasheadas usando `werkzeug.security`
- Nunca armazene senhas em texto plano
- O sistema migra senhas existentes automaticamente

### Variáveis de Ambiente

**Obrigatórias:**
- `DATABASE_URL`: URL de conexão do PostgreSQL

**Recomendadas:**
- `SECRET_KEY`: Chave secreta para sessões Flask (gerada automaticamente se não fornecida)

## 📊 Estrutura do Banco de Dados

### Tabela: `site_data`
Armazena todos os dados do site em formato JSON:
- `id`: ID único
- `key`: Chave da seção (ex: 'welcome', 'valores', 'footer')
- `value`: Dados JSON da seção
- `updated_at`: Data da última atualização

### Tabela: `users`
Armazena usuários administrativos:
- `id`: ID único
- `username`: Nome de usuário (único)
- `password_hash`: Hash da senha
- `name`: Nome completo
- `email`: Email
- `active`: Status ativo/inativo
- `created_at`: Data de criação

## ✅ Verificação

Após o deploy:

1. Acesse o site
2. Faça login no painel admin (`/admin/login`)
3. Verifique se os dados estão sendo carregados corretamente
4. Teste criar/editar conteúdo

## 🔄 Fallback para JSON

Se `DATABASE_URL` não estiver configurado, o sistema usa automaticamente os arquivos JSON:
- `data/site_data.json`
- `data/users.json`

Isso permite desenvolvimento local sem banco de dados.

## 🐛 Troubleshooting

### Erro: "relation does not exist"
- O banco ainda não foi inicializado
- Execute manualmente: `python -c "from app import app; from database import init_db; init_db(app)"`

### Erro: "could not connect to server"
- Verifique se `DATABASE_URL` está correto
- Use a **Internal Database URL** (não a External)
- Verifique se o banco está ativo no Render

### Dados não aparecem
- Verifique se a migração foi executada
- Confira os logs do Render para erros
- Verifique se as tabelas foram criadas no banco

## 📝 Notas Importantes

- O plano Free do Render pode colocar o banco em "sleep" após inatividade
- Para produção, considere um plano pago
- Faça backup regular dos dados
- Use variáveis de ambiente para configurações sensíveis

