import time
import schedule
import subprocess
import datetime
import sys

def executar_robo():
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] Iniciando a varredura diária de leilões...", flush=True)
    
    try:
        # Executa o script principal usando o interpretador do ambiente virtual
        resultado = subprocess.run(["venv\\Scripts\\python.exe", "main.py"], capture_output=True, text=True)
        
        # Exibe o que o robô processou
        if resultado.stdout:
            print(resultado.stdout, flush=True)
        if resultado.stderr:
            print(f"[Aviso/Erro]: {resultado.stderr}", flush=True)
            
    except Exception as e:
        print(f"[X] Erro ao disparar o robô: {e}", flush=True)

# AGENDA PARA RODAR A CADA 10 MINUTOS
schedule.every(10).minutes.do(executar_robo)

print("[-] Monitor de agendamento do Python ativado com sucesso.", flush=True)
print("[-] Aguardando o horário configurado para iniciar a varredura...", flush=True)

while True:
    schedule.run_pending()
    time.sleep(1)