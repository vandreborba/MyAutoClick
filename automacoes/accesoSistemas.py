import time
from selenium.webdriver.common.keys import Keys
from automacoes import util_selenium, utils
from selenium.webdriver.common.by import By
from automacoes.log_util import obter_logger
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from automacoes import caixas_dialogo

logger = obter_logger(__name__)

def abrir_portalWeb(driver):
    url_portal_web = "https://portalweb.ibge.gov.br/"
    driver.get(url_portal_web)
    # tela login usuário? ou Entrou?
    texto = util_selenium.aguardar_textos_na_pagina(driver, lista_textos=["Pesquisas Econômicas", "Entrar"], tempo_espera=30)
    if texto == "Pesquisas Econômicas":
        print("[INFO] Acesso ao Portal Web do IBGE concluído.")
        return
    elif texto == "Entrar":
        # exibir caixa de diálogo para solicitar usuário logar manualmente:
        caixas_dialogo.exibir_caixa_dialogo(
            titulo="Acesso ao Portal Web",
            mensagem="Por favor, faça login manualmente no Portal Web do IBGE.",
            tipo="info")
        util_selenium.aguardar_elemento_por_texto(driver, "Pesquisas Econômicas", tempo_espera=360)
        print("[INFO] Acesso ao Portal Web do IBGE concluído.")
        return


def aguardar_distribuicao_nao_zero(driver, tempo_espera=60):
    """
    PnadC:
    Aguarda até que o elemento com id 'NaoDistribuido' ou 'Distribuido' tenha valor diferente de zero.
    Útil para garantir que a página carregou os dados de distribuição.

    Parâmetros:
        driver: Instância do WebDriver.
        tempo_espera: Tempo máximo de espera em segundos (padrão: 60).
    Retorno:
        bool: True se algum dos elementos ficou diferente de zero, False se tempo esgotado.
    """
    

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
    # Utiliza função centralizada para garantir acesso ao portal
    abrir_portalWeb(driver)
    # Clica no menu principal, aguardando o login se necessário
    util_selenium.clicar_elemento_por_texto_com_fallback(driver, "Pesquisas Domiciliares e Sociais", tempo_espera=180)
    util_selenium.clicar_elemento_por_texto_com_fallback(driver, "PNAD Contínua")
    # Alterna para a nova aba aberta, caso o clique abra em nova aba
    util_selenium.alternar_para_ultima_aba(driver)
    # Aguarda até que o elemento com id 'NaoDistribuido' ou 'Distribuido' seja diferente de zero
    aguardar_distribuicao_nao_zero(driver, tempo_espera=60)
    print("[INFO] Site Carregado")
    # Verifica se é necessário realizar login adicional
    if util_selenium.verificar_texto_presente(driver, "Login"):
        util_selenium.clicar_elemento_por_texto_com_fallback(driver, "Login")
        (login, senha) = utils.solicitar_credenciais("Portalweb")
        util_selenium.aguardar_elemento_por_texto(driver, "Login Integrado", tempo_espera=30)
        util_selenium.preencher_campo(driver, (By.ID, "UserName"), login)
        util_selenium.preencher_campo(driver, (By.ID, "Password"), senha)
        util_selenium.clicar_elemento_com_fallback(driver, (By.ID, "login"))
        resultado_login = util_selenium.aguardar_textos_na_pagina(
            driver,
            ["Login ou senha inválidos.", "Visão Geral"],
            tempo_espera=30
        )
        if resultado_login == "Login ou senha inválidos.":
            # Exibe mensagem de erro e encerra o driver
            caixas_dialogo.exibir_caixa_dialogo(
                titulo="Erro de Login",
                mensagem="Login ou senha inválidos. Limpe suas credenciais e tente novamente.",
                tipo="erro"
            )            
            driver.quit()
            return
        elif resultado_login is None:
            print("[ERRO] Não foi possível determinar o resultado do login (timeout).")
            driver.quit()
            return
        time.sleep(2)
    print("[INFO] Acesso à PNAD Contínua concluído.")


def acessarSda(driver):
    """
    Acessa o portal web do IBGE, navega até o SDA e realiza o login, se necessário.
    Preenche os campos de usuário e senha e clica nos botões de login.
    """
    # Utiliza função centralizada para garantir acesso ao portal
    abrir_portalWeb(driver)
    # Clica no menu principal, aguardando o login se necessário    
    util_selenium.clicar_elemento_por_texto_com_fallback(driver, "Sistemas Administrativos", tempo_espera=180)
    util_selenium.clicar_elemento_por_texto_com_fallback(driver, "SDA")
    # Alterna para a nova aba aberta, caso o clique abra em nova aba
    util_selenium.alternar_para_ultima_aba(driver)    
    # Aqui pode acontecer de pedir o login ou não pedir.
    texto = util_selenium.aguardar_textos_na_pagina(driver, lista_textos=["Usuário da Rede", "INÍCIO"], tempo_espera=20)
    if (texto == "Usuário da Rede"):    
        (login, senha) = utils.solicitar_credenciais("Portalweb")
        time.sleep(2)
        driver.switch_to.active_element.send_keys(login)
        util_selenium.preencher_campo(driver, (By.ID, "frmPortal-conteudo:cmpSenha"), senha)
        util_selenium.clicar_elemento_por_texto_com_fallback(driver, "Logar", tempo_espera=20)
        util_selenium.clicar_elemento_por_texto_com_fallback(driver, "Ciente", tempo_espera=20)        
    #todo: tratar caso de erro de senha.
    if (util_selenium.aguardar_elemento_por_texto(driver, "GESTÃO E LOGÍSTICA", tempo_espera=20, contem_texto=True)):
        print("[INFO] Acesso ao SDA concluído.")
    else:
        # execeção:        
        print("\033[91m[ERRO] Não foi possível acessar o SDA. Verifique suas credenciais ou a conexão com a internet.\033[0m")
        driver.quit()
    

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