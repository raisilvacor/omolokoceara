# CASS - Congá de Aruanda São Sebastião

Site institucional desenvolvido em Python (Flask) e HTML5 para o Congá de Aruanda São Sebastião.

## Características

- Design profissional e institucional
- Totalmente responsivo (mobile-first)
- HTML5 semântico
- CSS moderno com gradientes e animações suaves
- Navegação intuitiva
- Formulário de contato funcional

## Estrutura do Projeto

```
CASS/
├── app.py                 # Aplicação Flask principal
├── requirements.txt       # Dependências Python
├── templates/             # Templates HTML
│   ├── base.html         # Template base
│   ├── index.html        # Página inicial
│   ├── sobre.html        # Página sobre
│   ├── atividades.html   # Página de atividades
│   └── contato.html      # Página de contato
└── static/               # Arquivos estáticos
    ├── css/
    │   └── style.css     # Estilos principais
    ├── js/
    │   └── main.js       # JavaScript
    └── images/           # Imagens (adicione suas imagens aqui)
```

## Instalação

1. Certifique-se de ter Python 3.7+ instalado

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Execução

Para executar o servidor de desenvolvimento:

```bash
python app.py
```

O site estará disponível em: `http://localhost:5000`

## Páginas Disponíveis

- `/` - Página inicial
- `/sobre` - Sobre o CASS
- `/atividades` - Atividades e programas
- `/contato` - Formulário de contato

## Personalização

### Cores

As cores principais podem ser alteradas no arquivo `static/css/style.css` através das variáveis CSS:

- `--primary-color`: Cor principal (preto)
- `--secondary-color`: Cor secundária (marrom)
- `--accent-color`: Cor de destaque (dourado)

### Conteúdo

Edite os arquivos em `templates/` para modificar o conteúdo das páginas.

### Imagens

Adicione suas imagens na pasta `static/images/` e referencie-as nos templates HTML.

## Tecnologias Utilizadas

- Python 3
- Flask (framework web)
- HTML5
- CSS3 (com variáveis CSS e Grid/Flexbox)
- JavaScript (vanilla)

## Licença

Este projeto foi desenvolvido para o CASS - Congá de Aruanda São Sebastião.

