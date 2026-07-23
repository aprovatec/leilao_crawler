import re
import os
import datetime
import pandas as pd

def extrair_dados_publicacao(texto_publicacao, comarca="Campinas"):
    """
    Analisa o texto de uma publicação do DJE para identificar gatilhos de leilão,
    extrair o número do processo, o advogado/OAB e o valor de avaliação do bem.
    """
    # 1. Termos de gatilho de Prospecção Antecipada (Linha de Tiro)
    gatilhos = [
        "homologo o laudo de avaliação",
        "manifeste-se o exequente sobre a designação de leilão",
        "indique o exequente leiloeiro",
        "manifeste-se o exequente sobre a estimativa de valor"
    ]
    
    texto_lower = texto_publicacao.lower()
    gatilho_encontrado = None
    for g in gatilhos:
        if g in texto_lower:
            gatilho_encontrado = g
            break
            
    if not gatilho_encontrado:
        return None # Ignora se não for um processo prestes a ir a leilão
        
    # 2. Captura do Número do Processo (Padrão CNJ do TJ-SP: XXXXXXX-XX.XXXX.8.26.XXXX)
    padrao_processo = r'\b\d{7}-\d{2}\.\d{4}\.8\.26\.\d{4}\b'
    processo_match = re.search(padrao_processo, texto_publicacao)
    processo = processo_match.group(0) if processo_match else "Não identificado"
    
    # 3. Captura Inteligente do Valor do Bem (R$ 1.234.567,89)
    # Procura pela cifra R$ seguida de números pontuados
    padrao_valor = r'R\$\s?([0-9]{1,3}(?:\.[0-9]{3})*,\d{2})'
    valores_encontrados = re.findall(padrao_valor, texto_publicacao)
    
    valor_bem = "Não especificado"
    if valores_encontrados:
        # Pegamos o primeiro valor monetário relevante que aparece na sentença de avaliação
        valor_bem = f"R$ {valores_encontrados[0]}"

    # 4. Captura do Advogado e sua OAB (Filtro para OAB/SP)
    padrao_oab = r'(?:OAB/SP\s?\d{3}\.?\d{3}|\b\d{3}\.\d{3}/SP\b|\b\d{5,6}/SP\b)'
    oab_match = re.search(padrao_oab, texto_publicacao)
    oab = oab_match.group(0) if oab_match else "Não identificada"
    
    # Tenta resgatar o nome do Advogado que vem logo antes da palavra OAB
    advogado = "Verificar no Processo"
    if oab_match:
        posicao_oab = texto_publicacao.find(oab)
        # Analisa os 60 caracteres anteriores à OAB para achar o nome do Dr./Dra.
        trecho_anterior = texto_publicacao[max(0, posicao_oab-60):posicao_oab]
        match_nome = re.search(r'(?:ADV:|ADVOGADO:)?\s*([A-ZÃÉÍÓÚÂÊÔ\s]{10,40})', trecho_anterior)
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
        df_existente = pd.read_csv(caminho_csv)
        # Evita duplicar o mesmo número de processo na planilha de leads
        if novo_lead["Processo"] not in df_existente["Processo"].values:
            df_final = pd.concat([df_existente, df_novo], ignore_index=True)
            df_final.to_csv(caminho_csv, index=False)
    else:
        df_novo.to_csv(caminho_csv, index=False)