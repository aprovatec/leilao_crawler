import os
import time
from playwright.sync_api import sync_playwright

def fazer_login_esaj(page, cpf, senha):
    """
    Realiza o login no portal e-SAJ do TJ-SP.
    """
    print("[*] Acessando tela de login do e-SAJ TJ-SP...")
    page.goto("https://esaj.tjsp.jus.br/sajcas/login", timeout=60000)
    
    # Preenche os campos de CPF e Senha
    print("[*] Preenchendo credenciais...")
    page.fill("input[name='username']", cpf)
    page.fill("input[name='password']", senha)
    
    # Clica no botão de submissão
    print("[*] Efetuando autenticação...")
    page.click("input[type='submit']")
    
    # Aguarda o carregamento da navegação
    page.wait_for_load_state("networkidle")
    
    # Valida se o login teve sucesso
    if "sajcas/login" in page.url:
        print("[X] Erro no login: Credenciais inválidas ou bloqueio por CAPTCHA.")
        return False
        
    print("[+] Login realizado com sucesso no e-SAJ!")
    return True

def consultar_processo_esaj(numero_processo, cpf=None, senha=None):
    """
    Acessa o e-SAJ, realiza a consulta de um processo específico e retorna o HTML.
    """
    cpf = cpf or os.environ.get("ESAJ_CPF")
    senha = senha or os.environ.get("ESAJ_SENHA")
    
    if not cpf or not senha:
        print("[X] Erro: CPF ou Senha do e-SAJ não configurados nas variáveis de ambiente.")
        return None

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        try:
            sucesso = fazer_login_esaj(page, cpf, senha)
            if not sucesso:
                browser.close()
                return None
                
            print(f"[*] Consultando processo: {numero_processo}...")
            url_consulta = f"https://esaj.tjsp.jus.br/cpopg/search.do?conversationId=&cbPesquisa=NUMPROC&numeroDigitoAnoUnificado={numero_processo}"
            
            page.goto(url_consulta, timeout=60000)
            page.wait_for_load_state("networkidle")
            
            conteudo_html = page.content()
            browser.close()
            return conteudo_html

        except Exception as e:
            print(f"[X] Erro durante a navegação no e-SAJ: {e}")
            browser.close()
            return None