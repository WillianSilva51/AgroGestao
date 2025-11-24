# AgroGestao

Para instalar e executar o AgroGestao, siga os passos abaixo:

## Requisitos
- Python 3.8 ou superior
- pip (gerenciador de pacotes do Python)
- Virtualenv (opcional, mas recomendado)
- Banco de dados PostgreSQL (versão 12 ou superior)
- Git
- Docker e Docker Compose (opcional, para ambiente de desenvolvimento)

## Passos para Instalação
1. **Clone o repositório do AgroGestao:**
   ```bash
   git clone https://github.com/WillianSilva51/AgroGestao.git
   cd AgroGestao
    ```

2. **Crie um ambiente virtual (opcional, mas recomendado):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # No Windows use `venv\Scripts\activate
    ```
3. **Instale as dependências do projeto:**
    ```bash
    pip install -r requirements.txt
    ```