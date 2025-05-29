import time
from automacoes import util_selenium, utils
from selenium.webdriver.common.by import By
from automacoes.log_util import obter_logger

logger = obter_logger(__name__)

def aguardar_distribuicao_nao_zero(driver, tempo_espera=60):
    """
    Aguarda até que o elemento com id 'NaoDistribuido' ou 'Distribuido' tenha valor diferente de zero.
    Útil para garantir que a página carregou os dados de distribuição.

    Parâmetros:
        driver: Instância do WebDriver.
        tempo_espera: Tempo máximo de espera em segundos (padrão: 60).
    Retorno:
        bool: True se algum dos elementos ficou diferente de zero, False se tempo esgotado.
    """
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    import time

    logger.info("Aguardando que 'NaoDistribuido' ou 'Distribuido' seja diferente de zero...")
    def condicao(driver):
        for id_elemento in ["NaoDistribuido", "Distribuido"]:
            try:
                elemento = driver.find_element(By.ID, id_elemento)
                texto = elemento.text.strip()
                if texto and texto != "0":
                    logger.info(f"Elemento '{id_elemento}' com valor diferente de zero: {texto}")
                    return True
            except Exception:
                continue
        return False

    try:
        WebDriverWait(driver, tempo_espera).until(condicao)
        return True
    except Exception as erro:
        logger.error(f"Timeout ao aguardar distribuição diferente de zero: {erro}")
        return False

def abrir_pnad_c(driver):
    """
    Acessa o portal web do IBGE, navega até a seção 'PNAD Contínua' e alterna para a nova aba aberta.
    Parâmetros:
        driver: Instância do WebDriver já inicializada.
    """
    url_portal_web = "https://portalweb.ibge.gov.br/"
    driver.get(url_portal_web)
    # Clica no menu principal, aguardando o login se necessário
    util_selenium.clicar_elemento_por_texto_com_fallback(driver, "Pesquisas Domiciliares e Sociais", tempo_espera=180)
    util_selenium.clicar_elemento_por_texto_com_fallback(driver, "PNAD Contínua")
    # Alterna para a nova aba aberta, caso o clique abra em nova aba
    util_selenium.alternar_para_ultima_aba(driver)
    # Aguarda até que o elemento com id 'NaoDistribuido' ou 'Distribuido' seja diferente de zero
    aguardar_distribuicao_nao_zero(driver, tempo_espera=60)
    print("[INFO] Site Carregado")
    # tem que logar ou já está logado?
    if util_selenium.verificar_texto_presente(driver, "Login"):
        util_selenium.clicar_elemento_por_texto_com_fallback(driver, "Login")
        (login, senha) = utils.solicitar_credenciais("Portalweb")
        util_selenium.aguardar_elemento_por_texto(driver, "Login Integrado", tempo_espera=30)
        # Preenche o campo de login
        util_selenium.preencher_campo(driver, (By.ID, "UserName"), login)
        # Preenche o campo de senha
        util_selenium.preencher_campo(driver, (By.ID, "Password"), senha)
        # Clica no botão de login
        util_selenium.clicar_elemento_com_fallback(driver, (By.ID, "login"))
        # Aguarda até aparecer "Login ou senha inválidos." ou "Visão Geral"
        resultado_login = util_selenium.aguardar_textos_na_pagina(
            driver,
            ["Login ou senha inválidos.", "Visão Geral"],
            tempo_espera=30
        )
        if resultado_login == "Login ou senha inválidos.":
            print("[ERRO] Login ou senha inválidos. Limpe suas credenciais e tente novamente.")
            driver.quit()
            return
        # Se for "Visão Geral", segue normalmente
        # Se for None, pode ser timeout, tratar conforme necessário
        elif resultado_login is None:
            print("[ERRO] Não foi possível determinar o resultado do login (timeout).")
            driver.quit()
            return
        # Se "Visão Geral", segue o fluxo normalmente
        time.sleep(2)
    # Já logou.    
    print("[INFO] Acesso à PNAD Contínua concluído.")

def acessarSda(driver):
    """
    Acessa o portal web do IBGE, navega até o SDA e realiza o login, se necessário.
    Preenche os campos de usuário e senha e clica nos botões de login.
    """
    url_portal_web = "https://portalweb.ibge.gov.br/"
    driver.get(url_portal_web)
    # Clica no menu principal, aguardando o login se necessário
    util_selenium.clicar_elemento_por_texto_com_fallback(driver, "Sistemas Administrativos", tempo_espera=180)
    util_selenium.clicar_elemento_por_texto_com_fallback(driver, "SDA")
    # Alterna para a nova aba aberta, caso o clique abra em nova aba
    util_selenium.alternar_para_ultima_aba(driver)    
    # Aqui pode acontecer de pedir o login: (ou sempre?)
    util_selenium.aguardar_elemento_por_texto(driver, "Usuário da Rede", tempo_espera=20)
    (login, senha) = utils.solicitar_credenciais("Portalweb")
    # Preenche diretamente os campos de usuário e senha usando seletores robustos    
    # Preenche o campo de usuário utilizando o novo nome identificado no HTML
    util_selenium.preencher_campo(driver, (By.NAME, "frmPortal-conteudo:j_idt133"), login)
    # Preenche o campo de senha normalmente pelo ID
    util_selenium.preencher_campo(driver, (By.ID, "frmPortal-conteudo:cmpSenha"), senha)
    # tem que verificar caso de erro de login:

    util_selenium.clicar_elemento_por_texto_com_fallback(driver, "Logar", tempo_espera=20)
    util_selenium.clicar_elemento_por_texto_com_fallback(driver, "Ciente", tempo_espera=20)
    time.sleep(3)  # Espera um pouco para garantir que a página carregou completamente

if __name__ == "__main__":
    # Exemplo de teste simples:
    from automacoes import util_selenium
    import automacoes.accesoSistemas as acesso

    driver = util_selenium.inicializar_webdriver_com_perfil()
    try:
        # Chame aqui a função que deseja testar, por exemplo:
        # abrir_pnad_c(driver)
        acessarSda(driver)
        pass
    finally:
        driver.quit()