from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import os
import psutil

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
    Inicializa o WebDriver do Selenium utilizando um diretório de perfil exclusivo para automação,
    conforme recomendado para ChromeDriver v136+.
    O usuário pode logar uma vez nesse perfil e a sessão será mantida nas próximas execuções.

    Retorna:
        WebDriver: Instância do WebDriver configurada com o perfil de automação.
    """
    opcoes = Options()
    # Diretório exclusivo para automação (não usar o padrão do usuário)
    caminho_perfil_automacao = os.path.abspath('./chrome_temp_profile')
    if not os.path.exists(caminho_perfil_automacao):
        os.makedirs(caminho_perfil_automacao)
    opcoes.add_argument(f"--user-data-dir={caminho_perfil_automacao}")
    opcoes.add_argument("--profile-directory=Default")
    opcoes.add_argument('--disable-extensions')
    opcoes.add_argument('--no-sandbox')    
    opcoes.add_argument('--disable-gpu')
    opcoes.add_argument('--disable-software-rasterizer')
    opcoes.add_argument('--disable-dev-shm-usage')

    # Força o encerramento de todos os processos do Chrome e relacionados
    processos_encerrar = ['chrome.exe', 'GoogleCrashHandler.exe', 'GoogleUpdate.exe']
    while True:
        processos_ativos = [p for p in psutil.process_iter(['name']) if p.info['name'] in processos_encerrar]
        if processos_ativos:
            print("[ATENÇÃO] Para continuar, feche TODAS as janelas do Google Chrome e finalize processos em segundo plano.")
            for proc in processos_ativos:
                try:
                    print(f"[INFO] Encerrando processo: {proc.info['name']} (PID: {proc.pid})")
                    proc.terminate()
                except Exception as e:
                    print(f"[ERRO] Não foi possível encerrar {proc.info['name']}: {e}")
            input("Após fechar/encerrar, pressione Enter para continuar...")
        else:
            break
    print(f"[INFO] Iniciando o WebDriver com o perfil de automação em: {caminho_perfil_automacao}")
    driver = webdriver.Chrome(options=opcoes)
    print(f"[SUCESSO] WebDriver iniciado com o perfil de automação.")
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
        WebElement: O elemento encontrado ou None se não for localizado.
    """
    try:
        return WebDriverWait(driver, tempo).until(EC.presence_of_element_located(seletor))
    except Exception as erro:
        print(f"[ERRO] Elemento com seletor {seletor} não foi encontrado dentro do tempo limite: {erro}")
        return None

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

def clicar_elemento_por_texto(driver, texto, tag_nome='*', tempo=10):
    """
    Clica em um elemento que contém um texto específico na página.

    Args:
        driver (WebDriver): Instância do WebDriver.
        texto (str): Texto exato ou parcial do elemento a ser clicado.
        tag_nome (str): Nome da tag HTML a ser buscada (ex: 'button', 'a', 'div'). Use '*' para buscar em todas as tags.
        tempo (int): Tempo máximo de espera em segundos.

    Retorna:
        bool: True se o elemento foi clicado com sucesso, False caso contrário.
    """
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    print(f"[INFO] Buscando elemento com texto '{texto}' e tag '{tag_nome}'...")
    try:
        # Monta o XPath para buscar o elemento pelo texto
        xpath = f"//{tag_nome}[contains(normalize-space(text()), '{texto}') or contains(@value, '{texto}') or contains(@aria-label, '{texto}') or contains(@title, '{texto}') ]"
        print(f"[DEBUG] XPath utilizado: {xpath}")
        elemento = WebDriverWait(driver, tempo).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        print(f"[SUCESSO] Elemento encontrado. Realizando clique...")
        elemento.click()
        print(f"[SUCESSO] Clique realizado no elemento com texto '{texto}'.")
        return True
    except Exception as erro:
        # Comentário: Exibe mensagem de erro caso não encontre ou não consiga clicar
        print(f"[ERRO] Não foi possível clicar no elemento com texto '{texto}': {erro}")
        try:
            # Tira um print da tela para facilitar a depuração
            caminho_print = f"screenshot_erro_{texto.replace(' ', '_')}.png"
            driver.save_screenshot(caminho_print)
            print(f"[INFO] Screenshot salvo em: {caminho_print}")
        except Exception as erro_print:
            print(f"[ERRO] Não foi possível salvar o screenshot: {erro_print}")
        return False

