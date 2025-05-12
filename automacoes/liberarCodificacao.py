from automacoes import util_selenium


driver = None  # Variável global para armazenar o WebDriver
def sequencia_portal():
    global driver

    # Solicitar o mês para liberar:
    mes = input("Digite o mês para liberar a codificação (ex: 5): ")

    # Será se este endereço muda com o tempo?
    urlLiberarCodificacao = "https://portalweb.ibge.gov.br/f5-w-68747470733a2f2f773373696763706e6164632e696267652e676f762e6272$$/f5-h-$$/LiberarParaCodificacao"    
    
    # Acessa o portal web:
    urlPortalWeb = "https://portalweb.ibge.gov.br/"
    driver.get(urlPortalWeb)
    util_selenium.clicar_elemento_por_texto_com_fallback(driver, "Pesquisas Domiciliares e Sociais")
    util_selenium.clicar_elemento_por_texto_com_fallback(driver, "PNAD Contínua")    
    # Após clicar, alterna para a nova aba aberta (caso o clique abra em nova aba)
    util_selenium.alternar_para_ultima_aba(driver)
    # Comentário: Garante que o Selenium continue operando na aba correta

    # Vamos tentr acessar a URL diretamente agora:
    driver.get(urlLiberarCodificacao)

    # tem que aguardar o carregamento: Aguardar aparecer 41 - Paraná:
    util_selenium.aguardar_elemento_por_texto(driver, "41 - PARANÁ", tempo_espera=30)    

    



def executar():
    global driver  
    print("Iniciando automação para liberar codificação...")

    driver = util_selenium.inicializar_webdriver_com_perfil()
    sequencia_portal()


    # Terminou:
    # driver.quit()
    print("Automação concluída.")