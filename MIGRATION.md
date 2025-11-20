# Guia de Migração para Banco de Dados

## ✅ Migração Automática Implementada

O sistema agora migra **automaticamente** todos os dados dos arquivos JSON para o banco de dados PostgreSQL quando o `DATABASE_URL` estiver configurado.

## 🔄 Como Funciona

1. **Detecção Automática**: Quando o `DATABASE_URL` está configurado, o sistema usa o banco de dados
2. **Migração na Primeira Execução**: Na primeira inicialização, todos os dados dos arquivos JSON são migrados
3. **Backup Automático**: Antes da migração, um backup dos arquivos JSON é criado em `data/backups/`
4. **Preservação de Dados**: Nenhuma informação é perdida - todos os dados existentes são preservados

## 📋 O que é Migrado

### Dados do Site (`site_data.json`):
- ✅ Logo e configurações
- ✅ Menu de navegação
- ✅ Seção "Bem-vindo ao CASS"
- ✅ Nossos Valores
- ✅ Sobre o CASS
- ✅ Nossas Atividades
- ✅ Agenda
- ✅ Vídeos
- ✅ Rodapé (incluindo redes sociais)
- ✅ Configurações do WhatsApp
- ✅ Todas as páginas (Sobre, Atividades, Consultas, Contato)

### Usuários (`users.json`):
- ✅ Todos os usuários administrativos
- ✅ Senhas convertidas para hash (segurança)
- ✅ Informações de perfil (nome, email, status)

## 🔐 Segurança

- **Senhas**: Todas as senhas são automaticamente convertidas para hash usando `werkzeug.security`
- **Backup**: Backups automáticos são criados antes de qualquer migração
- **Validação**: O sistema verifica se os dados já existem antes de migrar (evita duplicação)

## 🚀 Processo de Deploy

### 1. Configurar Banco de Dados no Render

1. Crie um banco PostgreSQL no Render
2. Anote a **Internal Database URL**
3. Adicione como variável de ambiente `DATABASE_URL` no seu Web Service

### 2. Deploy

Ao fazer o deploy, o sistema:
1. Detecta que `DATABASE_URL` está configurado
2. Cria as tabelas no banco (se não existirem)
3. Migra automaticamente todos os dados dos arquivos JSON
4. Cria backups dos arquivos originais
5. Inicializa dados padrão (se o banco estiver vazio)

### 3. Verificação

Após o deploy:
- ✅ Acesse o site e verifique se os dados aparecem corretamente
- ✅ Faça login no painel admin (`/admin/login`)
- ✅ Verifique se todos os usuários foram migrados
- ✅ Confirme que as configurações estão preservadas

## 📁 Estrutura de Backups

Os backups são salvos em:
```
data/backups/
├── site_data.json.backup_20250101_120000
└── users.json.backup_20250101_120000
```

## ⚠️ Importante

- **Não delete os arquivos JSON** até confirmar que a migração foi bem-sucedida
- Os backups são criados automaticamente, mas mantenha cópias de segurança
- Se houver problemas, você pode restaurar dos backups
- O sistema continua funcionando com JSON se `DATABASE_URL` não estiver configurado

## 🔧 Migração Manual (Opcional)

Se precisar migrar manualmente, você pode executar:

```python
from app import app
from migrate_data import migrate_json_to_database

with app.app_context():
    migrate_json_to_database(app)
```

## ✅ Checklist de Migração

- [ ] Banco de dados criado no Render
- [ ] `DATABASE_URL` configurado no Web Service
- [ ] Deploy realizado
- [ ] Dados migrados automaticamente
- [ ] Backups criados em `data/backups/`
- [ ] Site funcionando corretamente
- [ ] Login no admin funcionando
- [ ] Todos os dados preservados
- [ ] Configurações mantidas

## 🐛 Troubleshooting

### Dados não aparecem após migração
- Verifique os logs do Render
- Confirme que `DATABASE_URL` está correto
- Verifique se as tabelas foram criadas

### Erro de conexão
- Confirme que está usando a **Internal Database URL** (não External)
- Verifique se o banco está ativo no Render

### Usuários não conseguem fazer login
- As senhas foram convertidas para hash
- Use as mesmas senhas que estavam nos arquivos JSON
- Se necessário, redefina a senha pelo painel admin

