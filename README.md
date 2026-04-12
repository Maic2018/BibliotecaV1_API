# Biblioteca MVP - Backend (API)

Este é o backend do sistema de biblioteca, desenvolvido utilizando Python e o framework Flask. Sua principal função é gerenciar o banco de dados (SQLite) e fornecer uma API para o frontend da aplicação.

## Tecnologias Utilizadas

- **Linguagem:** Python 3.x
- **Framework Web:** Flask
- **Banco de Dados:** SQLite
- **Documentação da API:** Flask-RESTX, Flasgger (Swagger)
- **Controle de Ambiente:** venv (ambiente virtual Python)
- **Gerenciamento de Dependências:** requirements.txt (pip)
- **Outras dependências:** Flask-SQLAlchemy, Werkzeug, etc.

## Como rodar a aplicação

Siga estes passos no seu terminal (Prompt de Comando, PowerShell ou Terminal Linux):

### 1. Abra a pasta do backend

```bash
cd backend
```

### 2. Crie e ative um ambiente virtual

Se ainda não existir o ambiente virtual (`venv`), crie-o:

```bash
python -m venv ../venv
```

Ative o ambiente virtual:
- **No Windows:**
  ```bash
  ..\venv\Scripts\Activate
  ```
- **No Mac/Linux:**
  ```bash
  source ../venv/bin/activate
  ```

*(Você saberá que funcionou se aparecer `(venv)` no início da linha do seu terminal).*

### 3. Instale as dependências

Instale as bibliotecas necessárias usando o pip:

```bash
pip install -r requirements.txt
```

### 4. Inicie o servidor

```bash
python app.py
```

Pronto! A API estará rodando em `http://localhost:5000`.

---

## Documentação da API (Swagger)

Com o servidor rodando, você pode visualizar e testar todos os endpoints acessando pelo navegador:
**[http://localhost:5000/apidocs]**

## Usuários Padrão

Ao rodar o projeto pela primeira vez, dois usuários são criados automaticamente no banco de dados para facilitar seus testes:

- **Administrador:**
  - Login: `admin`
  - Senha: `admin123`
- **Usuário Comum:**
  - Login: `user`
  - Senha: `user123`