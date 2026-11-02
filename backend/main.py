import os
import asyncio
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from agent import agente_com_memoria

load_dotenv()

app = FastAPI(title="API do Agente de Investimentos")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    mensagem: str
    session_id: str = "carteira_principal"

async def gerador_resposta(mensagem: str, session_id: str):
    try:
        # 1. PREVINE O TIMEOUT SILENCIOSO: Envia uma mensagem imediata para manter a conexão aberta
        yield "data: ⏳ Analisando a sua carteira e estruturando a estratégia. Por favor, aguarde...\n\n"

        # 2. PROCESSAMENTO SEGURO: Aguarda a IA utilizar as planilhas sem o bug 'iterator_'
        resposta = await agente_com_memoria.ainvoke(
            {"input": mensagem},
            config={"configurable": {"session_id": session_id}}
        )
        
        texto_final = ""
        
        # 3. EXTRATOR UNIVERSAL
        if isinstance(resposta, dict):
            if "output" in resposta:
                texto_final = resposta["output"]
            elif "messages" in resposta:
                texto_final = resposta["messages"][-1].content
            else:
                for key, value in resposta.items():
                    if isinstance(value, dict) and "messages" in value:
                        texto_final = value["messages"][-1].content
                        break

        if isinstance(texto_final, list):
            texto_final = "".join([str(b.get("text", "")) for b in texto_final if isinstance(b, dict) and "text" in b])
        else:
            texto_final = str(texto_final)

        if not texto_final:
            yield "data: \n\ndata: *[Erro: Nenhuma resposta gerada]*\n\n"
            return

        # Separador visual entre o aviso e o resultado
        yield "data: \n\ndata: ---\n\n"

        # 4. STREAMING SSE SEGURO: Envia linha a linha. 
        # Isto garante que as tabelas Markdown fiquem perfeitas e elimina a gagueira do React.
        linhas = texto_final.split('\n')
        for linha in linhas:
            yield f"data: {linha}\n\n"
            await asyncio.sleep(0.05) # Efeito fluido de leitura

    except Exception as e:
        yield f"data: \n\ndata: *[Falha na execução: {str(e)}]*\n\n"

# Trecho relevante do main.py
@app.post("/api/agente")
async def chat_com_agente(req: ChatRequest):
    resposta = await agente_com_memoria.ainvoke(
        {"input": req.mensagem},
        config={"configurable": {"session_id": req.session_id}}
    )
    
    texto = ""
    if isinstance(resposta, dict):
        if "output" in resposta:
            texto = resposta["output"]
        elif "messages" in resposta:
            texto = resposta["messages"][-1].content
            
    if isinstance(texto, list):
        texto = "".join([str(b.get("text", "")) for b in texto if isinstance(b, dict) and "text" in b])
        
    return {"resposta": str(texto)}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)