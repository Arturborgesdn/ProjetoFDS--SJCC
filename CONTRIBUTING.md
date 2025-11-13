## Guia de Contribuição

> Obrigado por se interessar em contribuir com este projeto! 
> Este guia vai ajudá-lo a configurar seu ambiente, entender o fluxo de trabalho e enviar suas contribuições de forma eficiente.

---

### Pré-requisitos

Antes de começar, certifique-se de ter as seguintes ferramentas instaladas:

* **[Git](https://git-scm.com/downloads)** – Controle de versão.
* **[Python 3.8+](https://www.python.org/downloads/)** – Linguagem usada no backend.
* **[MySQL](https://www.mysql.com/)** – Sistema de banco de dados.
* Um editor de código de sua preferência (**[VS Code](https://code.visualstudio.com/)**).

---

### Configuração do Ambiente

Siga os passos abaixo para rodar o projeto localmente:

#### 1️⃣ Clonar o Repositório

Primeiro, faça um **fork** do repositório principal e clone o seu fork:

```bash
git clone https://github.com/Arturborgesdn/ProjetoFDS--SJCC.git

# Acesse a pasta do projeto
cd ProjetoFDS--SJCC
```

---

#### 2️⃣ Configurar o Backend (Python/Flask)

Utilizamos um ambiente virtual para isolar as dependências do projeto.

```bash
# Criar o ambiente virtual
python -m venv venv
```

Ative o ambiente virtual:

```bash
# Windows (PowerShell/CMD)
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

Em seguida, instale as dependências:

```bash
pip install -r requirements.txt
```

---

#### 3️⃣ Configurar o Banco de Dados (MySQL)

1. Verifique se o serviço **MySQL** está ativo.
2. Crie um novo banco de dados para o projeto:

```sql
CREATE DATABASE nome_do_banco;
```

3. Crie um arquivo chamado `.env` na raiz do projeto e adicione suas variáveis de ambiente:

```ini
# Exemplo de configuração
DATABASE_URL="mysql+pymysql://USUARIO:SENHA@localhost/nome_do_banco"

# Outras configurações
FLASK_ENV="development"
FLASK_DEBUG=1
```

> Se existir um arquivo `.env.example`, use-o como referência.

---

#### 4️⃣ Rodar o Projeto

Se o projeto utilizar migrações (Flask-Migrate), aplique-as antes de rodar:

```bash
flask db upgrade
```

Agora, inicie o servidor:

```bash
flask run
```

O projeto estará disponível em:
**[http://127.0.0.1:5000](http://127.0.0.1:5000)** (ou na porta definida).

---

### Fluxo de Contribuição

1. **Crie uma branch:**

   Nunca trabalhe diretamente na branch `main`. Crie uma nova branch para sua funcionalidade ou correção:

   ```bash
   # Exemplo
   git checkout -b feature/nova-tela-login
   # ou
   git checkout -b fix/bug-no-cadastro
   ```

2. **Implemente suas alterações:**
   Faça as modificações necessárias e garanta que tudo funcione corretamente.

3. **Crie commits claros:**
   Use mensagens de commit descritivas (recomendamos o padrão [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/)):

   ```bash
   git add .
   git commit -m "feat: adiciona botão de login com Google"
   ```

4. **Envie sua branch para o GitHub:**

   ```bash
   git push origin nome-da-sua-branch
   ```

5. **Abra um Pull Request (PR):**
   Vá até o repositório original e abra um PR da sua branch para a `main`.
   Descreva suas mudanças, anexe prints (se aplicável) e vincule a *Issue* correspondente.

---

### Dicas Finais

* Mantenha seu fork atualizado com o repositório principal (`git pull upstream main`).
* Siga o estilo de código e convenções do projeto.
* Seja respeitoso nas discussões e revisões.
* Teste suas alterações antes de enviar o Pull Request.

---

### Agradecimento

Sua contribuição faz toda a diferença!
Obrigado por ajudar a melhorar este projeto!

