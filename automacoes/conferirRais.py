import time
from automacoes import accesoSistemas, util_selenium, utils
from automacoes.caixas_dialogo import solicitar_texto_multilinha
from automacoes.util_cnpj import processar_lista_raiz_cnpjs
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

def iniciar_sequencia(cnpjs):
    driver = util_selenium.inicializar_webdriver_com_perfil()
    accesoSistemas.abrir_portalWeb(driver)
    util_selenium.clicar_elemento_por_texto_com_fallback(driver, "Pesquisas Econômicas", tempo_espera=180)
    util_selenium.clicar_elemento_por_texto_com_fallback(driver, "CEMPRE Web")
    driver.switch_to.window(driver.window_handles[-1])
    # Aguarda até 20 segundos pelo elemento de menu 'Fonte Externa' para saber se está logado
    elemento = util_selenium.aguardar_elemento_por_texto(
        driver, "LOGIN", tempo_espera=5
    )
    driver.switch_to.window(driver.window_handles[-1])

    if elemento:        
        print("Necessidade de fazer login detectado.")
        # Acessa diretamente a tela de login sem clicar no botão LOGIN
        util_selenium.clicar_elemento_por_texto_com_fallback(driver, "LOGIN", tempo_espera=15)
        time.sleep(1)  # Aguarda a tela de login carregar
        (login, senha) = utils.solicitar_credenciais("Portalweb")
        util_selenium.preencher_campo(driver, (By.ID, "UserName"), login)
        util_selenium.preencher_campo(driver, (By.ID, "Password"), senha)
        util_selenium.clicar_elemento_com_fallback(driver, (By.ID, "login"))
        # Aguarda o menu aparecer após login
        time.sleep(2)
    else:
        print("Login já realizado ou não necessário.")
    
    url = "https://portalweb.ibge.gov.br/f5-w-68747470733a2f2f773363656d7072652e696267652e676f762e6272$$/f5-h-$$/ConsultarRaisOnline"    
    driver.get(url)
    util_selenium.aguardar_elemento_por_texto(driver, "Raiz CNPJ", tempo_espera=20)

    # Seleciona os 5 primeiros anos no campo múltiplo 'Ano'
    try:
        select_ano = Select(driver.find_element(By.ID, "Ano"))
        opcoes = select_ano.options
        # Seleciona os 5 primeiros anos disponíveis
        for option in opcoes[:5]:
            select_ano.select_by_value(option.get_attribute("value"))
    except Exception as e:
        print(f"Erro ao selecionar anos: {e}")

    # Variável para salvar os dados:
    dadosColetados = []
    for cnpj in cnpjs:
        # Preencher o campo de Raiz CNPJ
        try:            
            util_selenium.preencher_campo(driver, (By.ID, "Raiz"), cnpj)
            # Aqui você pode adicionar lógica para clicar em consultar, aguardar resultado, etc.
        except Exception as e:
            print(f"Erro ao preencher Raiz CNPJ {cnpj}: {e}")

        # apertar submit:
        try:
            util_selenium.clicar_elemento_com_fallback(driver, (By.NAME, "ButtonSubmit"))
            time.sleep(5)  # Aguarda a resposta do servidor
            util_selenium.aguardar_elemento_por_texto(driver, "Anterior", tempo_espera=40)
            # Aguarda algum texto ou elemento que indique o resultado da pesquisa, se necessário
            # util_selenium.aguardar_elemento_por_texto(driver, "Resultado", tempo_espera=20)
        except Exception as e:
            print(f"Erro ao clicar em Pesquisar para Raiz CNPJ {cnpj}: {e}")
        
        # Após aguardar o resultado, processa cada aba de ano
        try:
            abas_ano = driver.find_elements(By.CSS_SELECTOR, '#lsAnos .nav-link')
            dados_anos = {}
            for idx, aba in enumerate(abas_ano):
                ano = aba.get_attribute('data-ano')
                if idx == 0:
                    maior_po, maior_salario = processar_aba_ano(driver, ano)
                    dados_anos[ano] = {'PO': maior_po, 'Salario': maior_salario}                    
                else:
                    aba.click()
                    time.sleep(1)
                # Processa a aba do ano
                maior_po, maior_salario = processar_aba_ano(driver, ano)
                dados_anos[ano] = {'PO': maior_po, 'Salario': maior_salario}
            dadosColetados.append(dados_anos)
        except Exception as e:
            print(f"Erro ao processar abas de ano: {e}")


    print("Dados coletados:", dadosColetados)
    return

# Função para solicitar lista de raízes de CNPJs ao usuário e retornar lista limpa
# Comentário: Centraliza a solicitação e processamento das raízes dos CNPJs, garantindo que a entrada seja tratada e validada.
def solicitar_lista_cnpjs():
    """
    Solicita ao usuário uma lista de CNPJs (formatados ou não) e retorna uma lista apenas com as raízes (8 dígitos).
    Retorna:
        list: Lista de raízes de CNPJs (8 dígitos cada).
    """
    texto = solicitar_texto_multilinha(
        titulo="Lista de CNPJs",
        mensagem="Informe os CNPJs (um por linha, separados por vírgula ou ponto e vírgula):"
    )
    if not texto:
        return []
    lista_raizes = processar_lista_raiz_cnpjs(texto)
    return lista_raizes

def processar_aba_ano(driver, ano):
    """
    Processa a aba do ano informada, coletando o maior valor de PO e Salário Total da tabela.
    Parâmetros:
        driver: Instância do Selenium WebDriver.
        ano (str|int): Ano da aba a ser processada.
    Retorna:
        tuple: (maior_po, maior_salario) encontrados na tabela da aba.
    """
    from selenium.webdriver.common.by import By
    import re
    maior_po = 0
    maior_salario = 0.0
    try:
        tabela = driver.find_element(By.ID, f"grid-{ano}")
        linhas = tabela.find_elements(By.CSS_SELECTOR, "tbody tr")
        if not linhas:
            # Caso não haja linhas na tabela, retorna 'sem dados'
            return "sem dados", "sem dados"
        for linha in linhas:
            colunas = linha.find_elements(By.TAG_NAME, "td")
            if len(colunas) < 14:
                continue
            # Qtde PO(3112) está na coluna 13 (índice 12), Salário Total na 14 (índice 13)
            texto_po = colunas[12].text.strip().replace('.', '').replace(',', '')
            texto_salario = colunas[13].text.strip().replace('.', '').replace(',', '').replace(' ', '')
            try:
                po = int(re.sub(r'\D', '', texto_po)) if texto_po else 0
            except Exception:
                po = 0
            try:
                salario = float(re.sub(r'\D', '', texto_salario)) if texto_salario else 0.0
            except Exception:
                salario = 0.0
            if po > maior_po:
                maior_po = po
            if salario > maior_salario:
                maior_salario = salario
    except Exception as e:
        print(f"Erro ao processar tabela do ano {ano}: {e}")
    return maior_po, maior_salario

def executar():
    cnpjs = solicitar_lista_cnpjs()
    if not cnpjs:
        print("Nenhum CNPJ fornecido. Encerrando a automação.")
        return
    print("CNPJs fornecidos:", cnpjs)
    print(f"Processando {len(cnpjs)} CNPJs...")
    
    iniciar_sequencia(cnpjs)