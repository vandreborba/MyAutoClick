from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def testar_webdriver():
    driver = inicializar_webdriver()
    driver.get("https://www.google.com")
    input("Pressione Enter para fechar o navegador...")
    driver.quit()

# Função para inicializar o WebDriver
def inicializar_webdriver():
    """
    Inicializa o WebDriver do Selenium para o navegador Chrome.
    """
    # Configurações do Chrome
    options = Options()
    # Não adicione 'headless' para garantir que o navegador seja visível
    driver = webdriver.Chrome(options=options)
    return driver

def inicializar_webdriver_com_perfil():
    """
    Inicializa o WebDriver do Selenium utilizando o perfil padrão do usuário do Windows,
    permitindo que qualquer usuário mantenha seus logins e preferências salvos.
    
    Retorna:
        WebDriver: Instância do WebDriver configurada com o perfil do usuário.
    """
    opcoes = Options()
    # Obtém o caminho do diretório do usuário atual do Windows
    import os
    caminho_usuario = os.path.expanduser('~')
    caminho_perfil = rf"{caminho_usuario}\AppData\Local\Google\Chrome\User Data"
    opcoes.add_argument(f"user-data-dir={caminho_perfil}")
    # (Opcional) Pode-se especificar um perfil, ex: 'Profile 1', se necessário
    # opcoes.add_argument("profile-directory=Profile 1")
    driver = webdriver.Chrome(options=opcoes)
    return driver

# Função para aguardar um elemento estar presente na página
def aguardar_elemento(driver, seletor, tempo=10):
    """
    Aguarda até que um elemento esteja presente na página.

    Args:
        driver (WebDriver): Instância do WebDriver.
        seletor (tuple): Tupla contendo o tipo de seletor e o valor (ex: (By.ID, "meu_id")).
        tempo (int): Tempo máximo de espera em segundos.

    Retorna:
        WebElement: O elemento encontrado.
    """
    return WebDriverWait(driver, tempo).until(EC.presence_of_element_located(seletor))

# Função para clicar em um elemento
def clicar_elemento(driver, seletor):
    """
    Localiza e clica em um elemento na página.

    Args:
        driver (WebDriver): Instância do WebDriver.
        seletor (tuple): Tupla contendo o tipo de seletor e o valor (ex: (By.ID, "meu_id")).
    """
    elemento = aguardar_elemento(driver, seletor)
    elemento.click()

# Função para preencher um campo de texto
def preencher_campo(driver, seletor, texto):
    """
    Localiza um campo de texto e insere o texto fornecido.

    Args:
        driver (WebDriver): Instância do WebDriver.
        seletor (tuple): Tupla contendo o tipo de seletor e o valor (ex: (By.ID, "meu_id")).
        texto (str): Texto a ser inserido no campo.
    """
    elemento = aguardar_elemento(driver, seletor)
    elemento.clear()
    elemento.send_keys(texto)