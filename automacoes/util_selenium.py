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
    Inicializa o WebDriver do Selenium utilizando o perfil padrão do usuário do Windows,
    permitindo que qualquer usuário mantenha seus logins e preferências salvos.
    
    Retorna:
        WebDriver: Instância do WebDriver configurada com o perfil do usuário.
    """
    opcoes = Options()
    # Obtém o caminho do diretório do usuário atual do Windows

    caminho_usuario = os.path.expanduser('~')
    caminho_perfil = rf"{caminho_usuario}\AppData\Local\Google\Chrome\User Data"
    opcoes.add_argument(f"user-data-dir={caminho_perfil}")
    # (Opcional) Pode-se especificar um perfil, ex: 'Profile 1', se necessário
    # opcoes.add_argument("profile-directory=Profile 1")
    # Verifica se o Chrome está em execução
    for processo in psutil.process_iter(['name']):
        if processo.info['name'] == 'chrome.exe':
            input("O navegador Chrome está aberto. Por favor, feche-o e pressione Enter para continuar...")
            break
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