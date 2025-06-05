import time
from automacoes import caixas_dialogo, util_selenium, utils
from selenium.webdriver.common.by import By
from automacoes.config_municipio_estado import config_municipio_estado
from automacoes.log_util import obter_logger
from automacoes.accesoSistemas import aguardar_distribuicao_nao_zero, abrir_pnad_c

logger = obter_logger(__name__)

driver = None  # Variável global para armazenar o WebDriver

def solicitar_mes_ano():
    """
    Solicita ao usuário o mês e o ano usando interface gráfica intuitiva.
    Retorna:
        tuple: (mes, ano) como strings, ou (None, None) se a entrada for inválida.
    """
    from automacoes.pnadC.solicitar_mes_ano_interface import solicitar_mes_ano_interface
    return solicitar_mes_ano_interface()
def clicar_todos_botoes_bloqueado(driver):
    """
    Clica em todos os botões de 'Bloqueado' na página para liberar a codificação dos domicílios.
    Busca todos os elementos <label> com a classe 'btn-danger' e texto 'Bloqueado' e clica neles.
    Parâmetros:
        driver: Instância do WebDriver.
    Retorna:
        int: Quantidade de botões 'Bloqueado' clicados com sucesso.
    """
    from selenium.webdriver.common.by import By
    import time
    # Busca todos os elementos <label> com a classe 'btn-danger' e texto 'Bloqueado'
    botoes_bloqueado = driver.find_elements(By.XPATH, "//label[contains(@class, 'btn-danger') and contains(text(), 'Bloqueado')]")
    print(f"[INFO] Encontrados {len(botoes_bloqueado)} botões 'Bloqueado' para liberar.")
    total_clicados = 0  # Contador de botões clicados
    for indice, botao in enumerate(botoes_bloqueado, start=1):
        try:
            # Rola até o botão para garantir visibilidade
            driver.execute_script("arguments[0].scrollIntoView(true);", botao)
            botao.click()
            print(f"[SUCESSO] Botão 'Bloqueado' {indice} liberado com sucesso.")
            total_clicados += 1  # Incrementa o contador
            # Pequena pausa para evitar problemas de sincronização
            time.sleep(0.5)
        except Exception as erro:
            print(f"[ERRO] Não foi possível clicar no botão 'Bloqueado' {indice}: {erro}")
    return total_clicados  # Retorna o total de botões clicados

def sequencia_portal(mes, ano):
    global driver

    # Será se este endereço muda com o tempo?
    urlLiberarCodificacao = "https://portalweb.ibge.gov.br/f5-w-68747470733a2f2f773373696763706e6164632e696267652e676f762e6272$$/f5-h-$$/LiberarParaCodificacao"    
    
    # Acessa o portal web e navega até PNAD Contínua
    abrir_pnad_c(driver)

    # Vamos tentr acessar a URL diretamente agora:
    driver.get(urlLiberarCodificacao)
    

    # tem que aguardar o carregamento: Aguardar aparecer o estado e município configurados
    # util_selenium.aguardar_elemento_por_texto(driver, config_municipio_estado.estado, tempo_espera=30)
    util_selenium.aguardar_elemento_por_texto(driver, "TODOS", tempo_espera=30)

    util_selenium.selecionar_dropdown_por_label(driver, "Ano", ano)
    time.sleep(2)
    util_selenium.selecionar_dropdown_por_label(driver, "Mes", mes)
    time.sleep(2)    
    util_selenium.selecionar_dropdown_por_label(driver, "Agência", config_municipio_estado.municipio.split(" - ")[0])
    time.sleep(2)

    listaSetores = util_selenium.listar_opcoes_dropdown_por_label(driver, "Controle")
    # o primeiro elemento é o "Selecione", vamos remover:
    listaSetores = listaSetores[1:]  # Remove o primeiro elemento
    # precisamos apenas dos textos, e não dos valores:
    listaSetores = [setor['texto'] for setor in listaSetores]
    print(f"Setores disponíveis: {listaSetores}")

    total_liberado = 0  # Contador total de entrevistas liberadas

    # Agora para cada setor precisamos "liberar" a codificação:
    for setor in listaSetores:        
        util_selenium.selecionar_dropdown_por_label(driver, "Controle", setor)
        util_selenium.clicar_elemento_por_texto_com_fallback(driver, "Filtrar")
        # Acho que uns 2 segundos é suficiente para carregar:
        time.sleep(2)
        # caso aparecer Nenhum registro encontrado:
        if (util_selenium.verificar_texto_presente_na_pagina(driver, "Nenhum registro encontrado!")):
            print(f"[INFO] Nenhum para liberar para o setor: {setor}")
            util_selenium.clicar_elemento_com_fallback(driver, (By.ID, "btnMenuFiltro"))
            time.sleep(1)
            continue
        else:            
            # Função para clicar em todos os botões "Bloqueado" e liberar os domicílios
            liberados_setor = clicar_todos_botoes_bloqueado(driver)
            total_liberado += liberados_setor  # Soma ao total geral
            # Após liberar, clicar no botão de submit para efetivar as liberações
            util_selenium.clicar_elemento_com_fallback(driver, (By.ID, "btnSubmit"))
            # Aparece uma mensagem de confirmação após o carregamento, clicar em "OK"  ou apertar ESC                                  
            time.sleep(5)            
            # Em vez de clicar no botão, envia a tecla ESC para fechar a caixa de diálogo
            from selenium.webdriver.common.keys import Keys
            driver.switch_to.active_element.send_keys(Keys.ESCAPE)
            time.sleep(1)
            util_selenium.clicar_elemento_com_fallback(driver, (By.ID, "btnMenuFiltro"))
            time.sleep(1)

        # Depois que percorreu tudo do setor, tem que clicar em Expandir Filtro, para aparecer o menu novamente:        
                
    # Exibe mensagem final com o total de entrevistas liberadas, usando cor verde no terminal
    caixas_dialogo.exibir_caixa_dialogo(
        "Liberação de Codificação Concluída",
        f"{total_liberado} entrevistas foram liberadas para codificação.",
        tipo="sucesso"
    )        

def executar():
    global driver  
    print("Iniciando automação para liberar codificação...")

    # Solicita o mês e o ano antes de iniciar o WebDriver
    mes, ano = solicitar_mes_ano()    
    if not mes or not ano:
        return
    
    utils.solicitar_credenciais("Portalweb")
    driver = util_selenium.inicializar_webdriver_com_perfil()
    sequencia_portal(mes, ano)

    # Terminou:
    driver.quit()
    print("Automação concluída.")