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
        print(f"[INFO] Acessando o site {nome_portal}...", flush=True)
        driver.get(url_portal)

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
        print(f"Erro ao acessar o site {nome_portal}: {e}", flush=True)

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
        print("[ERRO] Não foram encontrados dois arquivos CSV para juntar.")
        return None
    
    # Seleciona os dois arquivos CSV mais recentes
    arquivo_csv1 = arquivos_csv[0]
    arquivo_csv2 = arquivos_csv[1]
    print(f"[INFO] Juntando arquivos: {arquivo_csv1} e {arquivo_csv2}")
    
    linhas_unificadas = []
    linhas1 = ler_arquivo_csv_coringa(arquivo_csv1)
    linhas2 = ler_arquivo_csv_coringa(arquivo_csv2)
    if not linhas1 or not linhas2:
        print("[ERRO] Um dos arquivos CSV está vazio.")
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
    print(f"[SUCESSO] Arquivo unificado salvo em: {arquivo_unificado}")
    return arquivo_unificado

def copiarAreadeTransferencia():
    """
    Função para copiar o conteúdo do arquivo unificado para a área de transferência, formatando como tabela com tabs para colar no Excel.
    """
    import os
    import pyperclip
    pasta_downloads = os.path.join(os.path.expanduser('~'), 'Downloads')
    arquivo_unificado = os.path.join(pasta_downloads, 'relatorio_mensal_unificado.csv')
    if not os.path.exists(arquivo_unificado):
        print("[ERRO] Arquivo unificado não encontrado para copiar para a área de transferência.")
        return
    with open(arquivo_unificado, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    # Substitui as vírgulas por tabs para facilitar a colagem no Excel
    conteudo_com_tabs = '\n'.join(['\t'.join(linha.split(',')) for linha in conteudo.splitlines()])
    pyperclip.copy(conteudo_com_tabs)
    print("[SUCESSO] Conteúdo do relatório unificado copiado para a área de transferência (formato Excel).")

def executar():
    global driver, login_usuario, senha_usuario
    login_usuario, senha_usuario = utils.solicitar_credenciais("Portal Web PMC/PMS")    
    driver = util_selenium.inicializar_webdriver_com_perfil()
    print("Iniciando automação de relatórios mensais...")
    # Executa sequência para PMC
    executar_sequencia_portal("https://pmc.ibge.gov.br/", "PMC")
    # Executa sequência para PMS
    executar_sequencia_portal("https://pms.ibge.gov.br/", "PMS")
    juntarArquivosCSV()
    copiarAreadeTransferencia()
    driver.quit()
    print("Automação de relatórios mensais concluída.")

# para teste.
if __name__ == "__main__":
    juntarArquivosCSV()