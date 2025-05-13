import time
from automacoes import config_municipio_estado, util_selenium
from automacoes.pnadC.liberarCodificacao import abrir_pnad_c, solicitar_mes_ano


def sequencia_portal(lista_entradas, mes, ano):
    global driver

    # Será se este endereço muda com o tempo?
    urlLiberarCodificacao = "https://portalweb.ibge.gov.br/f5-w-68747470733a2f2f773373696763706e6164632e696267652e676f762e6272$$/f5-h-$$/Questionario"    
    
    # Acessa o portal web e navega até PNAD Contínua
    abrir_pnad_c(driver)

    # Vamos tentr acessar a URL diretamente agora:
    driver.get(urlLiberarCodificacao)
    # aguardar carregar: (Aparece "TODOS" quando carrega)
     # tem que dar tempo da pessoa fazer o login.
    util_selenium.aguardar_elemento_por_texto(driver, "TODOS", tempo_espera=120)    
    util_selenium.selecionar_dropdown_por_label(driver, "Ano", ano)
    time.sleep(2)
    util_selenium.selecionar_dropdown_por_label(driver, "Mês", mes)
    time.sleep(2)    

    # Ok! Agora tenho que aguardar ter alguma entrevista realizada para testar...
    


def executar():
    global driver  
    print("Iniciando automação para baixar questionários...")

    # Solicita o mês e o ano antes de iniciar o WebDriver
    mes, ano = solicitar_mes_ano()
    if not mes or not ano:
        return

    # Solicita a lista de setores e domicílios
    print("Cole a lista de setores e domicílios (numeroSetor\tnumeroDomicilio), uma linha por registro. Finalize com uma linha vazia:")
    lista_entradas = []
    while True:
        linha = input()
        if not linha.strip():
            break
        try:
            numero_setor, numero_domicilio = linha.strip().split("\t")
            lista_entradas.append({
                'numero_setor': numero_setor.strip(),
                'numero_domicilio': numero_domicilio.strip()
            })
        except Exception:
            print(f"[ERRO] Linha inválida: {linha}. Use o formato numeroSetor\tnumeroDomicilio.")

    driver = util_selenium.inicializar_webdriver_com_perfil()
    sequencia_portal(lista_entradas, mes, ano)    
   
    # Terminou:
    # driver.quit()
    print("Automação concluída.")