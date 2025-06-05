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
from automacoes.config_municipio_estado import config_municipio_estado
from automacoes.log_util import obter_logger
from automacoes.caixas_dialogo import exibir_caixa_dialogo

logger = obter_logger(__name__)

login_usuario = None  # Variável global para armazenar o login do usuário
senha_usuario = None  # Variável global para armazenar a senha do usuário
conteudo_csv_exportado = None  # Variável global para armazenar o conteúdo do CSV exportado
driver = None  # Variável global para armazenar o WebDriver

def executar_sequencia_portal(url_portal, nome_portal):
    """
    Função genérica para acessar o portal (PMC ou PMS), realizar login, selecionar estado e cidade,
    e exportar o relatório CSV. O conteúdo do arquivo CSV exportado é salvo na variável global conteudo_csv_exportado.
    Parâmetros:
        url_portal (str): URL do portal a ser acessado.
        nome_portal (str): Nome do portal para exibição nas mensagens.
    Retorna:
        driver: Instância do WebDriver após execução.
    """
    global login_usuario, senha_usuario, driver
    try:
        logger.info(f"Acessando o site {nome_portal}...")
        driver.get(url_portal)

        # Aguarda o elemento de login aparecer
        aguardar_elemento(driver, (By.ID, "UserName"), 10)
        logger.info("Elemento de login encontrado. Preenchendo credenciais...")
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

        # Deixa a primeira letra de cada palavra do estado em maiúscula
        estado = config_municipio_estado.estado.title()
        logger.info(f"Selecionando o estado: {estado}...")
                
        util_selenium.aguardar_elemento_por_texto(
            driver, estado, nome_tag="td", tempo_espera=20
        )
    
        # Tenta clicar normalmente, via JS e dispara manualmente o evento onclick, se existir
        util_selenium.clicar_elemento_por_texto_com_fallback(driver, estado, nome_tag="td", tempo_espera=10)
        
        municipio = config_municipio_estado.municipio.title()

        # Aguarda o elemento da cidade configurada
        util_selenium.aguardar_elemento_por_texto(
            driver, municipio, tempo_espera=20, nome_tag="td"
        )
        time.sleep(1)
        logger.info(f"Clicando na cidade {municipio}...")
        util_selenium.clicar_elemento_por_texto_com_fallback(
            driver, municipio, tempo_espera=5, nome_tag="td"
        )

        # Aguarda o botão de exportação para CSV aparecer na tela
        botao_exportar = util_selenium.aguardar_elemento(driver, (By.ID, "ContentPlaceHolder1_btnExportarCSV"), 30)
        if (botao_exportar):
            logger.info("Botão de exportação para CSV encontrado. Realizando clique...")
            botao_exportar.click()
            logger.info("Clique realizado no botão de exportação para CSV. Aguarde o download...")
            # Aguarda o download do arquivo CSV (delay fixo de 5 segundos)
            time.sleep(5)  # Aguarda 5 segundos para o download
            pasta_downloads = os.path.join(os.path.expanduser('~'), 'Downloads')
            padrao_arquivo = os.path.join(pasta_downloads, '*.csv')
            arquivo_csv = None
            arquivos_csv = glob.glob(padrao_arquivo)
            if arquivos_csv:
                # Pega o arquivo CSV mais recente
                arquivo_csv = max(arquivos_csv, key=os.path.getctime)
            if arquivo_csv and os.path.exists(arquivo_csv):
                logger.info(f"Arquivo CSV encontrado: {arquivo_csv}")
                with open(arquivo_csv, 'r', encoding='utf-8') as f:
                    global conteudo_csv_exportado
                    conteudo_csv_exportado = f.read()
                logger.info("Conteúdo do CSV exportado salvo na variável global.")
            else:
                logger.error("Arquivo CSV não foi encontrado na pasta de downloads.")

        else:
            logger.error("Botão de exportação para CSV não foi encontrado.")

    except Exception as e:
        logger.error(f"Erro ao acessar o site {nome_portal}: {e}")

    return driver

def ler_arquivo_csv_coringa(caminho):
    """
    Tenta ler o arquivo CSV usando UTF-8, se falhar tenta latin-1.
    Retorna as linhas do arquivo.
    """
    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            return f.readlines()
    except UnicodeDecodeError:
        with open(caminho, 'r', encoding='latin-1') as f:
            return f.readlines()

