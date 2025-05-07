import pyautogui
import time
from automacoes import util_selenium, utils
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from automacoes.util_selenium import inicializar_webdriver
from automacoes.util_selenium import aguardar_elemento

def executarSequenciaPMC():
    """
    Função para acessar o site da PMC e inicializar o WebDriver.
    """
    # Inicializa o WebDriver
    driver =  util_selenium.inicializar_webdriver_com_perfil()

    try:
        urlPMC = "https://portalweb.ibge.gov.br/f5-w-687474703a2f2f77332e706d632e696267652e676f762e6272$$/"
        # Acessa o site Portal Web   
        driver.get(urlPMC)

        #aguarde 5 segundos e abra novamente o site: (as vezes abre só portal web)
        time.sleep(5)
        driver.get(urlPMC)
        # aguarde elemente id="UserName" aparecer:
        aguardar_elemento(driver, (By.ID, "UserName"), 10)
        
        # aguardando usuário fazer login
        print("Aguardando login do usuário...")
        
        aguardar_elemento(driver, (By.ID, "ContentPlaceHolder1_quadroColetaUF"), 10)

        # clicar no 41 - Paraná


        print("Site da PMC aberto com sucesso.")
        

        
        print("Elemento '/Common/portalweb-pms.pa' encontrado na página.")

    except Exception as e:
        print(f"Erro ao acessar o site da PMC: {e}")

    return driver

def executar():
    print("Iniciando automação de relatórios mensais...")        
    drive = executarSequenciaPMC()
    print("Automação de relatórios mensais concluída.")