def clicar_elemento_com_fallback(driver, seletor):
    """
    Tenta clicar em um elemento normalmente. Se falhar, tenta via JavaScript.
    
    Parâmetros:
        driver (WebDriver): Instância do WebDriver.
        seletor (tuple): Tupla contendo o tipo de seletor e o valor (ex: (By.ID, "meu_id")).
    
    Retorno:
        bool: True se o clique foi realizado com sucesso, False caso contrário.
    """
    try:
        # Aguarda o elemento estar presente e visível na página
        elemento = aguardar_elemento(driver, seletor)
        print(f"[INFO] Tentando clicar normalmente no elemento com seletor: {seletor}")
        elemento.click()
        print("[SUCESSO] Clique realizado normalmente.")
        return True
    except Exception as erro:
        print(f"[ERRO] Clique normal falhou: {erro}. Tentando via JavaScript...")
        try:
            # Tenta clicar usando JavaScript
            driver.execute_script("arguments[0].click();", elemento)
            print("[SUCESSO] Clique realizado via JavaScript.")
            return True
        except Exception as erro_js:
            print(f"[ERRO] Não foi possível clicar nem via JavaScript: {erro_js}")
            try:
                # Tira um print da tela para facilitar a depuração
                caminho_print = f"screenshot_erro_click_{seletor[1].replace(' ', '_')}.png"
                driver.save_screenshot(caminho_print)
                print(f"[INFO] Screenshot salvo em: {caminho_print}")
            except Exception as erro_print:
                print(f"[ERRO] Não foi possível salvar o screenshot: {erro_print}")
            return False

def clicar_elemento_por_texto_com_fallback(driver, texto, nome_tag='*', tempo_espera=10):
    """
    Tenta clicar em um elemento pelo texto, rolando até ele e usando fallback via JavaScript.
    Caso ocorra erro, atualiza a página e tenta novamente uma vez.
    
    Parâmetros:
        driver: Instância do WebDriver.
        texto: Texto do elemento a ser clicado.
        nome_tag: Tag HTML do elemento (ex: 'td', 'button'). Use '*' para qualquer tag.
        tempo_espera: Tempo máximo de espera em segundos.
    
    Retorno:
        bool: True se o clique foi realizado, False caso contrário.
    """
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    def tentar_clicar():
        print(f"[INFO] Buscando elemento com texto '{texto}' e tag '{nome_tag}'...")
        try:
            # Monta o XPath para buscar o elemento pelo texto
            xpath = f"//{nome_tag}[contains(normalize-space(text()), '{texto}')]"
            print(f"[DEBUG] XPath utilizado: {xpath}")
            elemento = WebDriverWait(driver, tempo_espera).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            # Rola até o elemento para garantir visibilidade
            driver.execute_script("arguments[0].scrollIntoView(true);", elemento)
            print("[INFO] Rolando até o elemento antes do clique.")
            try:
                elemento.click()
                print(f"[SUCESSO] Clique realizado normalmente no elemento '{texto}'.")
                return True
            except Exception as erro_click:
                print(f"[ERRO] Clique normal falhou: {erro_click}. Tentando via JavaScript...")
                driver.execute_script("arguments[0].click();", elemento)
                print(f"[SUCESSO] Clique realizado via JavaScript no elemento '{texto}'.")
                return True
        except Exception as erro:
            print(f"[ERRO] Não foi possível clicar no elemento com texto '{texto}': {erro}")
            try:
                caminho_print = f"screenshot_erro_{texto.replace(' ', '_')}.png"
                driver.save_screenshot(caminho_print)
                print(f"[INFO] Screenshot salvo em: {caminho_print}")
            except Exception as erro_print:
                print(f"[ERRO] Não foi possível salvar o screenshot: {erro_print}")
            return False

    # Primeira tentativa de clique
    if tentar_clicar():
        return True
    else:
        print("[INFO] Atualizando a página e tentando novamente...")
        driver.refresh()
        # Opcional: aguarda a página recarregar completamente
        try:
            WebDriverWait(driver, tempo_espera).until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )
        except Exception as erro_espera:
            print(f"[ERRO] Timeout ao aguardar recarregamento da página: {erro_espera}")
        # Segunda tentativa de clique
        return tentar_clicar()

