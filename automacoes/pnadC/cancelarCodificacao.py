# 1) Cancelar codificação
# 2) Passar a entrevista

import time
from selenium.webdriver.common.by import By  # Importa o By para localizar elementos no Selenium
from automacoes import config_municipio_estado, util_selenium
from automacoes.pnadC import liberarCodificacao
from selenium.webdriver.common.keys import Keys

driver = None

def sequencia_portal(mes, ano):
    liberarCodificacao.abrir_pnad_c(driver)
    urlCancelarCodificacao = "https://portalweb.ibge.gov.br/f5-w-68747470733a2f2f773373696763706e6164632e696267652e676f762e6272$$/f5-h-$$/CancelarLiberacaoParaCodificacao"
    driver.get(urlCancelarCodificacao)
    # tem que aguardar o carregamento: Aguardar aparecer o estado e município configurados
    # util_selenium.aguardar_elemento_por_texto(driver, config_municipio_estado.estado, tempo_espera=30)
    util_selenium.aguardar_elemento_por_texto(driver, "TODOS", tempo_espera=30)
    util_selenium.selecionar_dropdown_por_label(driver, "Ano", ano)
    time.sleep(2)
    util_selenium.selecionar_dropdown_por_label(driver, "Mes", mes)
    time.sleep(2)
    for entrada in lista_entradas:
        # Seleciona o setor e o domicílio usando a função específica para Select2
        util_selenium.selecionar_select2_por_label(driver, "Controle", entrada['numero_setor'])
        time.sleep(2)        
        # Clica no botão "Filtrar" para aplicar os filtros
        util_selenium.clicar_elemento_por_texto_com_fallback(driver, "Filtrar")
        time.sleep(1)
        # Clicar no "Liberado" correspondente:
        clicar_liberado_por_numero_domicilio(driver, entrada['numero_domicilio'])
        time.sleep(2)
        util_selenium.clicar_elemento_com_fallback(driver, (By.ID, "btnSubmit"))
        # Aparece uma mensagem de confirmação após o carregamento, clicar em "OK"  ou apertar ESC                                  
        time.sleep(5)            
        # Em vez de clicar no botão, envia a tecla ESC para fechar a caixa de diálogo        
        driver.switch_to.active_element.send_keys(Keys.ESCAPE)
        time.sleep(1)
        util_selenium.clicar_elemento_com_fallback(driver, (By.ID, "btnMenuFiltro"))
        time.sleep(1)                        

    
def solicitar_lista_setores_domicilios(texto=None):
    """
    Solicita ao usuário uma lista de setores e domicílios usando interface gráfica centralizada.
    Retorna uma lista de dicionários com as chaves: numero_setor, numero_domicilio.
    """
    if not texto:
        from automacoes.caixas_dialogo import solicitar_texto_multilinha, exibir_caixa_dialogo
        mensagem = (
            "Cole a lista de setores e domicílios (numeroSetor numeroDomicilio),\n"
            "separados por espaço ou tabulação, uma linha por registro:"
        )
        texto = solicitar_texto_multilinha(
            titulo="Setores e Domicílios",
            mensagem=mensagem,
            texto_exemplo="123456789012345 1\n123456789012346 2"
        )
    lista_entradas = []
    if texto:
        linhas = texto.splitlines()
        for linha in linhas:
            if not linha.strip():
                continue
            partes = linha.strip().replace("\t", " ").split()
            if len(partes) != 2:
                exibir_caixa_dialogo("Erro de Formato", f"Linha inválida: {linha}\nUse o formato: numeroSetor numeroDomicilio", tipo="erro")
                return solicitar_lista_setores_domicilios()
            lista_entradas.append({
                'numero_setor': partes[0].strip(),
                'numero_domicilio': partes[1].strip()
            })
    return lista_entradas

def executar(mes, ano, texto_input, driver_in=None, fechar_driver=True):
    global driver, lista_entradas  
    print("Iniciando automação para Cancelar Liberção Codificação...")

    # Solicita o mês e o ano antes de iniciar o WebDriver
    if not mes or not ano:
        mes, ano = liberarCodificacao.solicitar_mes_ano()    
    if not mes or not ano:
        return
    # Solicita a lista de setores e domicílios
    lista_entradas = solicitar_lista_setores_domicilios(texto_input)
    
    # Remove itens duplicados mantendo a ordem original
    lista_entradas_unicas = []
    entradas_vistas = set()
    for entrada in lista_entradas:
        # Cria uma chave única baseada no setor e domicílio
        chave_entrada = (entrada['numero_setor'], entrada['numero_domicilio'])
        if chave_entrada not in entradas_vistas:
            entradas_vistas.add(chave_entrada)
            lista_entradas_unicas.append(entrada)
    
    # Atualiza a lista com os itens únicos
    lista_entradas = lista_entradas_unicas
    
    # Exibe informação sobre duplicatas removidas
    total_original = len(lista_entradas) + len(entradas_vistas) - len(lista_entradas_unicas)
    if total_original > len(lista_entradas):
        duplicatas_removidas = total_original - len(lista_entradas)
        print(f"[INFO] {duplicatas_removidas} entrada(s) duplicada(s) removida(s). Total de entradas únicas: {len(lista_entradas)}")

    driver = driver_in
    if not driver:
        driver = util_selenium.inicializar_webdriver_com_perfil()
    sequencia_portal(mes, ano)

    # Terminou:
    if not fechar_driver:
        print("Automação concluída. O WebDriver permanecerá aberto para próxima execução.")
        return driver
    else:
        print("Automação concluída. Fechando o WebDriver.")
        driver.quit()        

def clicar_liberado_por_numero_domicilio(driver, numero_domicilio, tempo_espera=10):
    """
    Clica no botão "Liberado" correspondente ao número do domicílio informado.
    Parâmetros:
        driver: Instância do WebDriver.
        numero_domicilio: Número do domicílio (str ou int).
        tempo_espera: Tempo máximo de espera em segundos.
    Retorna True se o clique foi realizado, False caso contrário.
    """
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    import time
    try:
        # Monta o XPath para encontrar o label do domicílio
        xpath_label = f"//label[contains(text(), 'Domicílio - {numero_domicilio}') or contains(text(), 'Domicílio - {int(numero_domicilio)}')]"
        label = WebDriverWait(driver, tempo_espera).until(
            EC.visibility_of_element_located((By.XPATH, xpath_label))
        )
        # Sobe para o elemento pai (div.row), depois desce para o botão "Liberado"
        div_row = label.find_element(By.XPATH, "../../..")
        # Procura o label do botão "Liberado" dentro do grupo de toggle
        label_liberado = div_row.find_element(By.XPATH, ".//label[contains(@class, 'toggle-off') and contains(text(), 'Liberado')]")
        driver.execute_script("arguments[0].scrollIntoView(true);", label_liberado)
        time.sleep(0.2)
        label_liberado.click()
        return True
    except Exception as erro:
        # Se não encontrar o label do domicílio, apenas exibe mensagem informativa
        if "TimeoutException" in str(type(erro)):
            print(f"[INFO] Label do domicílio {numero_domicilio} não encontrado na página.")
            return True
        else:
            print(f"[ERRO] Não foi possível clicar no botão 'Liberado' do domicílio {numero_domicilio}: {erro}")
        return False