from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import os
import psutil
from automacoes.log_util import obter_logger

logger = obter_logger(__name__)

# Constante para controlar exibição dos logs do Chromedriver/Chrome
EXIBIR_LOGS_CHROMEDRIVER = False  # Altere para True para ver logs do driver no console

# Constante para o caminho do Chrome Portable (Desktop do usuário)
CAMINHO_CHROME_PORTABLE = os.path.join(os.path.expanduser('~'), 'Desktop', 'GoogleChromePortable', 'App', 'Chrome-bin', 'chrome.exe')

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
    Inicializa o WebDriver do Selenium utilizando um diretório de perfil exclusivo para automação.
    Se o Chrome Portable estiver disponível, utiliza-o; caso contrário, utiliza o Chrome padrão do sistema.
    O usuário pode logar uma vez nesse perfil e a sessão será mantida nas próximas execuções.

    Retorna:
        WebDriver: Instância do WebDriver configurada com o perfil de automação.
    """
    from selenium.webdriver.chrome.service import Service
    opcoes = Options()
    # Diretório exclusivo para automação (não usar o padrão do usuário)
    caminho_perfil_automacao = os.path.abspath('./chrome_temp_profile')
    if not os.path.exists(caminho_perfil_automacao):
        os.makedirs(caminho_perfil_automacao)
    opcoes.add_argument(f"--user-data-dir={caminho_perfil_automacao}")
    opcoes.add_argument("--profile-directory=Default")
    opcoes.add_argument('--disable-extensions')
    opcoes.add_argument('--no-sandbox')    
    if not EXIBIR_LOGS_CHROMEDRIVER:
        opcoes.add_argument('--log-level=4')  # Minimiza logs do Chrome
    prefs = {
        "plugins.always_open_pdf_externally": True
    }
    opcoes.add_experimental_option("prefs", prefs)

    # Se o Chrome Portable existir, usa ele; senão, usa o Chrome padrão
    if os.path.exists(CAMINHO_CHROME_PORTABLE):
        opcoes.binary_location = CAMINHO_CHROME_PORTABLE
        logger.info(f"Chrome Portable detectado e será utilizado: {CAMINHO_CHROME_PORTABLE}")
    else:
        logger.info("Chrome Portable não encontrado. Usando Chrome padrão do sistema.")

    # Suprime logs do Chromedriver se a constante estiver False
    if EXIBIR_LOGS_CHROMEDRIVER:
        servico = Service()
    else:
        servico = Service(log_path=os.devnull)

    logger.info(f"Iniciando o WebDriver com o perfil de automação em: {caminho_perfil_automacao}")
    driver = webdriver.Chrome(options=opcoes, service=servico)
    logger.info(f"WebDriver iniciado com o perfil de automação.")
    return driver

# Função para inicializar o WebDriver de forma indetectável
# Utiliza o pacote undetected-chromedriver para evitar bloqueios por servidores

def inicializar_webdriver_indetectavel():
    """
    Inicializa o WebDriver do Selenium utilizando undetected-chromedriver,
    dificultando a detecção por sites que bloqueiam automações.
    Retorna:
        WebDriver: Instância do WebDriver indetectável.
    """
    import undetected_chromedriver as uc
    # Comentário: Configurações do Chrome podem ser personalizadas conforme necessário
    opcoes = uc.ChromeOptions()
    # Não adicione 'headless' para garantir que o navegador seja visível
    # Exemplo de configuração adicional:
    # opcoes.add_argument('--disable-blink-features=AutomationControlled')
    driver = uc.Chrome(options=opcoes, headless=False, use_subprocess=True)
    logger.info("WebDriver indetectável iniciado com undetected-chromedriver.")
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
        logger.error(f"Elemento com seletor {seletor} não foi encontrado dentro do tempo limite: {erro}")
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

    logger.info(f"Buscando elemento com texto '{texto}' e tag '{tag_nome}'...")
    try:
        # Monta o XPath para buscar o elemento pelo texto
        xpath = f"//{tag_nome}[contains(normalize-space(text()), '{texto}') or contains(@value, '{texto}') or contains(@aria-label, '{texto}') or contains(@title, '{texto}') ]"
        logger.debug(f"XPath utilizado: {xpath}")
        elemento = WebDriverWait(driver, tempo).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        logger.info(f"Elemento encontrado. Realizando clique...")
        elemento.click()
        logger.info(f"Clique realizado no elemento com texto '{texto}'.")
        return True
    except Exception as erro:
        # Comentário: Exibe mensagem de erro caso não encontre ou não consiga clicar
        logger.error(f"Não foi possível clicar no elemento com texto '{texto}': {erro}")
        try:
            # Tira um print da tela para facilitar a depuração
            caminho_print = f"screenshot_erro_{texto.replace(' ', '_')}.png"
            driver.save_screenshot(caminho_print)
            logger.info(f"Screenshot salvo em: {caminho_print}")
        except Exception as erro_print:
            logger.error(f"Não foi possível salvar o screenshot: {erro_print}")
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
        logger.info(f"Tentando clicar normalmente no elemento com seletor: {seletor}")
        elemento.click()
        logger.info("Clique realizado normalmente.")
        return True
    except Exception as erro:
        logger.error(f"Clique normal falhou: {erro}. Tentando via JavaScript...")
        try:
            # Tenta clicar usando JavaScript
            driver.execute_script("arguments[0].click();", elemento)
            logger.info("Clique realizado via JavaScript.")
            return True
        except Exception as erro_js:
            logger.error(f"Não foi possível clicar nem via JavaScript: {erro_js}")
            try:
                # Tira um print da tela para facilitar a depuração
                caminho_print = f"screenshot_erro_click_{seletor[1].replace(' ', '_')}.png"
                driver.save_screenshot(caminho_print)
                logger.info(f"Screenshot salvo em: {caminho_print}")
            except Exception as erro_print:
                logger.error(f"Não foi possível salvar o screenshot: {erro_print}")
            return False

def clicar_elemento_por_texto_com_fallback(driver, texto, nome_tag='*', tempo_espera=10, reiniciar_ao_falhar=True):
    """
    Tenta clicar em um elemento pelo texto, rolando até ele e usando fallback via JavaScript.
    Caso ocorra erro, pode atualizar a página e tentar novamente uma vez, dependendo do parâmetro reiniciar_ao_falhar.
    
    Parâmetros:
        driver: Instância do WebDriver.
        texto: Texto do elemento a ser clicado.
        nome_tag: Tag HTML do elemento (ex: 'td', 'button'). Use '*' para qualquer tag.
        tempo_espera: Tempo máximo de espera em segundos.
        reiniciar_ao_falhar: Se True, reinicia a página e tenta novamente ao falhar. Se False, não reinicia.
    
    Retorno:
        bool: True se o clique foi realizado, False caso contrário.
    """
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    import time

    def tentar_clicar():
        logger.info(f"Buscando elemento com texto '{texto}' e tag '{nome_tag}'...")
        try:
            # Monta o XPath para buscar o elemento pelo texto
            xpath = f"//{nome_tag}[contains(normalize-space(text()), '{texto}')]"
            logger.debug(f"XPath utilizado: {xpath}")
            elemento = WebDriverWait(driver, tempo_espera).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            # Rola até o elemento para garantir visibilidade
            driver.execute_script("arguments[0].scrollIntoView(true);", elemento)
            logger.info("Rolando até o elemento antes do clique.")
            time.sleep(0.2)  # Aguarda a rolagem concluir
            # Verifica se o elemento está visível e não coberto
            if not elemento.is_displayed():
                logger.error(f"Elemento com texto '{texto}' não está visível na tela.")
                return False
            try:
                elemento.click()
                logger.info(f"Clique realizado normalmente no elemento '{texto}'.")
                return True
            except Exception as erro_click:
                logger.error(f"Clique normal falhou: {erro_click}. Tentando via JavaScript...")
                try:
                    driver.execute_script("arguments[0].click();", elemento)
                    logger.info(f"Clique realizado via JavaScript no elemento '{texto}'.")
                    return True
                except Exception as erro_js:
                    logger.error(f"Clique via JavaScript também falhou: {erro_js}")
                    return False
        except Exception as erro:
            logger.error(f"Não foi possível clicar no elemento com texto '{texto}': {erro}")
            try:
                caminho_print = f"screenshot_erro_{texto.replace(' ', '_')}.png"
                driver.save_screenshot(caminho_print)
                logger.info(f"Screenshot salvo em: {caminho_print}")
            except Exception as erro_print:
                logger.error(f"Não foi possível salvar o screenshot: {erro_print}")
            return False

    # Primeira tentativa de clique
    if tentar_clicar():
        return True
    else:
        if reiniciar_ao_falhar:
            logger.info("Atualizando a página e tentando novamente...")            
            # Aguarda a página recarregar completamente
            try:
                WebDriverWait(driver, tempo_espera).until(
                    lambda d: d.execute_script('return document.readyState') == 'complete'
                )
            except Exception as erro_espera:
                logger.error(f"Timeout ao aguardar recarregamento da página: {erro_espera}")
            # Segunda tentativa de clique
            return tentar_clicar()
        else:
            logger.info("Não irá reiniciar a página após falha, conforme parâmetro reiniciar_ao_falhar=False.")
            return False

def aguardar_elemento_por_texto(driver, texto, nome_tag='*', tempo_espera=10, contem_texto=True):
    """
    Aguarda até que um elemento com o texto especificado esteja presente e visível na página.

    Parâmetros:
        driver: Instância do WebDriver.
        texto: Texto do elemento a ser aguardado.
        nome_tag: Tag HTML do elemento (ex: 'td', 'button'). Use '*' para qualquer tag.
        tempo_espera: Tempo máximo de espera em segundos.
        contem_texto: Se True, faz correspondência parcial e ignora maiúsculas/minúsculas. Se False, exige correspondência exata (case sensitive).

    Retorno:
        elemento: WebElement encontrado ou None se não for localizado.
    """
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    logger.info(f"Aguardando elemento com texto '{texto}' e tag '{nome_tag}'...")
    try:
        if contem_texto:
            # Busca parcial, ignorando maiúsculas/minúsculas
            xpath = f"//{nome_tag}[contains(translate(normalize-space(text()), 'ABCDEFGHIJKLMNOPQRSTUVWXYZÁÉÍÓÚÂÊÎÔÛÃÕÀÇ', 'abcdefghijklmnopqrstuvwxyzáéíóúâêîôûãõàç'), '{texto.lower()}')]"
        else:
            # Busca exata, case sensitive
            xpath = f"//{nome_tag}[normalize-space(text())='{texto}']"
        logger.debug(f"XPath utilizado para aguardar: {xpath}")
        elemento = WebDriverWait(driver, tempo_espera).until(
            EC.visibility_of_element_located((By.XPATH, xpath))
        )
        logger.info(f"Elemento com texto '{texto}' encontrado e visível.")
        return elemento
    except Exception as erro:
        # Mensagem de erro personalizada para timeout
        logger.error(f"\nTimeout ao aguardar o elemento com texto '{texto}' e tag '{nome_tag}'.\nVerifique se o elemento realmente existe na página, se o texto está correto ou se há algum problema de carregamento.\nTempo de espera excedido ({tempo_espera} segundos).\nDetalhes do erro: {erro}\n")
        try:
            caminho_print = f"screenshot_erro_aguardar_{texto.replace(' ', '_')}.png"
            driver.save_screenshot(caminho_print)
            logger.info(f"Screenshot salvo em: {caminho_print}")
        except Exception as erro_print:
            logger.error(f"Não foi possível salvar o screenshot: {erro_print}")
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
    logger.info("Alternado para a última aba/janela do navegador.")

def fechar_todas_abas(driver):
    """
    Fecha todas as abas/janelas abertas do navegador, mantendo apenas a primeira.
    Útil para garantir que a automação comece com apenas uma aba aberta.
    """
    try:
        handles = driver.window_handles
        if not handles:
            return
        # Mantém a primeira aba e fecha as demais
        for h in handles[1:]:
            try:
                driver.switch_to.window(h)
                driver.close()
            except Exception as e:
                logger.warning(f"Falha ao fechar aba/janela {h}: {e}")
        # Garante foco na primeira aba remanescente
        driver.switch_to.window(handles[0])
        logger.info("Todas as abas extras foram fechadas; permaneceu apenas a primeira.")
    except Exception as e:
        logger.error(f"Erro ao fechar abas/janelas: {e}")

def passar_mouse_sobre_elemento_por_texto(driver, texto, nome_tag='*', tempo_espera=10):
    """
    Move o mouse sobre um elemento identificado pelo texto, simulando o hover necessário para exibir menus suspensos.
    Garante robustez para menus <a> do IBGE, disparando eventos JavaScript de mouseover/mouseenter caso necessário.
    Parâmetros:
        driver: Instância do WebDriver.
        texto: Texto do elemento alvo.
        nome_tag: Tag HTML do elemento (ex: 'a', 'div'). Use '*' para qualquer tag.
        tempo_espera: Tempo máximo de espera em segundos.
    Retorno:
        bool: True se o hover foi realizado com sucesso, False caso contrário.
    """
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    import time

    logger.info(f"Procurando elemento para hover: '{texto}' (tag: {nome_tag})")
    xpath = f"//{nome_tag}[contains(normalize-space(text()), '{texto}')]"
    try:
        elemento = WebDriverWait(driver, tempo_espera).until(
            EC.visibility_of_element_located((By.XPATH, xpath))
        )
        # Rola até o elemento para garantir visibilidade
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elemento)
        time.sleep(0.2)
        # Primeiro tenta o hover padrão
        ActionChains(driver).move_to_element(elemento).perform()
        logger.info(f"Mouse passado sobre o elemento '{texto}' via ActionChains.")
        time.sleep(0.2)
        # Verifica se um submenu ficou visível (heurística: procura por submenus abertos próximos)
        submenu_visivel = False
        try:
            submenu = elemento.find_element(By.XPATH, "./following-sibling::*[contains(@class, 'open') or contains(@class, 'show')]")
            if submenu.is_displayed():
                submenu_visivel = True
        except Exception:
            pass
        if submenu_visivel:
            logger.info(f"Submenu detectado após hover padrão.")
            return True
        # Se não funcionou, tenta disparar eventos via JavaScript
        logger.warning(f"Hover padrão não abriu submenu. Tentando disparar eventos JavaScript...")
        driver.execute_script("var evObj = document.createEvent('MouseEvents'); evObj.initEvent('mouseover', true, false); arguments[0].dispatchEvent(evObj);", elemento)
        driver.execute_script("var evObj = document.createEvent('MouseEvents'); evObj.initEvent('mouseenter', true, false); arguments[0].dispatchEvent(evObj);", elemento)
        time.sleep(0.3)
        # Verifica novamente se o submenu ficou visível
        try:
            submenu = elemento.find_element(By.XPATH, "./following-sibling::*[contains(@class, 'open') or contains(@class, 'show')]")
            if submenu.is_displayed():
                logger.info(f"Submenu detectado após eventos JS.")
                return True
        except Exception:
            pass
        logger.error(f"Não foi possível exibir o submenu para o elemento '{texto}'.")
        return False
    except Exception as erro:
        logger.error(f"Erro ao tentar passar mouse sobre elemento '{texto}': {erro}")
        return False

def selecionar_dropdown_por_label(driver, texto_label, valor):
    """
    Seleciona um valor em um dropdown (<select>) a partir do texto do label associado.
    Tenta primeiro selecionar pelo value, depois pelo texto visível se necessário.
    Parâmetros:
        driver: Instância do WebDriver.
        texto_label: Texto exato do label (ex: 'Ano').
        valor: Valor a ser selecionado no dropdown (ex: '2025').
    """
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import Select
    import time

    try:
        # Localiza o label pelo texto
        label = driver.find_element(By.XPATH, f"//label[normalize-space(text())='{texto_label}']")
        id_select = label.get_attribute("for")
        if not id_select:
            logger.error(f"Label '{texto_label}' não possui atributo 'for'.")
            return False
        # Localiza o select pelo id
        select_element = driver.find_element(By.ID, id_select)
        select = Select(select_element)
        try:
            # Tenta selecionar o valor desejado pelo value
            select.select_by_value(str(valor))
            logger.info(f"Valor '{valor}' selecionado no dropdown '{texto_label}' (por value).")
            return True
        except Exception as erro_selecao:
            logger.warning(f"Não foi possível selecionar por value: {erro_selecao}. Tentando por texto visível...")
            try:
                # Tenta selecionar pelo texto visível
                select.select_by_visible_text(str(valor))
                logger.info(f"Valor '{valor}' selecionado no dropdown '{texto_label}' (por texto visível).")
                return True
            except Exception as erro_texto:
                # Se não conseguir selecionar, lista as opções disponíveis
                opcoes_disponiveis = [opcao.get_attribute('value') for opcao in select.options]
                logger.error(f"Valor '{valor}' não encontrado no dropdown '{texto_label}'. Opções disponíveis: {opcoes_disponiveis}")
                return False
    except Exception as erro:
        # Erro ao localizar o label ou o select
        logger.error(f"Não foi possível localizar o dropdown associado ao label '{texto_label}': {erro}")
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
            logger.error(f"Label '{texto_label}' não possui atributo 'for'.")
            return []
        # Localiza o select pelo id
        select_element = driver.find_element(By.ID, id_select)
        select = Select(select_element)
        # Percorre todas as opções do dropdown
        for opcao in select.options:
            valor = opcao.get_attribute('value')
            texto = opcao.text
            lista_opcoes.append({'valor': valor, 'texto': texto})
        logger.info(f"Opções encontradas no dropdown '{texto_label}': {lista_opcoes}")
        return lista_opcoes
    except Exception as erro:
        # Erro ao localizar o label ou o select
        logger.error(f"Não foi possível listar opções do dropdown associado ao label '{texto_label}': {erro}")
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
                logger.info(f"Texto '{texto}' encontrado na página.")
                return True
        except Exception as erro:
            logger.error(f"Erro ao buscar texto na página: {erro}")
        time.sleep(0.5)
    logger.info(f"Texto '{texto}' NÃO encontrado na página após {tempo_espera} segundos.")
    return False

def selecionar_select2_por_label(driver, texto_label, valor, tempo_espera=10):
    """
    Seleciona um valor em um dropdown Select2 a partir do texto do label associado.
    Parâmetros:
        driver: Instância do WebDriver.
        texto_label: Texto exato do label (ex: 'Ano').
        valor: Valor/texto a ser selecionado no dropdown.
        tempo_espera: Tempo máximo de espera em segundos.
    Retorno:
        bool: True se o valor foi selecionado com sucesso, False caso contrário.
    """
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    try:
        # Localiza o label e o id do select associado
        label = driver.find_element(By.XPATH, f"//label[normalize-space(text())='{texto_label}']")
        id_select = label.get_attribute("for")
        if not id_select:
            logger.error(f"Label '{texto_label}' não possui atributo 'for'.")
            return False

        # Clica no container do Select2 para abrir as opções
        seletor_container = f"//span[@aria-labelledby='select2-{id_select}-container']"
        select2_container = driver.find_element(By.XPATH, seletor_container)
        select2_container.click()

        # Aguarda o campo de busca do Select2 aparecer
        campo_busca = WebDriverWait(driver, tempo_espera).until(
            EC.visibility_of_element_located((By.XPATH, "//input[contains(@class, 'select2-search__field')]"))
        )
        campo_busca.clear()
        campo_busca.send_keys(valor)

        # Aguarda e clica na opção desejada
        opcao = WebDriverWait(driver, tempo_espera).until(
            EC.element_to_be_clickable((By.XPATH, f"//li[contains(@class, 'select2-results__option') and contains(text(), '{valor}')]"))
        )
        opcao.click()
        logger.info(f"Valor '{valor}' selecionado no Select2 '{texto_label}'.")
        return True
    except Exception as erro:
        logger.error(f"Não foi possível selecionar '{valor}' no Select2 '{texto_label}': {erro}")
        return False

def verificar_texto_presente(driver, texto):
    """
    Verifica imediatamente se um determinado texto está presente no corpo da página.
    Retorna True se encontrar, False caso contrário.
    Parâmetros:
        driver: Instância do WebDriver.
        texto: Texto a ser procurado na página.
    """
    try:
        corpo = driver.find_element(By.TAG_NAME, 'body').text
        if texto.lower() in corpo.lower():
            logger.info(f"Texto '{texto}' encontrado na página.")
            return True
        else:
            logger.info(f"Texto '{texto}' NÃO encontrado na página.")
            return False
    except Exception as erro:
        logger.error(f"Erro ao buscar texto na página: {erro}")
        return False

def verificar_texto_presente_timeout(driver, texto, tempo_espera=10):
    """
    Verifica se um texto está presente na página dentro de um tempo máximo (timeout).
    Retorna True se encontrar, False se não encontrar no tempo estipulado.
    Parâmetros:
        driver: Instância do WebDriver.
        texto: Texto a ser procurado na página.
        tempo_espera: Tempo máximo de espera em segundos (padrão: 10).
    """
    import time
    tempo_inicial = time.time()
    while time.time() - tempo_inicial < tempo_espera:
        try:
            corpo = driver.find_element(By.TAG_NAME, 'body').text
            if texto.lower() in corpo.lower():
                logger.info(f"Texto '{texto}' encontrado na página.")
                return True
        except Exception as erro:
            logger.error(f"Erro ao buscar texto na página: {erro}")
        time.sleep(0.5)
    logger.info(f"Texto '{texto}' NÃO encontrado na página após {tempo_espera} segundos.")
    return False

def aguardar_textos_na_pagina(driver, lista_textos, tempo_espera=30):
    """
    Aguarda até que um dos textos especificados apareça na página ou até o tempo limite.
    Retorna o texto encontrado ou None se nenhum for encontrado no tempo.
    Parâmetros:
        driver: Instância do WebDriver.
        lista_textos: Lista de textos a serem procurados.
        tempo_espera: Tempo máximo de espera em segundos (padrão: 30).
    """
    import time
    tempo_inicial = time.time()
    while time.time() - tempo_inicial < tempo_espera:
        try:
            corpo = driver.find_element(By.TAG_NAME, 'body').text.lower()
            for texto in lista_textos:
                if texto.lower() in corpo:
                    logger.info(f"Texto '{texto}' encontrado na página.")
                    return texto
        except Exception as erro:
            logger.error(f"Erro ao buscar textos na página: {erro}")
        time.sleep(0.5)
    logger.info(f"Nenhum dos textos {lista_textos} encontrado após {tempo_espera} segundos.")
    return None

def preencher_campo_por_label(driver, texto_label, valor, tipo_input='text', tempo_espera=10):
    """
    Preenche um campo de input associado a um label com o texto especificado.
    Procura o label pelo texto, localiza o input relacionado (mesmo bloco visual) e preenche o valor.
    Parâmetros:
        driver: Instância do WebDriver.
        texto_label: Texto exato do label (ex: 'Usuário da Rede', 'Senha').
        valor: Valor a ser preenchido no campo.
        tipo_input: 'text' ou 'password' (opcional, para restringir o tipo de input).
        tempo_espera: Tempo máximo de espera em segundos.
    Retorno:
        bool: True se o campo foi preenchido com sucesso, False caso contrário.
    """
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    import time

    try:
        # Localiza o label pelo texto
        label_xpath = f"//span[contains(@class, 'nomeCampoObrigatorio') and normalize-space(text())='{texto_label}']"
        label_element = WebDriverWait(driver, tempo_espera).until(
            EC.visibility_of_element_located((By.XPATH, label_xpath))
        )
        # Sobe para o container do label e desce para o input
        box_div = label_element.find_element(By.XPATH, "../../..")
        # Busca o input dentro do mesmo bloco visual
        if tipo_input == 'password':
            input_element = box_div.find_element(By.XPATH, 
                ".//input[@type='password']")
        else:
            input_element = box_div.find_element(By.XPATH, 
                ".//input[@type='text' or not(@type)]")
        input_element.clear()
        input_element.send_keys(valor)
        logger.info(f"Campo '{texto_label}' preenchido com sucesso.")
        return True
    except Exception as erro:
        logger.error(f"Não foi possível preencher o campo '{texto_label}': {erro}")
        return False

def selecionar_opcoes_select_por_prefixo(driver, id_select, lista_prefixos):
    """
    Seleciona todas as opções de um <select multiple> cujo texto começa com qualquer um dos prefixos informados.
    Parâmetros:
        driver: Instância do WebDriver.
        id_select: ID do elemento <select>.
        lista_prefixos: Lista de strings com os prefixos desejados.
    Retorna:
        Tupla (lista_encontradas, lista_nao_encontradas) onde:
        - lista_encontradas: Lista de prefixos que foram encontrados e selecionados
        - lista_nao_encontradas: Lista de prefixos que não foram encontrados
    """
    from selenium.webdriver.support.ui import Select
    from selenium.webdriver.common.by import By
    # Localiza o elemento select pelo ID
    select_element = driver.find_element(By.ID, id_select)
    select = Select(select_element)
    total_selecionados = 0
    lista_encontradas = []
    lista_nao_encontradas = lista_prefixos.copy()
    
    for option in select.options:
        for prefixo in lista_prefixos:
            if option.text.startswith(prefixo):
                option.click()  # Seleciona a opção
                total_selecionados += 1
                if prefixo not in lista_encontradas:
                    lista_encontradas.append(prefixo)
                if prefixo in lista_nao_encontradas:
                    lista_nao_encontradas.remove(prefixo)
                break  # Não precisa checar outros prefixos para esta opção
    
    print(f"[INFO] Total de opções selecionadas no select '{id_select}': {total_selecionados}")
    return lista_encontradas, lista_nao_encontradas

