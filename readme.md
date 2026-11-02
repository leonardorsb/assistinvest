# 📈 Agente de Investimentos AI

Um assistente virtual inteligente desenvolvido com **FastAPI** (Python) e **Next.js** (React) que analisa a sua carteira de investimentos e sugere os melhores aportes do dia. O agente utiliza Inteligência Artificial para cruzar o capital disponível com uma planilha de "Preço Teto", focando em margem de segurança e rebalanceamento inteligente.

⚠️ **Aviso Legal:** Este projeto é uma ferramenta de automação e estudo pessoal. As sugestões geradas pela IA não constituem recomendação oficial de compra ou venda de ativos financeiros.

## ✨ Funcionalidades
- **Análise em Tempo Real:** Conecta-se à sua planilha do Google Sheets para ler cotações, preços teto e a sua carteira atual ("Holding").
  <img width="1120" height="910" alt="image" src="https://github.com/user-attachments/assets/60ed0030-70bb-450f-a628-c45381e54c0f" />
- **Estratégia Bola de Neve:** Filtra e sugere apenas ativos com margem de segurança atrativa.
- **Filtro de Segurança:** A IA está programada para analisar estritamente ativos que você já possui e acompanha, evitando "alucinações" com tickers desconhecidos.
  <img width="1120" height="910" alt="image" src="https://github.com/user-attachments/assets/0dc4d482-8c94-4485-b36e-1fc859b8da80" />

- **Memória de Contexto:** Lembra-se da conversa durante a sessão para facilitar o registro de aportes.

## 🛠️ Tecnologias Utilizadas
- **Backend:** Python, FastAPI, LangChain, SQLite (para memória).
- **Frontend:** Next.js, React, Tailwind CSS, Lucide Icons.
- **Integrações:** API do Google Sheets (Service Account) e IA [INSERIR QUAL LLM ESTÁ USANDO, EX: Google Gemini / OpenAI].

---

## 🚀 Como Executar o Projeto Localmente

### 1. Pré-requisitos
Certifique-se de ter instalado em sua máquina:
- [Python 3.9+](https://www.python.org/downloads/)
- [Node.js 18+](https://nodejs.org/)
- Uma conta no Google Cloud Console (para gerar as credenciais da planilha).

### 2. Configurando a Planilha Base
Para que o sistema funcione sem expor os meus dados pessoais, criei uma planilha modelo.
1. Acesse a planilha modelo: https://docs.google.com/spreadsheets/d/1sD-3m-DLNboGTHP8CScTnsUJfn13nrL9zWjjgzLOSy8/edit?usp=sharing
2. Vá em **Arquivo > Fazer uma cópia** e salve no seu Google Drive.
3. Obtenha o ID da sua nova planilha (o código alfanumérico longo na URL) para colocar no arquivo `.env`.
4. Compartilhe a sua planilha com o e-mail da sua *Service Account* do Google Cloud (como editor).

### 3. Configurando o Backend (Python)
Abra o terminal, navegue até a raiz do projeto e entre na pasta do backend:
```bash
cd backend
```

Crie um ambiente virtual e ative-o:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

Instale as dependências:
```bash
pip install -r requirements.txt
```

Crie um arquivo `.env` dentro da pasta `backend` seguindo o modelo abaixo e preencha com as suas chaves:
```env
# Exemplo de .env
GOOGLE_API_KEY=sua_chave_da_ia_aqui
SPREADSHEET_ID=id_da_sua_planilha_copiada_aqui
GOOGLE_APPLICATION_CREDENTIALS=credentials.json # Coloque o arquivo JSON do Google Cloud na pasta do backend
```

Inicie o servidor backend:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Configurando o Frontend (Next.js)
Abra um novo terminal e navegue para a pasta do frontend:
```bash
cd frontend
```

Instale as dependências do Node:
```bash
npm install
```

Inicie o servidor de desenvolvimento:
```bash
npm run dev
```

### 5. Utilizando o Agente
Abra o seu navegador e acesse `http://localhost:3000`. O chat estará pronto para uso. Basta digitar o valor do seu aporte diário (Ex: "Recebi R$ 500, como devo aportar hoje?") e aguardar a análise estruturada da IA.

---
*Desenvolvido por LEONARDO ROSA / https://github.com/leonardorsb*
