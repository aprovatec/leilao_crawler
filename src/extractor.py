import os
import re
import pdfplumber

# RegEx exata para o padrão CNJ: NNNNNNN-DD.AAAA.J.TR.OOOO
CNJ_REGEX = r'\b\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}\b'

# Termos de interesse para Leilões
KEYWORDS = [
    "leilão", "leilao", 
    "arrematante", "arrematação", "arrematacao",
    "hasta pública", "hasta publica", 
    "praça pública", "praca publica",
    "edital de praça", "edital de praca"
]

# Filtros obrigatórios de Localidade/Região
FILTROS_LOCAL = [
    "indaiatuba", 
    "trt15", 
    "trt-15", 
    "campinas"
]

def analisar_pdf(caminho_pdf):
    """
    Abre o PDF, verifica se contém termos de leilão E se pertence à região de interesse.
    """
    achados = []
    nome_arquivo = os.path.basename(caminho_pdf) if 'os' in globals() else caminho_pdf
    
    with pdfplumber.open(caminho_pdf) as pdf:
        for num_pagina, pagina in enumerate(pdf.pages, start=1):
            texto = pagina.extract_text()
            if not texto:
                continue
                
            texto_minusculo = texto.lower()
            
            # 1. Verifica se tem alguma palavra sobre LEILÃO
            tem_leilao = any(kw in texto_minusculo for kw in KEYWORDS)
            
            # 2. Verifica se a página cita INDAIATUBA, CAMPINAS ou TRT-15
            e_da_regiao = any(local in texto_minusculo for local in FILTROS_LOCAL)
            
            # O processo só nos interessa se atender aos DOIS critérios na mesma página
            if tem_leilao and e_da_regiao:
                print(f"[!] Alerta: Oportunidade na região encontrada na página {num_pagina}!")
                processos_encontrados = re.findall(CNJ_REGEX, texto)
                
                # Tenta capturar a Vara ou Origem (Ex: 1ª Vara do Trabalho, 2ª Vara Cível)
                vara_match = re.search(r'(\d+ª?\s*Vara\s+(?:cível|criminal|do\s+trabalho|federal)?)\b', texto, re.IGNORECASE)
                vara = vara_match.group(1) if vara_match else "Vara Regional"
                
                for processo in set(processos_encontrados):
                    achados.append({
                        "Processo": processo,
                        "Vara/Origem": vara,
                        "Pagina": num_pagina,
                        "Arquivo": nome_arquivo
                    })
                    
    return achados