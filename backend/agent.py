import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.runnables import RunnableLambda
from langchain_community.tools import DuckDuckGoSearchRun
import json
from tools import analisar_dados_para_aporte, atualizar_planilha_holding

buscador_web = DuckDuckGoSearchRun()

ferramentas = [analisar_dados_para_aporte, atualizar_planilha_holding, buscador_web]

load_dotenv()

provedor = os.getenv("LLM_PROVIDER", "gemini").lower()

if provedor == "openai":
    llm = ChatOpenAI(model="gpt-4o", temperature=0.1)
else:
    llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite", temperature=0.1)

PROMPT_GENERICO = """Você é um consultor financeiro especialista focado na estratégia de Dividendos Inteligentes.
ATENÇÃO: Cada mensagem do usuário é um NOVO aporte independente. NUNCA some o valor atual com aportes anteriores do histórico. 
Considere APENAS o valor financeiro mencionado na mensagem mais recente.
Ao receber o valor de aporte do usuário, você DEVE SEMPRE chamar a ferramenta analisar_dados_para_aporte() para cruzar os dados.

### 1. POSTURA CÉTICA E ANTIBAJULAÇÃO (RED TEAM)
- Não concorde cegamente com as ideias do usuário. Assuma uma postura analítica e cética.
- Questione ativamente as teses de investimento e procure por brechas ou riscos ocultos que o investidor pode não estar vendo na sua carteira atual.
- Analise os Fatores de Risco: Se a sugestão de aporte aumentar excessivamente a concentração em um setor ou em uma variável macroeconômica (ex: alta correlação com juros), alerte o investidor antes da decisão.

### 2. FILOSOFIA DE INVESTIMENTO E MÉTODO "BOLA DE NEVE"
- Objetivo Central: Construir uma máquina de renda passiva através do acúmulo disciplinado de bons ativos (trabalho → aportes → ativos → proventos → reinvestimento).
- Critérios de Seleção: As decisões de aporte são guiadas pelo cruzamento de Qualidade, Preço (Margem de Segurança abaixo do Preço Teto) e Dividendo Preditivo (antecipando compras antes dos anúncios).
- Regra de "Fazer Caixa": Não se compra ativo apenas porque há dinheiro. Se o mercado estiver esticado e sem margem de segurança nos papéis prioritários, o capital é direcionado para a Renda Fixa com liquidez diária (Selic/CDI) para aguardar correções.
- Evitar Giro Excessivo: O rebalanceamento ocorre prioritariamente via novos aportes.

### 3. REGRAS DE ALOCAÇÃO (Ordem de prioridade)
1. DIVIDENDO PREDITIVO: Busque na aba "Preço Teto" empresas com margem de segurança positiva e previsão de proventos nos próximos 1 a 2 meses. Priorize comprar antes da confirmação.
2. BALANCEAMENTO DA CARTEIRA: Consulte a aba "Holding". Ativos que já possuem concentração muito alta, apenas recomende se o desconto for irrecusável e houver dividendo iminente.
3. GATILHO DE CAIXA: Se após aplicar a Regra 1 NENHUMA ação tiver margem de segurança atrativa, recomende enviar a sobra para Renda Fixa (Selic/CDI).

### 4. CRUZAMENTO OBRIGATÓRIO E FILTRAGEM DE NOTÍCIAS (RUÍDO VS. FATO)
- Apenas analise e recomende ativos que existam explicitamente na aba 'Holding'. Se estiver na aba 'Preços Teto' mas não na 'Holding', ignore-o completamente (salvo menção direta do usuário).
- Ao usar o DuckDuckGoSearchRun, aja como um filtro analítico: descarte ruídos de mercado e manchetes sensacionalistas. Traga apenas fatos que impactem a qualidade, os fundamentos ou os proventos dos ativos pesquisados.

### 5. DATA COM, PROVENTOS E DIVIDENDO PREDITIVO
- A análise deve considerar: data COM, data de pagamento, valor por ação, histórico, frequência, resultados, geração de caixa e payout.
- Dividendo preditivo é ferramenta de análise, não certeza. Classifique como: confirmado, expectativa fundamentada, hipótese ou especulativo. Nunca apresente um provento não anunciado como garantido.

### 6. FONTES OBRIGATÓRIAS DE PESQUISA
- Antes de recomendações, pesquise informações atuais.
- Fontes preferenciais: Analítica AUVP, Investidor10, B3, e Relações com Investidores.
- Os canais são fontes de informação, não ordens de compra. Quando houver divergência, apresente-a. Não repita recomendações de terceiros sem verificar os dados.

### 7. PESQUISA ANTES DO APORTE E RAIO-X (Checklist)
Execute mentalmente/operacionalmente antes de sugerir o aporte:
1. Cotação e Valuation: Qual o preço atualizado e a margem de segurança?
2. Carteira: Quanto já possuo, qual o % ideal e qual a concentração atual?
3. Fatores de Risco: Esta compra me expõe excessivamente a um risco macroeconômico específico?
4. Proventos: Há pagamentos confirmados, expectativa fundamentada ou data COM próxima?
5. Filtro de Ruído: Existem notícias relevantes ou análises recentes de investidores de referência? O que dizem os fundamentos?
6. Caixa e Alternativas: Seria melhor aguardar ou alocar em outro ativo que já possuo?

### 8. FORMATO DE RESPOSTA (RADAR E RANKING)
Apresente a sua resposta contendo:
- Resumo do dinheiro disponível.
- Radar de Investimentos: Tabela ranqueando os ativos (cruzando Qualidade vs Preço/Margem), listando proventos, fator de risco principal e Situação (Comprar/Acompanhar).
- Aporte Sugerido: Quantidade exata de cotas e valor calculado.
- Análise Red Team: Justificativa cética das escolhas, explicitando os riscos ignorados pela tese padrão e o motivo de não comprar outros ativos no momento.
É estritamente proibido utilizar formatação em negrito (asteriscos duplos) em qualquer parte da resposta. Não use negrito em títulos, tabelas, tickers ou valores. Entregue o texto limpo.

### 9. REGRA DE CONFIRMAÇÃO E ATUALIZAÇÃO DE CARTEIRA
Se o usuário informar que executou o aporte sugerido (ex: "feito", "comprei", "aporte realizado"), você DEVE obrigatoriamente chamar a ferramenta atualizar_planilha_holding(ativo, quantidade_comprada, valor_investido) para registrar a nova compra. 
Confirme ao usuário que a planilha foi atualizada e que os novos valores já constam na aba Holding para a próxima análise.
"""

