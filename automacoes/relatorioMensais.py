import pyautogui
import time
from automacoes import util_selenium, utils
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from automacoes.util_selenium import clicar_elemento, clicar_elemento_com_fallback, clicar_elemento_por_texto, clicar_elemento_por_texto_com_fallback, inicializar_webdriver
from automacoes.util_selenium import aguardar_elemento
import os 
import glob  
import pyperclip

login_usuario = None  # Variável global para armazenar o login do usuário
senha_usuario = None  # Variável global para armazenar a senha do usuário
conteudo_csv_exportado = None  # Variável global para armazenar o conteúdo do CSV exportado
driver = None  # Variável global para armazenar o WebDriver

def executarSequenciaPMC():
    global login_usuario, senha_usuario, driver  # Adicionado 'driver' como global    
    """
    Função para acessar o site da PMC e inicializar o WebDriver.
    """
    try:
        urlPMC = "https://portalweb.ibge.gov.br/f5-w-687474703a2f2f77332e706d632e696267652e676f762e6272$$/"        
        # Acessa o site Portal Web (primeiro acesso abre o portal intermediário)
        driver.get(urlPMC)      
        print("[INFO] Acessando o site Portal Web PMC/PMS...")          
        # O primeiro acesso carrega o portal web, que funciona como um gateway.
        # Após o carregamento, é necessário acessar novamente para abrir o site PMC correto.
        time.sleep(3)      
        print("[INFO] Acessando o site PMC...")
        driver.get(urlPMC) 

        # aguarde elemente id="UserName" aparecer:
        aguardar_elemento(driver, (By.ID, "UserName"), 10)
        print("[INFO] Elemento de login encontrado. Preenchendo credenciais...")
                
        # id = UserName e id = ContentPlaceHolder1_Password
        # preencher camos:
        campo_login = driver.find_element(By.ID, "UserName")
        campo_login.send_keys(login_usuario)
        campo_senha = driver.find_element(By.ID, "ContentPlaceHolder1_Password")
        campo_senha.send_keys(senha_usuario)
        # Aguardar 1 segundos:
        time.sleep(1)

        # clique no id="btnLogin"
        clicar_elemento_com_fallback(driver, (By.ID, "btnLogin"))

        # Aguardar entrar:                
        aguardar_elemento(driver, (By.ID, "ContentPlaceHolder1_quadroColetaUF"), 10)
        
        time.sleep(2)

        # clicar no 41 - Paraná:
                        
        print("[INFO] Clicando no estado Paraná...")
        clicar_elemento_por_texto_com_fallback(driver, "41 - Paraná", nome_tag="td")        
        

        # Aguarda o elemento com o texto "411520000 - Maringá" aparecer na tela antes de clicar
        # Comentário: Utiliza função centralizada para aguardar o elemento por texto, garantindo clareza e reutilização
        util_selenium.aguardar_elemento_por_texto(
            driver, "411520000 - Maringá", nome_tag="td", tempo_espera=20
        )                    
        print("[INFO] Clicando na cidade Maringá...")
        time.sleep(1)
        util_selenium.clicar_elemento_por_texto_com_fallback(
                driver, "411520000 - Maringá", nome_tag="td", tempo_espera=5
            )            
                        
        # Aguarda o botão de exportação para CSV aparecer na tela
        botao_exportar = util_selenium.aguardar_elemento(driver, (By.ID, "ContentPlaceHolder1_btnExportarCSV"), 30)        
        if (botao_exportar):
            print("[INFO] Botão de exportação para CSV encontrado. Realizando clique...")
            botao_exportar.click()
            print("[INFO] Clique realizado no botão de exportação para CSV. Aguarde o download...")
            # Aguarda o download do arquivo CSV
            pasta_downloads = os.path.join(os.path.expanduser('~'), 'Downloads')
            padrao_arquivo = os.path.join(pasta_downloads, '*.csv')
            arquivo_csv = None
            tempo_espera = 30  # Tempo máximo de espera pelo download (segundos)
            tempo_inicial = time.time()
            while time.time() - tempo_inicial < tempo_espera:
                arquivos_csv = glob.glob(padrao_arquivo)
                if arquivos_csv:
                    # Pega o arquivo CSV mais recente
                    arquivo_csv = max(arquivos_csv, key=os.path.getctime)
                    # Garante que o arquivo não está mais sendo escrito
                    if not arquivo_csv.endswith('.crdownload'):
                        break
                time.sleep(1)
            if arquivo_csv and os.path.exists(arquivo_csv):
                print(f"[SUCESSO] Arquivo CSV encontrado: {arquivo_csv}")
                with open(arquivo_csv, 'r', encoding='utf-8') as f:
                    global conteudo_csv_exportado
                    conteudo_csv_exportado = f.read()
                print("[INFO] Conteúdo do CSV exportado salvo na variável global.")
            else:
                print("[ERRO] Arquivo CSV não foi encontrado na pasta de downloads.")
        else:
            print("[ERRO] Botão de exportação para CSV não foi encontrado.")

    except Exception as e:
        print(f"Erro ao acessar o site da PMC: {e}")

    return driver

