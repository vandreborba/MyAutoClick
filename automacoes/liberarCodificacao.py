import time
from automacoes import util_selenium
from selenium.webdriver.common.by import By


driver = None  # Variável global para armazenar o WebDriver
def sequencia_portal(mes, ano):
    global driver

    # Será se este endereço muda com o tempo?
    urlLiberarCodificacao = "https://portalweb.ibge.gov.br/f5-w-68747470733a2f2f773373696763706e6164632e696267652e676f762e6272$$/f5-h-$$/LiberarParaCodificacao"    
    
    # Acessa o portal web:
    urlPortalWeb = "https://portalweb.ibge.gov.br/"
    driver.get(urlPortalWeb)
    util_selenium.clicar_elemento_por_texto_com_fallback(driver, "Pesquisas Domiciliares e Sociais",tempo_espera=180) #Esperar, pode ser que o usuário faça login
    util_selenium.clicar_elemento_por_texto_com_fallback(driver, "PNAD Contínua")    
    # Após clicar, alterna para a nova aba aberta (caso o clique abra em nova aba)
    util_selenium.alternar_para_ultima_aba(driver)
    # Comentário: Garante que o Selenium continue operando na aba correta

    # Vamos tentr acessar a URL diretamente agora:
    driver.get(urlLiberarCodificacao)

    # tem que aguardar o carregamento: Aguardar aparecer 41 - Paraná:
    util_selenium.aguardar_elemento_por_texto(driver, "41 - PARANÁ", tempo_espera=30)
    util_selenium.aguardar_elemento_por_texto(driver, "TODOS", tempo_espera=30)

    util_selenium.selecionar_dropdown_por_label(driver, "Ano", ano)
    time.sleep(2)
    util_selenium.selecionar_dropdown_por_label(driver, "Mes", mes)
    time.sleep(2)    
    util_selenium.selecionar_dropdown_por_label(driver, "Agência", "411520000")
    time.sleep(2)

    listaSetores = util_selenium.listar_opcoes_dropdown_por_label(driver, "Controle")
    # o primeiro elemento é o "Selecione", vamos remover:
    listaSetores = listaSetores[1:]  # Remove o primeiro elemento
    # precisamos apenas dos textos, e não dos valores:
    listaSetores = [setor['texto'] for setor in listaSetores]
    print(f"Setores disponíveis: {listaSetores}")

    # Agora para cada setor precisamos "liberar" a codificação:
    for setor in listaSetores:
        print(f"Liberando codificação para o setor: {setor}")
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
        # se tiver, tem que apertar os botões para liberar referente aos domicílios, (Não dá para fazer agora pq não tem nenhum para vermos como ficaria.)

        # Depois que percorreu tudo do setor, tem que clicar em Expandir Filtro, para aparecer o menu novamente:        
                

        
        
    



def executar():
    global driver  
    print("Iniciando automação para liberar codificação...")

    # Solicita o mês e o ano antes de iniciar o WebDriver
    entrada = input("Digite o mês e o ano para liberar a codificação (ex: 5-2025): ")
    try:
        mes, ano = entrada.strip().split("-")
        mes = mes.strip().lstrip("0") # remover leading zero
        ano = ano.strip()
    except Exception:
        print("[ERRO] Entrada inválida! Use o formato M-AAAA, por exemplo: 5-2025")
        return

    driver = util_selenium.inicializar_webdriver_com_perfil()
    sequencia_portal(mes, ano)

    # Terminou:
    # driver.quit()
    print("Automação concluída.")