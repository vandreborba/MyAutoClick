import os

from automacoes import util_selenium
from automacoes.autorizacaoDirigir import filtro_autorizacao_dirigir

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

    url_portal_web = "https://portalweb.ibge.gov.br/"
    driver.get(url_portal_web)
    # Clica no menu principal, aguardando o login se necessário
    util_selenium.clicar_elemento_por_texto_com_fallback(driver, "Sistemas Administrativos", tempo_espera=180)
    util_selenium.clicar_elemento_por_texto_com_fallback(driver, "SDA")
    # Alterna para a nova aba aberta, caso o clique abra em nova aba
    util_selenium.alternar_para_ultima_aba(driver)    
    # Aqui pode acontecer de pedir o login:
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
    Solicita ao usuário uma lista de SIAPEs e armazena na variável global e em arquivo.
    Se já houver uma lista salva no arquivo, pergunta se deseja reutilizar ou informar uma nova.
    """
    global lista_siapes
    # Tenta ler a lista do arquivo, se existir
    if os.path.exists(CAMINHO_ARQUIVO_SIAPES):
        with open(CAMINHO_ARQUIVO_SIAPES, 'r', encoding='utf-8') as f:
            lista_siapes = [linha.strip() for linha in f if linha.strip()]
    if lista_siapes:
        print(f"Lista de SIAPEs atual: {lista_siapes}")
        usar_atual = input("Deseja usar a lista atual de SIAPEs? (s/n): ").strip().lower()
        if usar_atual == 's':
            return lista_siapes
    # Solicita nova lista
    entrada = input("Informe os SIAPEs separados por vírgula, espaço ou enter: ")
    siapes = [s.strip() for s in entrada.replace(',', ' ').split() if s.strip()]
    lista_siapes = siapes
    # Salva a nova lista no arquivo
    with open(CAMINHO_ARQUIVO_SIAPES, 'w', encoding='utf-8') as f:
        for siape in lista_siapes:
            f.write(siape + '\n')
    print(f"Lista de SIAPEs definida: {lista_siapes}")
    return lista_siapes

def executar():
    global driver  
    print("Iniciando automação para liberar autorização dirigir...")    

    # Solicitar SIAPEs e salvar na variável global
    solicitar_lista_siapes()
    
    driver = util_selenium.inicializar_webdriver_com_perfil()
    
    iniciarSequencia()

    # Terminou:
    # driver.quit()
    print("Automação concluída.")