import re
import os
import datetime
import pandas as pd

def extrair_dados_publicacao(texto_publicacao, comarca="Campinas"):
    """
    Analisa o texto de uma publicação do DJE para identificar gatilhos de leilão,
    extrair o número do processo, o advogado/OAB e o valor de avaliação do bem.
    """
    # 1. Padrões Regex flexíveis para os Gatilhos Comerciais (Pega variações de escrita)
    padroes_gatilho = [
        r'homolog[oa](?:da|do|ção)?\s+o\s+laudo',         # homologo o laudo, homologado o laudo, homologação do laudo
        r'laudo\s+de\s+avaliação',                        # laudo de avaliação
        r'designa(?:ção|da)?\s+de\s+leilão',              # designação de leilão, designado leilão
        r'indique\s+o\s+exequente\s+leiloeiro',            # indique o exequente leiloeiro
        r'estimativa\s+de\s+valor'                        # estimativa de valor
    ]
    
    texto_lower = texto_publicacao.lower()
    gatilho_encontrado = None
    
    for padrao in padroes_gatilho:
        match_g = re.search(padrao, texto_lower)
        if match_g:
            gatilho_encontrado = match_g.group(0)
            break
            
    if not gatilho_encontrado:
        return None # Ignora se não for um processo prestes a ir a leilão
        
    # 2. Captura do Número do Processo (Padrão CNJ do TJ-SP)
    padrao_processo = r'\b\d{7}-\d{2}\.\d{4}\.8\.26\.\d{4}\b'
    processo_match = re.search(padrao_processo, texto_publicacao)
    processo = processo_match.group(0) if processo_match else "Não identificado"
    
    # 3. Captura Inteligente do Valor do Bem (R$ 1.234.567,89)
    padrao_valor = r'R\$\s?([0-9]{1,3}(?:\.[0-9]{3})*,\d{2})'
    valores_encontrados = re.findall(padrao_valor, texto_publicacao)
    
    valor_bem = "Não especificado"
    if valores_encontrados:
        valor_bem = f"R$ {valores_encontrados[0]}"

    # 4. Captura do Advogado e sua OAB (Filtro para OAB/SP)
    padrao_oab = r'(?:OAB/SP\s?\d{3}\.?\d{3}|\b\d{3}\.\d{3}/SP\b|\b\d{5,6}/SP\b)'
    oab_match = re.search(padrao_oab, texto_publicacao)
    oab = oab_match.group(0) if oab_match else "Não identificada"
    
    advogado = "Verificar no Processo"
    if oab_match:
        posicao_oab = texto_publicacao.find(oab)
        # Analisa os 80 caracteres anteriores à OAB
        trecho_anterior = texto_publicacao[max(0, posicao_oab-80):posicao_oab]
        # Remove quebras de linha para evitar falhas na regex do nome
        trecho_limpo = trecho_anterior.replace('\n', ' ')
        
        match_nome = re.search(r'(?:ADV:|ADVOGADO:)?\s*([A-ZÃÉÍÓÚÂÊÔ\s]{8,45})', trecho_limpo)
        if match_nome:
            advogado = match_nome.group(1).strip()

    return {
        "Data_Captura": datetime.date.today().strftime("%d/%m/%Y"),
        "Processo": processo,
        "Comarca": comarca,
        "Valor_do_Bem": valor_bem,
        "Gatilho_Identificado": gatilho_encontrado.upper(),
        "Advogado_Credor": advogado,
        "OAB": oab,
        "Status_Lead": "Novo / Pendente"
    }


def salvar_lead_na_planilha(novo_lead, caminho_csv="data/leads_leilao.csv"):
    """
    Registra o lead capturado em uma planilha consolidada sem sobrescrever os anteriores.
    """
    os.makedirs(os.path.dirname(caminho_csv), exist_ok=True)
    df_novo = pd.DataFrame([novo_lead])
    
    if os.path.exists(caminho_csv):
        try:
            df_existente = pd.read_csv(caminho_csv, encoding="utf-8-sig")
            # Evita duplicar o mesmo número de processo na planilha de leads
            if novo_lead["Processo"] not in df_existente["Processo"].values:
                df_final = pd.concat([df_existente, df_novo], ignore_index=True)
                df_final.to_csv(caminho_csv, index=False, encoding="utf-8-sig")
        except Exception:
            df_novo.to_csv(caminho_csv, index=False, encoding="utf-8-sig")
    else:
        df_novo.to_csv(caminho_csv, index=False, encoding="utf-8-sig")