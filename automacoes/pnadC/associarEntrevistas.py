import time
from automacoes import util_selenium, utils
from selenium.webdriver.common.by import By

from automacoes.pnadC import liberarCodificacao


def executar():
    global driver  
    print("Iniciando automação para liberar codificação...")
            
    lista_entradas = solicitar_lista_setores_domicilios_siape()
    lista_entradas_processada = processar_lista_siape_setores(lista_entradas)    

    utils.solicitar_credenciais("Portalweb")
    driver = util_selenium.inicializar_webdriver_com_perfil()

    iniciar_sequencia_portal(lista_entradas_processada)

    # Terminou:
    driver.quit()
    print("Automação concluída.")

def iniciar_sequencia_portal(lista_entradas_processada):
    liberarCodificacao.abrir_pnad_c(driver)

    url = "https://portalweb.ibge.gov.br/f5-w-68747470733a2f2f77337365727669636f736967632e696267652e676f762e6272$$/usuario/?codigoPesquisa=PNADC"    
    driver.get(url)
    # Estamos na tela de login?    
    texto_tela = util_selenium.aguardar_textos_na_pagina(driver, ["Login", "Usuário"], tempo_espera=20)
    
    if texto_tela=="Login":
        (login, senha) = utils.solicitar_credenciais("Portalweb")
        util_selenium.preencher_campo(driver, (By.ID, "UserName"), login)    
        util_selenium.preencher_campo(driver, (By.ID, "Password"), senha)    
        util_selenium.clicar_elemento_com_fallback(driver, (By.ID, "login"))
        time.sleep(2)
    
    # Percorre cada SIAPE e suas respectivas unidades de trabalho (setor+domicílio)
    for siape, lista_unidades in lista_entradas_processada.items():
        time.sleep(1)
        # Preenche o campo de matrícula (SIAPE)
        util_selenium.preencher_campo(driver, (By.ID, "cb_login"), siape)        
        # Clica no botão de submit após preencher a matrícula
        util_selenium.clicar_elemento_com_fallback(driver, (By.ID, "btnSubmit"))
        time.sleep(2)
        # Clica no botão para associar unidade de trabalho
        util_selenium.clicar_elemento_com_fallback(driver, (By.CSS_SELECTOR, '[data-original-title="Associar Unidade de Trabalho"]'))
        # Seleciona as unidades de trabalho pelo prefixo (setor+domicílio)
        time.sleep(2)
        util_selenium.selecionar_opcoes_select_por_prefixo(driver, "unidades_disponiveis", lista_unidades)
        time.sleep(1)
        # Clica no botão para associar unidade
        util_selenium.clicar_elemento_com_fallback(driver, (By.ID, "btn_associar_unidade"))
        time.sleep(1)
        # Para produção, descomente a linha abaixo e comente a de cancelar
        util_selenium.clicar_elemento_com_fallback(driver, (By.ID, "btn_salvar_modal_unidade"))
        # Para teste, cancela a associação
        # util_selenium.clicar_elemento_com_fallback(driver, (By.ID, "btn_cancelar_modal_unidade"))
        # Comentário: repete o processo para cada SIAPE e suas unidades
        time.sleep(1)
    # Exemplo testado:
    '''
    util_selenium.preencher_campo(driver, (By.ID, "cb_login"), "1202254")
    # Clica no botão de submit após preencher a matrícula
    util_selenium.clicar_elemento_com_fallback(driver, (By.ID, "btnSubmit"))
    util_selenium.clicar_elemento_com_fallback(driver, (By.CSS_SELECTOR, '[data-original-title="Associar Unidade de Trabalho"]'))
    util_selenium.selecionar_opcoes_select_por_prefixo(driver, "unidades_disponiveis", ["41141040500005201", "41141040500005202", "41141040500005203"])
    util_selenium.clicar_elemento_com_fallback(driver, (By.ID, "btn_associar_unidade"))
    # util_selenium.clicar_elemento_com_fallback(driver, (By.ID, "btn_salvar_modal_unidade")) 
    # para teste sem associar:
    util_selenium.clicar_elemento_com_fallback(driver, (By.ID, "btn_cancelar_modal_unidade"))
    '''
    
    
def solicitar_lista_setores_domicilios_siape():
    """
    Solicita ao usuário uma lista de setores, domicílios e SIAPE do entrevistador (separados por espaço, tab ou múltiplos espaços),
    uma linha por registro. Finaliza com linha vazia.
    Retorna uma lista de dicionários com as chaves: numero_setor, numero_domicilio, siape_entrevistador.
    Exemplo de entrada válida:
        410730605000009 1 1234567
        410730605000009 2 1234567
        412625605000054 2 7654321
    """
    print("Cole a lista de setores, domicílios e SIAPE (numeroSetor numeroDomicilio siapeEntrevistador), separados por espaço ou tabulação, uma linha por registro. Finalize com uma linha vazia:")    
    print("\nExemplo de entrada:")
    print("="*50)
    print("  410730605000009 1 1234567\n  410730605000009 2 1234567\n  412625605000054 2 7654321")
    print("="*50)
    lista_entradas = []
    while True:
        linha = input()
        if not linha.strip():
            break
        try:
            partes = linha.strip().split()
            if len(partes) != 3:
                raise ValueError("A linha deve conter exatamente 3 campos: setor, domicílio e SIAPE.")
            numero_setor, numero_domicilio, siape_entrevistador = partes
            lista_entradas.append({
                'numero_setor': numero_setor.strip(),
                'numero_domicilio': numero_domicilio.strip(),
                'siape_entrevistador': siape_entrevistador.strip()
            })
        except Exception:
            print(f"[ERRO] Linha inválida: {linha}. Use o formato numeroSetor numeroDomicilio siapeEntrevistador.")
    return lista_entradas

def processar_lista_siape_setores(lista_entradas):
    """
    Processa a lista de entradas para agrupar os setores+domicílio por SIAPE.
    Cada domicílio é formatado com dois dígitos (zero à esquerda se necessário).
    Retorna um dicionário: {siape: [setor+domicílio, ...], ...}
    """
    # Dicionário para armazenar o resultado
    dicionario_siape_setores = {}

    for entrada in lista_entradas:
        # Extrai os campos da entrada
        numero_setor = entrada['numero_setor']
        numero_domicilio = entrada['numero_domicilio'].zfill(2)  # Garante 2 dígitos
        siape_entrevistador = entrada['siape_entrevistador']

        # Concatena setor e domicílio
        setor_domicilio = f"{numero_setor}{numero_domicilio}"

        # Adiciona ao dicionário agrupando por SIAPE
        if siape_entrevistador not in dicionario_siape_setores:
            dicionario_siape_setores[siape_entrevistador] = []
        dicionario_siape_setores[siape_entrevistador].append(setor_domicilio)

    return dicionario_siape_setores

