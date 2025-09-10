import time
import colorama
from automacoes import util_selenium, utils
from selenium.webdriver.common.by import By

from automacoes.pnadC import liberarCodificacao

teste = False  # Define se está em modo de teste (True) ou produção (False)

# Inicializa o colorama para suporte a cores no terminal
colorama.init(autoreset=True)

def executar(texto_input=None, driver_in=None, fechar_driver=True):
    """
    Executa a automação para associar entrevistas. O parâmetro texto_input é opcional;
    se não for fornecido, será solicitado ao usuário.
    """
    global driver
    print("Iniciando automação para liberar codificação...")
    driver = driver_in

    if not driver:
        driver = util_selenium.inicializar_webdriver_com_perfil()        

    lista_entradas = solicitar_lista_setores_domicilios_siape(texto_input)
    lista_entradas_processada = processar_lista_siape_setores(lista_entradas)
    if not lista_entradas:
        print("Nenhuma entrada válida fornecida. Encerrando a automação.")
        return

    utils.solicitar_credenciais("Portalweb")

    iniciar_sequencia_portal(lista_entradas_processada)

    # Terminou:
    if not fechar_driver:
        print("Automação concluída. O WebDriver permanecerá aberto para próxima execução.")
        return driver
    else:
        print("Automação concluída. O WebDriver foi recebido por parâmetro e não será fechado aqui.")
        driver.quit()

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
    
    # Lista para coletar todas as unidades não encontradas
    todas_unidades_nao_encontradas = []
    
    # Percorre cada SIAPE e suas respectivas unidades de trabalho (setor+domicílio)
    for siape, lista_unidades in lista_entradas_processada.items():
        time.sleep(2)
        # Preenche o campo de matrícula (SIAPE)
        try:
            util_selenium.preencher_campo(driver, (By.ID, "cb_login"), siape)
        except Exception as erro:
            print(f"{colorama.Fore.RED}❌ Erro ao preencher SIAPE {siape}: {erro}. Passando para o próximo.{colorama.Style.RESET_ALL}")
            continue
        
        # Clica no botão de submit após preencher a matrícula
        util_selenium.clicar_elemento_com_fallback(driver, (By.ID, "btnSubmit"))
        time.sleep(2)
        # Clica no botão para associar unidade de trabalho
        util_selenium.clicar_elemento_com_fallback(driver, (By.CSS_SELECTOR, '[data-original-title="Associar Unidade de Trabalho"]'))
        # Seleciona as unidades de trabalho pelo prefixo (setor+domicílio)
        time.sleep(2)
        encontradas, nao_encontradas = util_selenium.selecionar_opcoes_select_por_prefixo(driver, "unidades_disponiveis", lista_unidades)
        
        # Adiciona as unidades não encontradas à lista global com o SIAPE correspondente
        if nao_encontradas:
            for unidade in nao_encontradas:
                todas_unidades_nao_encontradas.append(f"SIAPE {siape}: {unidade}")
        
        time.sleep(1)
        # Clica no botão para associar unidade
        util_selenium.clicar_elemento_com_fallback(driver, (By.ID, "btn_associar_unidade"))
        time.sleep(1)
        # Verifica se está em modo de teste ou produção para decidir qual botão clicar
        if teste:
            # Em modo de teste, cancela a associação
            util_selenium.clicar_elemento_com_fallback(driver, (By.ID, "btn_cancelar_modal_unidade"))
        else:
            # Em produção, salva a associação
            util_selenium.clicar_elemento_com_fallback(driver, (By.ID, "btn_salvar_modal_unidade"))
        # Comentário: repete o processo para cada SIAPE e suas unidades
        time.sleep(1)
    
    # Exibe as unidades não encontradas em vermelho ao final
    if todas_unidades_nao_encontradas:
        print(f"\n{colorama.Fore.RED}⚠️  UNIDADES NÃO ENCONTRADAS:{colorama.Style.RESET_ALL}")
        for unidade_nao_encontrada in todas_unidades_nao_encontradas:
            print(f"{colorama.Fore.RED}❌ {unidade_nao_encontrada}{colorama.Style.RESET_ALL}")
        print(f"{colorama.Fore.RED}Total de unidades não encontradas: {len(todas_unidades_nao_encontradas)}{colorama.Style.RESET_ALL}\n")
    else:
        print(f"{colorama.Fore.GREEN}✅ Todas as unidades foram encontradas e associadas com sucesso!{colorama.Style.RESET_ALL}\n")
    
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
    
    
def solicitar_lista_setores_domicilios_siape(texto=None):
    """
    Solicita ao usuário uma lista de setores, domicílios e SIAPE do entrevistador usando interface gráfica centralizada.
    Aceita dois formatos de entrada por linha:
    1. Formato antigo: <setor> <domicilio> <siape>
    2. Novo formato: <setor> <domicilio1> <domicilio2> ... <domicilioN> <siape>
    Retorna uma lista de dicionários com as chaves: numero_setor, numero_domicilio, siape_entrevistador.
    """
    if not texto:
        from automacoes.caixas_dialogo import solicitar_texto_multilinha, exibir_caixa_dialogo
        mensagem = (
            "Cole a lista de setores, domicílios e SIAPE (numeroSetor [domicilios...] siapeEntrevistador),\n"
            "separados por espaço ou tabulação, uma linha por registro.\n\nExemplo:\n410730605000009 1 1234567\n410730605000009 1 2 3 1234567\n412625605000054 2 7654321"
        )
        texto = solicitar_texto_multilinha(
            titulo="Setores, Domicílios e SIAPE",
            mensagem=mensagem,
            texto_exemplo="410730605000009 1 1234567\n410730605000009 1 2 3 1234567\n412625605000054 2 7654321"
        )
    lista_entradas = []
    if texto:
        linhas = texto.splitlines()
        for linha in linhas:
            if not linha.strip():
                continue
            partes = linha.strip().replace("\t", " ").split()
            # Precisa ter pelo menos 3 partes: setor, pelo menos 1 domicilio, siape
            if len(partes) < 3:
                exibir_caixa_dialogo("Erro de Formato", f"Linha inválida: {linha}\nUse o formato: numeroSetor [domicilios...] siapeEntrevistador", tipo="erro")
                return solicitar_lista_setores_domicilios_siape()
            numero_setor = partes[0]
            siape_entrevistador = partes[-1]
            lista_domicilios = partes[1:-1]
            # Para cada domicílio informado, cria uma entrada
            for numero_domicilio in lista_domicilios:
                lista_entradas.append({
                    'numero_setor': numero_setor.strip(),
                    'numero_domicilio': numero_domicilio.strip(),
                    'siape_entrevistador': siape_entrevistador.strip()
                })
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

