import os
import datetime
import requests


def baixar_diario_trt15(data_alvo=None):
    """
    Tenta baixar o Diário Eletrônico da Justiça do Trabalho (DEJT) do TRT-15
    para a data informada (padrão: hoje).
    """
    if data_alvo is None:
        data_alvo = datetime.date.today()
        
    data_formatada = data_alvo.strftime("%Y-%m-%d")
    print(f"[*] Buscando diário do TRT-15 para a data: {data_formatada}...")
    
    url = f"https://dejt.jt.jus.br/dejt/f/t/diariopdf?dataPublicacao={data_formatada}&tribunal=15"
    
    pasta_destino = os.path.join("data", "raw")
    os.makedirs(pasta_destino, exist_ok=True)
    nome_arquivo = f"trt15_{data_formatada}.pdf"
    caminho_completo = os.path.join(pasta_destino, nome_arquivo)
    
    try:
        response = requests.get(url, timeout=30, verify=True)
        
        if response.status_code == 200 and b"%PDF" in response.content[:4]:
            with open(caminho_completo, "wb") as f:
                f.write(response.content)
            print(f"[+] Sucesso! Diário do TRT-15 baixado e salvo em: {caminho_completo}")
            return caminho_completo
        else:
            print(f"[-] Sem publicações disponíveis para o TRT-15 na data {data_formatada} (Pode ser final de semana ou feriado).")
            return None
            
    except Exception as e:
        print(f"[X] Erro ao tentar conectar com o servidor do TRT-15: {e}")
        return None


def baixar_diario_tjsp(data_alvo=None):
    """
    Tenta baixar o Caderno do DJE (TJ-SP) para a data informada (padrão: hoje).
    """
    if data_alvo is None:
        data_alvo = datetime.date.today()
        
    # O DJE TJ-SP usa o formato DD/MM/AAAA para requisições do diário
    data_formatada = data_alvo.strftime("%d/%m/%Y")
    data_arquivo = data_alvo.strftime("%Y-%m-%d")
    
    print(f"[*] Buscando diário do TJ-SP para a data: {data_formatada}...")
    
    # URL padrão de download do caderno do DJE TJ-SP
    url = f"https://www.dje.tjsp.jus.br/cdje/getPaginaDoDiario.do?cdVolume=15&nuDiario=1&cdCaderno=12&nuSeqpagina=1"
    
    pasta_destino = os.path.join("data", "raw")
    os.makedirs(pasta_destino, exist_ok=True)
    
    # É fundamental conter 'tj' no nome para que o main.py reconheça na varredura
    nome_arquivo = f"diario_tjsp_{data_arquivo}.pdf"
    caminho_completo = os.path.join(pasta_destino, nome_arquivo)
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=45, verify=True)
        
        if response.status_code == 200 and (b"%PDF" in response.content[:4] or len(response.content) > 1000):
            with open(caminho_completo, "wb") as f:
                f.write(response.content)
            print(f"[+] Sucesso! Diário do TJ-SP baixado e salvo em: {caminho_completo}")
            return caminho_completo
        else:
            print(f"[-] Sem publicações do TJ-SP disponíveis para a data {data_formatada}.")
            return None
            
    except Exception as e:
        print(f"[X] Erro ao tentar baixar o diário do TJ-SP: {e}")
        return None