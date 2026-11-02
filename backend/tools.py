import pandas as pd
import urllib.parse
import requests
from langchain_core.tools import tool

@tool
def analisar_dados_para_aporte() -> str:
    """
    Lê as planilhas de 'Preço Teto' e 'Holding' e retorna os dados financeiros cruciais.
    """
    sheet_id = "1KEIbUV07nefgk8-LzRyfjPcE1-Pm6rijs0yH4jlkBno"
    
    # Codificação de URL blindada para caracteres especiais ("Preço Teto" vira "Pre%C3%A7o+Teto")
    aba_teto = urllib.parse.quote("Preço Teto")
    
    url_teto = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={aba_teto}"
    url_holding = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Holding"
    
    try:
        df_teto = pd.read_csv(url_teto)
        df_holding = pd.read_csv(url_holding)
        
        # Markdown é o formato mais limpo para LLMs lerem tabelas
        resumo_teto = df_teto.to_csv(index=False)
        resumo_holding = df_holding.to_csv(index=False)
        
        return f"DADOS PREÇO TETO:\n{resumo_teto}\n\nDADOS HOLDING:\n{resumo_holding}"
        
    except Exception as e:
        return f"Erro crítico na leitura da planilha: {str(e)}"
    
@tool
def atualizar_planilha_holding(ativo: str, quantidade: float) -> str:
    """
    Soma a nova quantidade de cotas/ações compradas a um ativo existente na aba Holding.
    DEVE ser chamada SEMPRE que o usuário confirmar que realizou um aporte sugerido.
    """
    # Substitua pelo URL da Aplicação Web gerado no Apps Script
    webhook_url = "https://script.google.com/macros/s/AKfycbzUkK_d4dFusp5CasTFEIYGBZoFIRJLd42goPAUrzpJ0TgjNkWYSuWQgSna0MYVRsmTqg/exec"
    
    payload = {
        "ativo": ativo,
        "quantidade": quantidade
    }
    
    try:
        resposta = requests.post(webhook_url, json=payload)
        if "Sucesso" in resposta.text:
            return f"Planilha atualizada! Foram adicionadas {quantidade} cotas de {ativo} à carteira."
        else:
            return f"Falha ao atualizar a planilha: {resposta.text}"
    except Exception as e:
        return f"Erro de conexão ao tentar atualizar a planilha: {str(e)}"