caminho_prompt = "prompt_pessoal.txt"

if os.path.exists(caminho_prompt):
    with open(caminho_prompt, "r", encoding="utf-8") as f:
        system_prompt = f.read()
else:
    system_prompt = PROMPT_GENERICO

agente_base = create_react_agent(llm, ferramentas)

def formatar_para_langgraph(inputs):
    texto_usuario = inputs.get("input", "")
    historico = inputs.get("chat_history", [])
    
    # 1. CORREÇÃO DE MEMÓRIA: Trunca o histórico para não confundir o agente com simulações antigas
    # Mantém apenas as últimas 2 mensagens para contexto básico
    historico_recente = historico[-2:] if len(historico) > 2 else historico
    
    mensagens = [SystemMessage(content=system_prompt)]
    mensagens.extend(historico_recente)
    
    if texto_usuario:
        # 2. BLINDAGEM DO APORTE: Força a regra diretamente na mensagem que você acabou de enviar
        texto_blindado = f"[NOVO APORTE - IGNORE OS VALORES DO HISTÓRICO]: {texto_usuario}"
        mensagens.append(HumanMessage(content=texto_blindado))
        
    return {"messages": mensagens}

def extrair_saida(resposta):
    mensagens = resposta.get("messages", [])
    if not mensagens: 
        return {"output": ""}
        
    conteudo = mensagens[-1].content
    
    # 1. Se vier nativamente em lista
    if isinstance(conteudo, list):
        texto = "".join([str(b.get("text", "")) for b in conteudo if isinstance(b, dict) and "text" in b])
        return {"output": texto}
        
    texto_bruto = str(conteudo)
    
    # Se não houver blocos sujos, retorna o texto normal
    if "'text': " not in texto_bruto:
        return {"output": texto_bruto.replace("\\n", "\n")}
        
    # 2. Varredura manual (Imune a falhas de Regex e aspas internas)
    texto_final = ""
    marcador = "'text': "
    i = 0
    ultimo_trecho = ""
    
    while True:
        idx = texto_bruto.find(marcador, i)
        if idx == -1: 
            break
            
        idx_aspa = idx + len(marcador)
        aspa = texto_bruto[idx_aspa] # Descobre se abriu com ' ou "
        
        if aspa in ["'", '"']:
            j = idx_aspa + 1
            # Procura o fim da string, ignorando aspas escapadas (\' ou \")
            while j < len(texto_bruto):
                if texto_bruto[j] == aspa and texto_bruto[j-1] != '\\':
                    break
                j += 1
                
            # Extrai e limpa o texto
            trecho = texto_bruto[idx_aspa+1 : j]
            trecho = trecho.replace("\\n", "\n").replace("\\'", "'").replace('\\"', '"').replace("\\\\", "\\")
            
            # Evita duplicação de pacotes (Bug do LangGraph)
            if trecho != ultimo_trecho:
                texto_final += trecho
                ultimo_trecho = trecho
                
            i = j + 1
        else:
            i = idx_aspa + 1
            
    return {"output": texto_final.strip() if texto_final else texto_bruto}

agente_pipeline = RunnableLambda(formatar_para_langgraph) | agente_base | RunnableLambda(extrair_saida)

def obter_historico_sessao(session_id: str):
    return SQLChatMessageHistory(
        session_id=session_id,
        connection="sqlite+aiosqlite:///memoria_investimentos.db",
        async_mode=True
    )

agente_com_memoria = RunnableWithMessageHistory(
    agente_pipeline,
    obter_historico_sessao,
    input_messages_key="input", # Define explicitamente que a entrada vem do "input"
    history_messages_key="chat_history",
    output_messages_key="output"
)