def aguardar_elemento_por_texto(driver, texto, nome_tag='*', tempo_espera=10):
    """
    Aguarda até que um elemento com o texto especificado esteja presente e visível na página.

    Parâmetros:
        driver: Instância do WebDriver.
        texto: Texto do elemento a ser aguardado.
        nome_tag: Tag HTML do elemento (ex: 'td', 'button'). Use '*' para qualquer tag.
        tempo_espera: Tempo máximo de espera em segundos.

    Retorno:
        elemento: WebElement encontrado ou None se não for localizado.
    """
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    print(f"[INFO] Aguardando elemento com texto '{texto}' e tag '{nome_tag}'...")
    try:
        # Monta o XPath para buscar o elemento pelo texto
        xpath = f"//{nome_tag}[contains(normalize-space(text()), '{texto}')]"
        print(f"[DEBUG] XPath utilizado para aguardar: {xpath}")
        elemento = WebDriverWait(driver, tempo_espera).until(
            EC.visibility_of_element_located((By.XPATH, xpath))
        )
        print(f"[SUCESSO] Elemento com texto '{texto}' encontrado e visível.")
        return elemento
    except Exception as erro:
        # Mensagem de erro personalizada para timeout
        print("""
[ERRO] Timeout ao aguardar o elemento com texto '{0}' e tag '{1}'.
Verifique se o elemento realmente existe na página, se o texto está correto ou se há algum problema de carregamento.
Tempo de espera excedido ({2} segundos).
Detalhes do erro: {3}
""".format(texto, nome_tag, tempo_espera, erro))
        try:
            caminho_print = f"screenshot_erro_aguardar_{texto.replace(' ', '_')}.png"
            driver.save_screenshot(caminho_print)
            print(f"[INFO] Screenshot salvo em: {caminho_print}")
        except Exception as erro_print:
            print(f"[ERRO] Não foi possível salvar o screenshot: {erro_print}")
        return None

def alternar_para_ultima_aba(driver):
    """
    Alterna o foco do Selenium para a última aba/janela aberta no navegador.
    Útil quando um clique abre uma nova aba automaticamente.
    Parâmetros:
        driver: Instância do WebDriver.
    """
    # Comentário: Obtém a lista de handles e alterna para o último
    handles = driver.window_handles
    driver.switch_to.window(handles[-1])
    print("[INFO] Alternado para a última aba/janela do navegador.")

def passar_mouse_sobre_elemento_por_texto(driver, texto, nome_tag='*', tempo_espera=10):
    """
    Move o mouse sobre um elemento identificado pelo texto, simulando o hover necessário para exibir menus suspensos.
    Parâmetros:
        driver: Instância do WebDriver.
        texto: Texto do elemento alvo.
        nome_tag: Tag HTML do elemento (ex: 'a', 'div'). Use '*' para qualquer tag.
        tempo_espera: Tempo máximo de espera em segundos.
    """
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    print(f"[INFO] Procurando elemento para hover: '{texto}' (tag: {nome_tag})")
    xpath = f"//{nome_tag}[contains(normalize-space(text()), '{texto}')]"
    elemento = WebDriverWait(driver, tempo_espera).until(
        EC.visibility_of_element_located((By.XPATH, xpath))
    )
    ActionChains(driver).move_to_element(elemento).perform()
    print(f"[INFO] Mouse passado sobre o elemento '{texto}'.")

