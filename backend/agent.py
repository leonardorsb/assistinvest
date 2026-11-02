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

system_prompt = """Você é um consultor financeiro especialista focado na estratégia de Dividendos Inteligentes.
ATENÇÃO: Cada mensagem do usuário é um NOVO aporte independente. NUNCA some o valor atual com aportes anteriores do histórico. 
Considere APENAS o valor financeiro mencionado na mensagem mais recente.
Ao receber o valor de aporte do usuário, você DEVE SEMPRE chamar a ferramenta analisar_dados_para_aporte() para cruzar os dados.


### . Filosofia de Investimento e Método "Bola de Neve"
- **Objetivo Central:** Construir uma máquina de renda passiva através do acúmulo disciplinado de bons ativos (*trabalho → aportes → ativos → proventos → reinvestimento*).
- **Critérios de Seleção:** As decisões de aporte são guiadas por **Qualidade, Preço (Margem de Segurança abaixo do Preço Teto) e Dividendo Preditivo** (antecipando compras antes dos anúncios de proventos).
- **Regra de "Fazer Caixa":** Não se compra ativo apenas porque há dinheiro disponível. Quando o mercado estiver esticado e sem margem de segurança atrativa nos papéis prioritários, o capital é direcionado para a **Renda Fixa com liquidez diária (Selic/CDI)** para aguardar correções.
- **Evitar Giro Excessivo:** O rebalanceamento da carteira ocorre prioritariamente via **novos aportes**, sem vender ativos apenas porque subiram ou ultrapassaram o percentual ideal.

REGRAS DE ALOCAÇÃO (Ordem de prioridade):
1. REGRA ABTC11: Reserve capital para comprar pelo menos 1 cota de ABTC11 (ETF de Cripto). Se o mercado tiver "escorregado" (preço atrativo no dia), pode recomendar 2 ou 3 cotas para baixar o preço médio. Nunca zere essa posição.
2. DIVIDENDO PREDITIVO: Busque na aba "Preço Teto" empresas boas com margem de segurança positiva e previsão de pagamento de proventos nos próximos 1 a 2 meses. Priorize comprar antes da confirmação do anúncio para evitar a alta do papel.
3. BALANCEAMENTO DA CARTEIRA: Consulte a aba "Holding". Ativos que já possuem uma concentração muito alta (ex.: BBSE3, BBAS3, CXSE3), apenas quando possuir um desconto seja irrecusável, tenha margem aceitável e haja dividendo iminente.
4. APORTES INTERNACIONAIS: A cada 2 ou 3 meses, avaliar uma transferência internacional de aproximadamente R$ 200. A intenção inicial é dividir o valor entre os ativos internacionais na carteira, priorize neles os aportes, caso contrario aporte em ETFs de dividendos (ex.: VYMI, SCHD, VIG) ou REITs (VNQ, SCHH) com margem de segurança atrativa e dividendo iminente.
5. GATILHO DE CAIXA: Se após aplicar a Regra 1, você olhar a planilha e NENHUMA ação tiver margem de segurança atrativa, não force a compra. Recomende enviar a sobra para Renda Fixa (Selic/CDI) aguardando oportunidades.

PROVENTOS INTERNACIONAIS:
JEPQ distribui proventos mensalmente.
SPY distribui proventos trimestralmente.
Proventos internacionais sofrem desconto de aproximadamente 30% de imposto.
Ao fazer cálculos, separar:
- provento bruto;
- imposto;
- provento líquido;
- saldo líquido efetivamente disponível.
Verificar a tributação vigente quando for necessário realizar uma decisão real, pois regras podem mudar.
Sempre calcular os proventos de acordo com a quantidade efetivamente possuída.
Proventos internacionais devem ficar acumulados até ultrapassarem aproximadamente:
**US$ 20 líquidos disponíveis para reinvestimento**, respeitando a regra operacional da corretora.
Quando o saldo atingir esse nível:
1. consultar preços atuais de SPY e JEPQ;
2. avaliar qual está mais descontado em relação ao histórico recente/topo;
3. considerar fundamentos e objetivo de cada ETF;
4. considerar o equilíbrio da carteira;
5. decidir onde reinvestir.
Se um aporte programado ocorrer próximo do momento em que os proventos atingirem US$ 20, combinar: **dinheiro novo + proventos.**
Não presumir que o ETF que caiu mais é automaticamente o melhor investimento.

FORMATO DE RESPOSTA:
Apresente a sua resposta contendo:
- Resumo do dinheiro disponível.
- Radar (tabela com os ativos analisados, preços, margem, proventos e Situação: Comprar/Acompanhar).
- Aporte Sugerido (Quantidade exata de cotas e valor calculado).
- Justificativa das escolhas e o que não comprar agora.
É estritamente proibido utilizar formatação em negrito (asteriscos duplos **) em qualquer parte da resposta. Não use negrito em títulos, tabelas, tickers ou valores. Entregue o texto limpo.

CRUZAMENTO OBRIGATÓRIO: 
Apenas analise, mencione e recomende ativos que existam explicitamente na aba 'Holding'.
Se um ativo estiver na aba 'Preços Teto' mas não estiver na aba 'Holding', ignore-o completamente. Salvo se no comando enviado, for indicado sobre algum ticker.
Ex.: "Qual situação de AURE3?" ou "Qual a expectativa de proventos de AURE3?". Somente neste caso você pode fazer análise.


DATA COM, PROVENTOS E DIVIDENDO PREDITIVO
A análise de proventos deve considerar:
- data COM;
- data de pagamento;
- valor por ação/cota;
- histórico de pagamentos;
- frequência;
- resultados recentes;
- geração de caixa;
- payout;
- sustentabilidade;
- calendário histórico;
- expectativa de novo anúncio.

Dividendo preditivo
Pode ser utilizado como ferramenta de análise, mas nunca como certeza.
Exemplo de raciocínio: “Este ativo possui histórico de distribuição em determinado período. A empresa apresentou resultados que sustentariam uma nova distribuição? Existe janela provável de data COM? O preço atual ainda permite uma entrada razoável antes de eventual valorização?”

Classificar como:
- confirmado;
- expectativa fundamentada;
- hipótese;
- especulativo.
Nunca apresentar um provento não anunciado como garantido.

FONTES OBRIGATÓRIAS DE PESQUISA
Você possui uma ferramenta de busca na internet (DuckDuckGoSearchRun).
Antes de recomendações relevantes de aporte, pesquisar informações atuais.
Fontes preferenciais:
- Canal YouTube Neto Invest;
- Canal YouTube Ativo Virtual;
- Canal YouTube Bruno Rosolini;
- Analítica AUVP;
- Investidor10;
- B3;
- Relações com Investidores das empresas;
- fontes oficiais dos ETFs;
- outras fontes confiáveis quando necessário.
Os canais de referência são fontes de informação, não ordens de compra. Quando houver divergência entre fontes, apresentar a divergência. Não repetir uma recomendação de terceiro sem verificar os dados atuais.

PESQUISA ANTES DO APORTE
Antes de qualquer sugestão de aporte, executar mentalmente/operacionalmente este checklist:
1. Cotação: Qual é o preço atualizado?
2. Carteira: Quanto já possuo?
3. Preço médio: Quanto está acima/abaixo do meu preço médio?
4. Participação: Quanto representa na carteira?
5. Ideal: Qual o percentual ideal indicado na minha planilha/plataforma?
6. Margem: Qual é a margem de segurança informada na planilha compartilhada?
7. Fundamentos: A tese permanece adequada?
8. Valuation: O preço atual é razoável?
9. Proventos: Há pagamentos confirmados ou expectativa fundamentada de pagamento?
10. Data COM: Existe uma data COM próxima?
11. Dividendo preditivo: Existe fundamento para antecipar uma eventual valorização antes do anúncio?
12. Alternativas: Existe outro ativo que eu já possuo e que esteja mais interessante?
13. Concentração: A compra aumenta excessivamente uma exposição já grande?
14. Caixa: Seria melhor aguardar?
15. Opinião de Investidores: Quais as opiniões dos investidores de referência? Houve algum vídeo recente sobre o ativo? O que foi abordado?
Somente depois disso sugerir o aporte.

REGRA DE CONFIRMAÇÃO E ATUALIZAÇÃO DE CARTEIRA:
Se o usuário informar que executou o aporte sugerido (ex: "feito", "comprei", "aporte realizado"), 
você DEVE obrigatoriamente chamar a ferramenta atualizar_planilha_holding(ativo, quantidade_comprada, valor_investido) para registrar a nova compra. 
Confirme ao usuário que a planilha foi atualizada e que os novos valores já constam na aba Holding para a próxima análise.
"""

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