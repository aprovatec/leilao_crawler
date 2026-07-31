import os
import glob
import datetime
import pandas as pd

# --- IMPORTAÇÕES DO DOWNLOADER E EXTRACTOR ---
# (Certifique-se de que a função baixar_diario_tjsp existe no seu downloader.py, 
# se não existir, o try/except garante que o script não vai quebrar)
from src.downloader import baixar_diario_trt15
try:
    from src.downloader import baixar_diario_tjsp
except ImportError:
    baixar_diario_tjsp = None

from src.extractor import analisar_pdf

# --- IMPORTAÇÕES PARA O TJ-SP e NOTIFIER ---
from src.extractor_tjsp_prospeccao import extrair_dados_publicacao, salvar_lead_na_planilha
from src.notifier import enviar_alerta_imediato_tj


def obter_data_util():
    """Retorna a data de hoje. Se for sábado ou domingo, retorna a sexta-feira."""
    hoje = datetime.date.today()
    if hoje.weekday() == 5:  # Sábado
        return hoje - datetime.timedelta(days=1)
    elif hoje.weekday() == 6:  # Domingo
        return hoje - datetime.timedelta(days=2)
    return hoje


def executar_rotina_tjsp():
    """Executa a varredura de prospecção do TJ-SP para arquivos baixados na pasta data/raw."""
    print("\n[=== INICIANDO ROTINA DE PROSPECÇÃO TJ-SP ===]")
    
    # 1. Tenta baixar o diário do TJ-SP se a função de download existir
    data_busca = obter_data_util()
    if baixar_diario_tjsp:
        try:
            print("[+] Tentando baixar diário do TJ-SP...")
            baixar_diario_tjsp(data_busca)
        except Exception as e:
            print(f"[X] Aviso/Erro ao baixar diário do TJ-SP: {e}")

    pasta_entrada = os.path.join("data", "raw")
    
    # Busca tanto arquivos .txt quanto .pdf que tenham "tj" no nome
    arquivos_tj = glob.glob(os.path.join(pasta_entrada, "*tj*.txt")) + glob.glob(os.path.join(pasta_entrada, "*tj*.pdf"))
    
    if not arquivos_tj:
        print(f"[-] Nenhum arquivo de diário do TJ-SP encontrado em: '{pasta_entrada}'.")
        print("[!] Dica: O robô precisa baixar ou ter o arquivo do TJ salvo nessa pasta com 'tj' no nome.")
        return

    print(f"[+] Encontrado(s) {len(arquivos_tj)} arquivo(s) do TJ-SP para leitura.")
    
    for caminho_arquivo in arquivos_tj:
        nome_arquivo = os.path.basename(caminho_arquivo)
        print(f"\n---> Analisando diário TJ: {nome_arquivo}")
        
        texto_diario_real = ""
        
        # Se o arquivo for texto puro (.txt)
        if caminho_arquivo.endswith(".txt"):
            with open(caminho_arquivo, "r", encoding="utf-8", errors="ignore") as f:
                texto_diario_real = f.read()
        
        # Se o arquivo for PDF (.pdf)
        elif caminho_arquivo.endswith(".pdf"):
            try:
                texto_diario_real = analisar_pdf(caminho_arquivo)
                if isinstance(texto_diario_real, list):
                    texto_diario_real = str(texto_diario_real)
            except Exception as e:
                print(f"[X] Erro ao tentar ler PDF do TJ: {e}")
                continue

        if not texto_diario_real:
            print(f"[X] Não foi possível extrair texto do arquivo: {nome_arquivo}")
            continue

        # Executa o extrator configurado para Campinas e região
        dados_capturados = extrair_dados_publicacao(texto_diario_real, comarca="Campinas")
        
        if dados_capturados:
            print("[+] Gatilho comercial encontrado no TJ-SP!")
            
            # CORREÇÃO: Caminho relativo compatível com Windows e Linux (GitHub Actions)
            caminho_local_leads = os.path.join("data", "leads_leilao.csv")
            
            # 1. Salva no banco de dados geral
            salvar_lead_na_planilha(dados_capturados, caminho_csv=caminho_local_leads)
            
            # 2. Envia o e-mail individual em HTML imediatamente
            enviar_alerta_imediato_tj(dados_capturados)
        else:
            print(f"[-] Nenhuma homologação de laudo detectada no arquivo: {nome_arquivo}")


def main():
    print("[=== INICIANDO ROTINA DIÁRIA DE LEILÕES TRT-15 ===]\n")
    
    # 1. Tenta baixar o diário do TRT-15 automaticamente
    data_busca = obter_data_util()
    try:
        arquivo_baixado = baixar_diario_trt15(data_busca)
    except Exception as e:
        print(f"[X] Erro ao baixar diário do TRT-15: {e}")
    
    pasta_entrada = os.path.join("data", "raw")
    caminho_saida = os.path.join("data", "processed", "resultados_leilao.csv")
    
    # Garantir que a pasta de saída existe
    os.makedirs(os.path.dirname(caminho_saida), exist_ok=True)
    
    # 2. Busca todos os PDFs disponíveis na pasta para análise (Foco TRT-15)
    arquivos_pdf = [f for f in glob.glob(os.path.join(pasta_entrada, "*.pdf")) if "tj" not in os.path.basename(f).lower()]
    
    if not arquivos_pdf:
        print(f"\n[X] Nenhum arquivo PDF do TRT-15 disponível para análise em '{pasta_entrada}'.")
    else:
        print(f"\n[+] Preparando varredura em {len(arquivos_pdf)} arquivo(s) PDF do TRT-15...")
        
        todos_dados = []
        
        for idx, caminho_pdf in enumerate(arquivos_pdf, start=1):
            nome_arquivo = os.path.basename(caminho_pdf)
            print(f"\n---> Analisando [{idx}/{len(arquivos_pdf)}]: {nome_arquivo}")
            
            dados_arquivo = analisar_pdf(caminho_pdf)
            if dados_arquivo:
                if isinstance(dados_arquivo, list):
                    todos_dados.extend(dados_arquivo)
                
        # 3. Consolida os resultados na planilha do TRT-15
        if todos_dados:
            df = pd.DataFrame(todos_dados)
            if "Processo" in df.columns:
                df = df.drop_duplicates(subset=["Processo"])
            
            print(f"\n[==== SUCESSO: OPORTUNIDADES ENCONTRADAS TRT-15 ====]")
            print(df.to_string(index=False))
            
            if os.path.exists(caminho_saida):
                try:
                    df_antigo = pd.read_csv(caminho_saida, encoding="utf-8-sig")
                    df = pd.concat([df_antigo, df])
                    if "Processo" in df.columns:
                        df = df.drop_duplicates(subset=["Processo"])
                except Exception:
                    pass
                    
            df.to_csv(caminho_saida, index=False, encoding="utf-8-sig")
            print(f"\n[*] Resultados consolidados e salvos em: {caminho_saida}")
        else:
            print("\n[-] Varredura concluída. Nenhuma nova oportunidade detectada no TRT-15.")

    # ==========================================
    # EXECUÇÃO DO TJ-SP EM SEQUÊNCIA
    # ==========================================
    executar_rotina_tjsp()


if __name__ == "__main__":
    main()