def juntarArquivosCSV():
    """
    Função para juntar os dois arquivos CSV exportados (PMC e PMS), mantendo apenas um cabeçalho.
    O arquivo final será salvo como 'relatorio_mensal_unificado.csv' na pasta Downloads.
    """
    import glob
    import os
    
    # Define a pasta de downloads do usuário
    pasta_downloads = os.path.join(os.path.expanduser('~'), 'Downloads')
    padrao_arquivo = os.path.join(pasta_downloads, '*.csv')
    arquivos_csv = sorted(glob.glob(padrao_arquivo), key=os.path.getctime, reverse=True)
    
    if len(arquivos_csv) < 2:
        logger.error("Não foram encontrados dois arquivos CSV para juntar.")
        return None
    
    # Seleciona os dois arquivos CSV mais recentes
    arquivo_csv1 = arquivos_csv[0]
    arquivo_csv2 = arquivos_csv[1]
    logger.info(f"Juntando arquivos: {arquivo_csv1} e {arquivo_csv2}")
    
    linhas_unificadas = []
    linhas1 = ler_arquivo_csv_coringa(arquivo_csv1)
    linhas2 = ler_arquivo_csv_coringa(arquivo_csv2)
    if not linhas1 or not linhas2:
        logger.error("Um dos arquivos CSV está vazio.")
        return None
    # Adiciona o cabeçalho do primeiro arquivo
    linhas_unificadas.append(linhas1[0].strip())
    # Adiciona os dados do primeiro arquivo (sem o cabeçalho)
    linhas_unificadas.extend([linha.strip() for linha in linhas1[1:]])
    # Adiciona os dados do segundo arquivo (sem o cabeçalho)
    linhas_unificadas.extend([linha.strip() for linha in linhas2[1:]])
    
    # Salva o arquivo unificado

    arquivo_unificado = os.path.join(pasta_downloads, 'relatorio_mensal_unificado.csv')
    with open(arquivo_unificado, 'w', encoding='utf-8') as f:
        for linha in linhas_unificadas:
            f.write(linha + '\n')
    logger.info(f"Arquivo unificado salvo em: {arquivo_unificado}")
    # limpar tela:
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"Arquivo unificado salvo em: {arquivo_unificado}")
    return arquivo_unificado

def copiarAreadeTransferencia():
    """
    Função para copiar o conteúdo do arquivo unificado para a área de transferência, formatando como tabela com tabs para colar no Excel.
    Substitui apenas o caractere ';' por tab ('\t') na cópia para a área de transferência.
    """
    import os
    import pyperclip
    pasta_downloads = os.path.join(os.path.expanduser('~'), 'Downloads')
    arquivo_unificado = os.path.join(pasta_downloads, 'relatorio_mensal_unificado.csv')
    if not os.path.exists(arquivo_unificado):
        logger.error("Arquivo unificado não encontrado para copiar para a área de transferência.")
        return
    with open(arquivo_unificado, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    # Substitui apenas o caractere ';' por tab para facilitar a colagem no Excel
    conteudo_com_tabs = conteudo.replace(';', '\t')
    pyperclip.copy(conteudo_com_tabs)
    logger.info("Conteúdo do relatório unificado copiado para a área de transferência (formato Excel, separador tab).")
    
    

def executar():
    global driver, login_usuario, senha_usuario
    login_usuario, senha_usuario = utils.solicitar_credenciais("Portal Web PMC/PMS")    
    driver = util_selenium.inicializar_webdriver_com_perfil()
    logger.info("Iniciando automação de relatórios mensais...")
    # Executa sequência para PMC
    executar_sequencia_portal("https://pmc.ibge.gov.br/", "PMC")
    # Executa sequência para PMS
    executar_sequencia_portal("https://pms.ibge.gov.br/", "PMS")
    juntarArquivosCSV()
    copiarAreadeTransferencia()
    driver.quit()
    mensagem = (
        "Conteúdo do relatório unificado copiado para a área de transferência.\n\n"
        "O arquivo 'relatorio_mensal_unificado.csv' foi salvo na sua pasta Downloads."
    )
    exibir_caixa_dialogo(
        titulo="Relatório Unificado",
        mensagem=mensagem,
        tipo="sucesso"
    )
    logger.info("Automação de relatórios mensais concluída.")
    print("Automação de relatórios mensais concluída.")

# para teste.
if __name__ == "__main__":
    juntarArquivosCSV()