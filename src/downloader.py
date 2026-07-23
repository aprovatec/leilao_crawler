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
        
    # Formata a data para o padrão que o tribunal exige no link (Ex: 2026-07-20)
    data_formatada = data_alvo.strftime("%Y-%m-%d")
    print(f"[*] Buscando diário do TRT-15 para a data: {data_formatada}...")
    
    # URL de exemplo do download direto do DEJT (Caderno Administrativo/Judiciário TRT-15)
    # Nota: Portais de diários frequentemente exigem parâmetros específicos de ID ou código.
    url = f"https://dejt.jt.jus.br/dejt/f/t/diariopdf?dataPublicacao={data_formatada}&tribunal=15"
    
    pasta_destino = os.path.join("data", "raw")
    nome_arquivo = f"trt15_{data_formatada}.pdf"
    caminho_completo = os.path.join(pasta_destino, nome_arquivo)
    
    try:
        response = requests.get(url, timeout=30, verify=True)
        
        # Verifica se o tribunal retornou um PDF válido ou se caiu numa página de erro/sem publicação
        if response.status_code == 200 and b"%PDF" in response.content[:4]:
            with open(caminho_completo, "wb") as f:
                f.write(response.content)
            print(f"[+] Sucesso! Diário baixado e salvo em: {caminho_completo}")
            return caminho_completo
        else:
            print(f"[-] Sem publicações disponíveis para o TRT-15 na data {data_formatada} (Pode ser final de semana ou feriado).")
            return None
            
    except Exception as e:
        print(f"[X] Erro ao tentar conectar com o servidor do TRT-15: {e}")
        return None