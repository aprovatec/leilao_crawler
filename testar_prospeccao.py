from src.extractor_tjsp_prospeccao import extrair_dados_publicacao, salvar_lead_na_planilha
# Trocamos a função antiga de planilha pela nova de alerta imediato
from src.notifier import enviar_alerta_imediato_tj 

# Texto simulado do DJE (Gatilho comercial do TJ-SP)
texto_diario_oficial = """
Campinas - Foro de Campinas - 2ª Vara Cível. Processo 1004321-88.2025.8.26.0114 - Execução de Título Extrajudicial - IBI PROMOTORA DE VENDAS LTDA. Vistos. HOMOLOGO O LAUDO DE AVALIAÇÃO do imóvel penhorado no valor de R$ 850.000,00. Intime-se o exequente via patrono Dr. Roberto Silva (OAB/SP 123.456) para manifestar termos de leilaria.
"""

print("[-] Testando extrator de prospecção e envio de alerta imediato...")

dados_capturados = extrair_dados_publicacao(texto_diario_oficial, comarca="Campinas")

if dados_capturados:
    print("\n[+] Dados capturados com sucesso!")
    
    # # 1. Salva localmente na planilha de prospecção (histórico geral)
    caminho_local = r"C:\Users\User\Documents\Python\leilao_crawler\data\leads_leilao.csv"
    salvar_lead_na_planilha(dados_capturados, caminho_csv=caminho_local)
    print(f"[+] Gravado na planilha local: {caminho_local}")
    
    # # 2. Dispara o e-mail individual IMEDIATO em HTML
    print("[*] Chamando o notifier para enviar o alerta individual em tempo real...")
    enviar_alerta_imediato_tj(dados_capturados)

else:
    print("\n[X] O robô ignorou o texto ou não encontrou os gatilhos.")

if dados_capturados:
    print("\n[+] Dados capturados com sucesso!")
    print("ESTES SÃO OS DADOS GERADOS PELO EXTRATOR:", dados_capturados) # <--- ADICIONE ESTA LINHA
    
    # ... resto do código continua igual