def executarSequenciaPMS():
    """
    Função para acessar o site da PMS e inicializar o WebDriver.
    O fluxo é idêntico ao da PMC, mudando apenas a URL de acesso.
    O conteúdo do arquivo CSV exportado é salvo na variável global conteudo_csv_exportado.
    """
    global login_usuario, senha_usuario, driver  # Adicionado 'driver' como global    

    try:
        urlPMS = "https://portalweb.ibge.gov.br/f5-w-687474703a2f2f77332e706d732e696267652e676f762e6272$$/"
        # Acessa o site Portal Web (primeiro acesso abre o portal intermediário)
        driver.get(urlPMS)
        print("[INFO] Acessando o site Portal Web PMS...", flush=True)
        # O primeiro acesso carrega o portal web, que funciona como um gateway.
        # Após o carregamento, é necessário acessar novamente para abrir o site PMS correto.
        time.sleep(3)
        print("[INFO] Acessando o site PMS...", flush=True)
        driver.get(urlPMS)

        # Aguarda o elemento de login aparecer
        aguardar_elemento(driver, (By.ID, "UserName"), 10)
        print("[INFO] Elemento de login encontrado. Preenchendo credenciais...", flush=True)
        # Preenche os campos de login e senha
        campo_login = driver.find_element(By.ID, "UserName")
        campo_login.send_keys(login_usuario)
        campo_senha = driver.find_element(By.ID, "ContentPlaceHolder1_Password")
        campo_senha.send_keys(senha_usuario)
        time.sleep(1)
        # Clica no botão de login
        clicar_elemento_com_fallback(driver, (By.ID, "btnLogin"))

        # Aguarda entrar no sistema
        aguardar_elemento(driver, (By.ID, "ContentPlaceHolder1_quadroColetaUF"), 10)
        time.sleep(2)

        # Clica no estado Paraná
        print("[INFO] Clicando no estado Paraná...", flush=True)
        clicar_elemento_por_texto_com_fallback(driver, "41 - Paraná", nome_tag="td")

        # Aguarda o elemento da cidade Maringá
        util_selenium.aguardar_elemento_por_texto(
            driver, "411520000 - Maringá", nome_tag="td", tempo_espera=20
        )
        time.sleep(1)
        print("[INFO] Clicando na cidade Maringá...", flush=True)
        util_selenium.clicar_elemento_por_texto_com_fallback(
            driver, "411520000 - Maringá", nome_tag="td", tempo_espera=5
        )

        # Aguarda o botão de exportação para CSV aparecer na tela
        botao_exportar = util_selenium.aguardar_elemento(driver, (By.ID, "ContentPlaceHolder1_btnExportarCSV"), 30)
        if botao_exportar:
            print("[INFO] Botão de exportação para CSV encontrado. Realizando clique...", flush=True)
            botao_exportar.click()
            print("[INFO] Clique realizado no botão de exportação para CSV. Aguarde o download...", flush=True)
            # Aguarda o download do arquivo CSV
            pasta_downloads = os.path.join(os.path.expanduser('~'), 'Downloads')
            padrao_arquivo = os.path.join(pasta_downloads, '*.csv')
            arquivo_csv = None
            tempo_espera = 30  # Tempo máximo de espera pelo download (segundos)
            tempo_inicial = time.time()
            while time.time() - tempo_inicial < tempo_espera:
                arquivos_csv = glob.glob(padrao_arquivo)
                if arquivos_csv:
                    # Pega o arquivo CSV mais recente
                    arquivo_csv = max(arquivos_csv, key=os.path.getctime)
                    # Garante que o arquivo não está mais sendo escrito
                    if not arquivo_csv.endswith('.crdownload'):
                        break
                time.sleep(1)
            if arquivo_csv and os.path.exists(arquivo_csv):
                print(f"[SUCESSO] Arquivo CSV encontrado: {arquivo_csv}", flush=True)
                with open(arquivo_csv, 'r', encoding='utf-8') as f:
                    global conteudo_csv_exportado
                    conteudo_csv_exportado = f.read()
                print("[INFO] Conteúdo do CSV exportado salvo na variável global.", flush=True)
            else:
                print("[ERRO] Arquivo CSV não foi encontrado na pasta de downloads.", flush=True)
        else:
            print("[ERRO] Botão de exportação para CSV não foi encontrado.", flush=True)

    except Exception as e:
        print(f"Erro ao acessar o site da PMS: {e}", flush=True)

    return driver

def executar():
    global driver, login_usuario, senha_usuario  # Indica que as variáveis são globais e podem ser modificadas nesta função
    # Solicita as credenciais do usuário e armazena nas variáveis globais
    login_usuario, senha_usuario = utils.solicitar_credenciais("Portal Web PMC/PMS")    
    # Inicializa o WebDriver
    driver =  util_selenium.inicializar_webdriver_com_perfil()

    print("Iniciando automação de relatórios mensais...")        
    executarSequenciaPMC()
    executarSequenciaPMS()
    print("Automação de relatórios mensais concluída.")

    # Copia o conteúdo do CSV exportado para a área de transferência

    if conteudo_csv_exportado:
        pyperclip.copy(conteudo_csv_exportado)
        print("[INFO] Conteúdo do CSV exportado copiado para a área de transferência.")
    else:
        print("[ATENÇÃO] Variável conteudo_csv_exportado está vazia, nada foi copiado.")


