# Especificação de Projeto: Agente de Investimentos IA (Baseado em Planilha)

Olá, assistente de código. Por favor, leia este documento para gerar os arquivos do projeto. Este sistema é um Agente de Investimentos autônomo criado com LangChain e FastAPI. Ele toma decisões de aporte baseadas na leitura direta de abas públicas do Google Sheets (sem autenticação complexa, via exportação CSV), aplicando regras estritas de dividendos e rebalanceamento.

## 1. Estrutura do Projeto (Backend Python)

O sistema rodará localmente. Precisaremos dos seguintes arquivos:
* `.env`
* `requirements.txt`
* `tools.py`
* `agent.py`
* `main.py`

## 2. Variáveis de Ambiente (`.env`)

Crie o arquivo `.env` na raiz do projeto contendo as chaves de API e o ID da planilha compartilhada.

```env
OPENAI_API_KEY=sua_chave_aqui
# O ID da planilha é a sequência de caracteres na URL do Google Sheets entre /d/ e /edit
GOOGLE_SHEET_ID=seu_id_da_planilha_aqui
```

## 3. Dependências (`requirements.txt`)

```text
fastapi
uvicorn
langchain
langchain-openai
langchain-community
sqlalchemy
pydantic
pandas
python-dotenv
requests
```

## 4. Ferramentas do Agente (`tools.py`)

Esta ferramenta utilizará o `pandas` para ler as abas específicas ("Preço Teto" e "Holding") da planilha, transformando a URL de compartilhamento em um link de download de CSV.

```python
import os
import pandas as pd
from langchain.tools import tool
from dotenv import load_dotenv

load_dotenv()

@tool
def analisar_dados_para_aporte() -> str:
    """Busca a custódia atual do usuário e as margens de segurança das ações no Google Sheets."""
    try:
        sheet_id = os.getenv("GOOGLE_SHEET_ID")
        if not sheet_id:
            return "Erro: GOOGLE_SHEET_ID não encontrado no .env"

        # URLs formatadas para extração direta de CSV das abas específicas
        url_teto = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Preço%20Teto"
        url_holding = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Holding"

        # Leitura via Pandas
        df_mercado = pd.read_csv(url_teto)
        df_custodia = pd.read_csv(url_holding)
        
        # Limpeza básica e conversão para dicionário (JSON)
        dados = {
            "aba_holding_minha_custodia": df_custodia.fillna(0).to_dict(orient="records"),
            "aba_preco_teto_margens": df_mercado.fillna(0).to_dict(orient="records")
        }
        
        return str(dados)
    
    except Exception as e:
        return f"Erro ao ler a planilha: {str(e)}"
```

## 5. Lógica e Regras do Agente (`agent.py`)

Este arquivo inicializa o LangChain e define o "cérebro" do agente através do System Prompt, contendo as teses de investimento específicas do usuário.

```python
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from tools import analisar_dados_para_aporte

# Instância do LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
tools = [analisar_dados_para_aporte]

# Prompt Mestre de Investimentos
system_prompt = """Você é um consultor financeiro especialista focado na estratégia de Dividendos Inteligentes.
Ao receber o valor de aporte do usuário, você DEVE SEMPRE chamar a ferramenta analisar_dados_para_aporte() para cruzar os dados.

REGRAS DE ALOCAÇÃO (Ordem de prioridade):
1. REGRA ABTC11: Reserve capital para comprar pelo menos 1 cota de ABTC11 (ETF de Cripto). Se o mercado tiver "escorregado" (preço atrativo no dia), pode recomendar 2 ou 3 cotas para baixar o preço médio. Nunca zere essa posição.
2. DIVIDENDO PREDITIVO: Busque na aba "Preço Teto" empresas boas com margem de segurança positiva e previsão de pagamento de proventos nos próximos 1 a 2 meses. Priorize comprar antes da confirmação do anúncio para evitar a alta do papel.
3. BALANCEAMENTO DA CARTEIRA: Consulte a aba "Holding". Evite aportar em ativos que já possuem uma concentração muito alta (como BBSE3, BBAS3, CXSE3), a menos que o desconto seja irrecusável e haja dividendo iminente.
4. GATILHO DE CAIXA: Se após aplicar a Regra 1, você olhar a planilha e NENHUMA ação tiver margem de segurança atrativa, não force a compra. Recomende enviar a sobra para Renda Fixa (Selic/CDI) aguardando oportunidades.

FORMATO DE RESPOSTA:
Apresente a sua resposta contendo:
- Resumo do dinheiro disponível.
- Radar (tabela com os ativos analisados, preços, margem, proventos e Situação: Comprar/Acompanhar).
- Aporte Sugerido (Quantidade exata de cotas e valor calculado).
- Justificativa das escolhas e o que não comprar agora.
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

def obter_historico_sessao(session_id: str):
    return SQLChatMessageHistory(session_id, "sqlite:///memoria_investimentos.db")

agente_com_memoria = RunnableWithMessageHistory(
    agent_executor,
    obter_historico_sessao,
    input_messages_key="input",
    history_messages_key="chat_history"
)
```

## 6. Servidor da API (`main.py`)

Configuração básica do FastAPI para expor o agente.

```python
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from agent import agente_com_memoria
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="API do Agente de Investimentos")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Configure para a porta do seu Frontend depois (ex: localhost:3000)
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    mensagem: str
    session_id: str = "carteira_principal"

async def gerador_resposta(mensagem: str, session_id: str):
    async for evento in agente_com_memoria.astream_events(
        {"input": mensagem},
        config={"configurable": {"session_id": session_id}},
        version="v2"
    ):
        if evento["event"] == "on_chat_model_stream":
            chunk = evento["data"]["chunk"].content
            if chunk:
                yield f"data: {chunk}\n\n"

@app.post("/api/agente")
async def chat_com_agente(req: ChatRequest):
    return StreamingResponse(
        gerador_resposta(req.mensagem, req.session_id),
        media_type="text/event-stream"
    )

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
```