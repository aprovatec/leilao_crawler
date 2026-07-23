import os
import smtplib
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.encoders import encode_base64

# === CONFIGURAÇÃO GLOBAL DE AUTENTICAÇÃO ===
REMETENTE = "f_falchioni@yahoo.com.br"
SENHA_APP = "olkvksypusztcbec"
DESTINATARIO = "f_falchioni@yahoo.com.br"
CAMINHO_LOG = r"C:\Users\User\Documents\Python\leilao_crawler\log_email.txt"

def enviar_alerta_imediato_tj(dados_lead: dict):
    """Dispara um e-mail em HTML estruturado imediatamente para um processo quente do TJ-SP."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(CAMINHO_LOG, "a", encoding="utf-8") as log:
        log.write(f"\n--- Alerta Imediato TJ-SP: {timestamp} ---\n")
        
        # Mapeamento correto com as chaves reais geradas pelo extrator do TJ-SP
        num_processo = dados_lead.get('Processo', 'N/A')
        comarca = dados_lead.get('Comarca', 'Não identificada')
        valor_bem = dados_lead.get('Valor_do_Bem', 'Não informado')
        advogado = dados_lead.get('Advogado_Credor', 'Não extraído')
        oab = dados_lead.get('OAB', 'N/A')
        
        # Como o extrator do TJ não pega a descrição do bem separada, 
        # puxamos o gatilho para contexto
        gatilho = dados_lead.get('Gatilho_Identificado', 'Homologação de Laudo')
        
        msg = MIMEMultipart()
        msg['From'] = REMETENTE
        msg['To'] = DESTINATARIO
        msg['Subject'] = f"🔥 NOVO LEAD TJ-SP: Laudo Homologado - Proc. {num_processo}"

        # Corpo do e-mail em HTML corrigido
        corpo_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
            <div style="max-width: 600px; margin: 0 auto; border: 1px solid #e0e0e0; padding: 20px; border-radius: 8px;">
                <h2 style="color: #d32f2f; margin-top: 0;">🔥 Oportunidade de Prospecção Ativa (TJ-SP)</h2>
                <p>Um novo gatilho de <strong>{gatilho}</strong> foi identificado pelo robô.</p>
                
                <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                    <tr>
                        <td style="padding: 8px; border-bottom: 1px solid #eeeeee; font-weight: bold; width: 35%;">Processo:</td>
                        <td style="padding: 8px; border-bottom: 1px solid #eeeeee;">{num_processo}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border-bottom: 1px solid #eeeeee; font-weight: bold;">Origem/Comarca:</td>
                        <td style="padding: 8px; border-bottom: 1px solid #eeeeee;">{comarca}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border-bottom: 1px solid #eeeeee; font-weight: bold;">Valor do Bem:</td>
                        <td style="padding: 8px; border-bottom: 1px solid #eeeeee; color: #2e7d32; font-weight: bold;">{valor_bem}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border-bottom: 1px solid #eeeeee; font-weight: bold;">Advogado:</td>
                        <td style="padding: 8px; border-bottom: 1px solid #eeeeee;">{advogado} (OAB: {oab})</td>
                    </tr>
                </table>
                
                <div style="background-color: #f9f9f9; padding: 15px; border-left: 4px solid #d32f2f; font-size: 13px;">
                    <strong>Ação Recomendada:</strong> Entrar em contato com o escritório do advogado para oferecer os serviços de leilaria para a execução deste bem penhorado.
                </div>
                
                <p style="font-size: 11px; color: #999; margin-top: 20px; text-align: center;">
                    Robô Leilão Crawler • Alerta gerado em {timestamp}
                </p>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(corpo_html, 'html'))

        try:
            log.write(f"[*] Conectando para enviar alerta do Processo {num_processo}...\n")
            server = smtplib.SMTP_SSL("smtp.mail.yahoo.com", 465, timeout=30)
            server.login(REMETENTE, SENHA_APP)
            server.sendmail(REMETENTE, DESTINATARIO, msg.as_string())
            server.quit()
            
            log.write(f"[+] Alerta individual enviado com sucesso para o processo {num_processo}!\n")
            print(f"[+] Alerta imediato disparado por e-mail: Processo {num_processo}")
            
        except Exception as e:
            log.write(f"[X] Erro ao disparar alerta individual ({num_processo}): {e}\n")
            print(f"[X] Falha ao enviar alerta imediato: {e}")