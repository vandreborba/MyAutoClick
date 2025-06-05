import os
import time

from automacoes import util_selenium, utils
from automacoes.accesoSistemas import acessarSda
from automacoes.autorizacaoDirigir import filtro_autorizacao_dirigir
from automacoes.caixas_dialogo import solicitar_texto_multilinha, exibir_caixa_dialogo
from selenium.webdriver.common.by import By

# Caminho do arquivo onde a lista de SIAPEs será salva (pasta do usuário)
CAMINHO_ARQUIVO_SIAPES = os.path.join(os.path.expanduser('~'), 'SIAPES_MOTORISTAS.TXT')

# Variável global para armazenar a lista de SIAPEs
lista_siapes = []

def iniciarSequencia():
    """
    Inicia a sequência de automação para liberar autorização de dirigir.
    A função acessa o site do IBGE, navega até a seção de autorização e clica nos botões necessários.
    """
    global driver

    acessarSda(driver)

    # cada hora o SDA abre de uma forma parece... tem que ver se tem o Autorização para Dirigir        
    util_selenium.clicar_elemento_por_texto_com_fallback(driver, "GESTÃO E LOGÍSTICA", tempo_espera=5)
    util_selenium.clicar_elemento_por_texto_com_fallback(driver, "Autorização para Dirigir", tempo_espera=180)
    util_selenium.clicar_elemento_por_texto_com_fallback(driver, "Relatórios")
    util_selenium.clicar_elemento_por_texto_com_fallback(driver, "Relatório de Validade de CNH")
    util_selenium.clicar_elemento_por_texto_com_fallback(driver, "Excel", tempo_espera=20) # as vezes demora.
    util_selenium.clicar_elemento_por_texto_com_fallback(driver, "Gerar Relatório")
    # Ele irá baixar um .xlsx na pasta Downloads, com todos os motoristas.
    filtro_autorizacao_dirigir.filtrar(lista_siapes)
    driver.quit()

def solicitar_lista_siapes():
    """
    Solicita ao usuário uma lista de SIAPEs usando interface gráfica centralizada.
    Armazena a lista na variável global e em arquivo. Se já houver uma lista salva, pergunta se deseja reutilizar ou informar uma nova.
    """
    global lista_siapes
    # Tenta ler a lista do arquivo, se existir
    if os.path.exists(CAMINHO_ARQUIVO_SIAPES):
        with open(CAMINHO_ARQUIVO_SIAPES, 'r', encoding='utf-8') as f:
            lista_siapes = [linha.strip() for linha in f if linha.strip()]
    if lista_siapes:
        # Exibe a lista de SIAPEs atual em caixa de diálogo
        mensagem_lista = "Lista de SIAPEs atual:\n" + ", ".join(lista_siapes)
        usar_atual = solicitar_texto_multilinha(
            titulo="SIAPEs já cadastrados",
            mensagem=mensagem_lista + "\n\nClique OK para usar esta lista ou edite para informar uma nova.",
            texto_exemplo=", ".join(lista_siapes)
        )
        # Se o usuário não alterar, mantém a lista atual
        if usar_atual.strip().replace(",", "").replace(" ", "") == "".join(lista_siapes):
            return lista_siapes
        # Caso o usuário edite, processa nova lista
        entrada = usar_atual
    else:
        # Solicita nova lista via interface
        entrada = solicitar_texto_multilinha(
            titulo="Informe os SIAPEs",
            mensagem="Informe os SIAPEs separados por vírgula, espaço ou enter:",
            texto_exemplo="1234567, 2345678, 3456789"
        )
    # Processa a entrada do usuário
    siapes = [s.strip() for s in entrada.replace(',', ' ').split() if s.strip()]
    lista_siapes = siapes
    # Salva a nova lista no arquivo
    with open(CAMINHO_ARQUIVO_SIAPES, 'w', encoding='utf-8') as f:
        for siape in lista_siapes:
            f.write(siape + '\n')
    # Exibe confirmação em caixa de diálogo
    exibir_caixa_dialogo(
        titulo="Lista de SIAPEs definida",
        mensagem="\n".join([f"{idx+1}. {siape}" for idx, siape in enumerate(lista_siapes)]),
        tipo="info"
    )
    return lista_siapes

def executar():
    global driver  
    print("Iniciando automação para liberar autorização dirigir...")    

    # Solicitar SIAPEs e salvar na variável global
    solicitar_lista_siapes()
    
    driver = util_selenium.inicializar_webdriver_com_perfil()
    
    iniciarSequencia()

    # Terminou:
    driver.quit()
    print("Automação concluída.")