def selecionar_dropdown_por_label(driver, texto_label, valor):
    """
    Seleciona um valor em um dropdown (<select>) a partir do texto do label associado.

    Parâmetros:
        driver: Instância do WebDriver.
        texto_label: Texto exato do label (ex: 'Ano').
        valor: Valor a ser selecionado no dropdown (ex: '2025').
    """
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import Select

    try:
        # Localiza o label pelo texto
        label = driver.find_element(By.XPATH, f"//label[normalize-space(text())='{texto_label}']")
        id_select = label.get_attribute("for")
        if not id_select:
            print(f"[ERRO] Label '{texto_label}' não possui atributo 'for'.")
            return False
        # Localiza o select pelo id
        select_element = driver.find_element(By.ID, id_select)
        select = Select(select_element)
        try:
            # Tenta selecionar o valor desejado
            select.select_by_value(str(valor))
            print(f"[INFO] Valor '{valor}' selecionado no dropdown '{texto_label}'.")
            return True
        except Exception as erro_selecao:
            # Se não conseguir selecionar, lista as opções disponíveis
            opcoes_disponiveis = [opcao.get_attribute('value') for opcao in select.options]
            print(f"[ERRO] Valor '{valor}' não encontrado no dropdown '{texto_label}'. Opções disponíveis: {opcoes_disponiveis}")
            return False
    except Exception as erro:
        # Erro ao localizar o label ou o select
        print(f"[ERRO] Não foi possível localizar o dropdown associado ao label '{texto_label}': {erro}")
        return False

def listar_opcoes_dropdown_por_label(driver, texto_label):
    """
    Lista todas as opções disponíveis em um dropdown (<select>) a partir do texto do label associado.

    Parâmetros:
        driver: Instância do WebDriver.
        texto_label: Texto exato do label (ex: 'Ano').
    Retorno:
        lista_opcoes: Lista de dicionários com 'valor' e 'texto' de cada opção.
        Exemplo: [{'valor': '2025', 'texto': '2025'}, ...]
        Retorna lista vazia se não encontrar o dropdown.
    """
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import Select

    lista_opcoes = []
    try:
        # Localiza o label pelo texto
        label = driver.find_element(By.XPATH, f"//label[normalize-space(text())='{texto_label}']")
        id_select = label.get_attribute("for")
        if not id_select:
            print(f"[ERRO] Label '{texto_label}' não possui atributo 'for'.")
            return []
        # Localiza o select pelo id
        select_element = driver.find_element(By.ID, id_select)
        select = Select(select_element)
        # Percorre todas as opções do dropdown
        for opcao in select.options:
            valor = opcao.get_attribute('value')
            texto = opcao.text
            lista_opcoes.append({'valor': valor, 'texto': texto})
        print(f"[INFO] Opções encontradas no dropdown '{texto_label}': {lista_opcoes}")
        return lista_opcoes
    except Exception as erro:
        # Erro ao localizar o label ou o select
        print(f"[ERRO] Não foi possível listar opções do dropdown associado ao label '{texto_label}': {erro}")
        return []

def verificar_texto_presente_na_pagina(driver, texto, tempo_espera=5):
    """
    Verifica se um determinado texto está presente na página.

    Parâmetros:
        driver: Instância do WebDriver.
        texto: Texto a ser procurado na página.
        tempo_espera: Tempo máximo de espera em segundos (padrão: 5).
    Retorno:
        bool: True se o texto for encontrado, False caso contrário.
    """
    import time
    from selenium.common.exceptions import TimeoutException

    # Aguarda até o tempo_espera, verificando a cada 0.5s
    tempo_inicial = time.time()
    while time.time() - tempo_inicial < tempo_espera:
        try:
            # Busca o texto no body da página
            corpo_pagina = driver.find_element('tag name', 'body').text
            if texto in corpo_pagina:
                print(f"[INFO] Texto '{texto}' encontrado na página.")
                return True
        except Exception as erro:
            print(f"[ERRO] Erro ao buscar texto na página: {erro}")
        time.sleep(0.5)
    print(f"[INFO] Texto '{texto}' NÃO encontrado na página após {tempo_espera} segundos.")
    return False