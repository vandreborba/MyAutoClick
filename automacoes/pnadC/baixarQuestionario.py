import time
from automacoes import config_municipio_estado, util_selenium
from automacoes.pnadC.liberarCodificacao import abrir_pnad_c, solicitar_mes_ano
from automacoes.utils import copiar_ultimo_pdf_baixado


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
    time.sleep(2)
    # Seleciona o ano e o mês usando a função específica para Select2
    util_selenium.selecionar_select2_por_label(driver, "Ano", ano)
    time.sleep(2)
    util_selenium.selecionar_select2_por_label(driver, "Mês", mes)
    time.sleep(2)
    for entrada in lista_entradas:
        # Seleciona o setor e o domicílio usando a função específica para Select2
        util_selenium.selecionar_select2_por_label(driver, "Controle", entrada['numero_setor'])
        time.sleep(2)
        util_selenium.selecionar_select2_por_label(driver, "Domicílio", entrada['numero_domicilio'])
        time.sleep(1)        
        # Clica no botão "Filtrar" para aplicar os filtros
        util_selenium.clicar_elemento_por_texto_com_fallback(driver, "Filtrar")
        time.sleep(1)              
        listar_e_baixar_entrevistas_disponiveis(driver)
        
    
    
    
    
def listar_e_baixar_entrevistas_disponiveis(driver):
    """
    Lista todos os ícones de lupa (entrevistas disponíveis), clica em cada um, coleta informações e baixa o PDF.
    """
    from selenium.webdriver.common.by import By
    import time

    # Busca todos os elementos com a classe 'fa fa-search' (pode ser <i>, <em> ou outra tag)
    icones_lupa = driver.find_elements(By.CSS_SELECTOR, ".fa.fa-search")
    print(f"[INFO] Encontrados {len(icones_lupa)} ícones de lupa (entrevistas disponíveis).")

    for indice, icone in enumerate(icones_lupa, start=1):
        try:
            # Sobe para o elemento pai <td> (que possui o evento de clique)
            elemento_td = icone.find_element(By.XPATH, "./ancestor::td")
            try:
                # Tenta clicar normalmente no <td>
                elemento_td.click()
                print(f"[SUCESSO] Clique realizado normalmente na entrevista {indice}.")
            except Exception as erro_click:
                # Se falhar, tenta via JavaScript
                driver.execute_script("arguments[0].click();", elemento_td)
                print(f"[SUCESSO] Clique realizado via JavaScript na entrevista {indice}.")
            time.sleep(1)

            # Alterna para a nova aba aberta
            driver.switch_to.window(driver.window_handles[-1])
            print("[INFO] Alternado para a nova aba da entrevista.")

            # Coleta informações de ano, mês, semana, controle, domicílio e morador
            info = coletar_informacoes_entrevista(driver)
            print(f"[INFO] Informações coletadas: {info}")

            # Espera 5 segundos antes de baixar o PDF
            time.sleep(5)

            # Clica no ícone de PDF para baixar o questionário
            try:
                # Aguarda o ícone de PDF estar presente e visível
                seletor_pdf = (By.CSS_SELECTOR, "i.fa-file-pdf")
                util_selenium.aguardar_elemento(driver, seletor_pdf, tempo=10)
                icone_pdf = driver.find_element(*seletor_pdf)
                driver.execute_script("arguments[0].scrollIntoView(true);", icone_pdf)
                # Usa função util_selenium para clicar com fallback
                util_selenium.clicar_elemento_com_fallback(driver, seletor_pdf)
                print("[SUCESSO] Clique realizado no ícone de PDF para baixar o questionário.")
                # Após clicar, aguarda e copia o arquivo baixado
                time.sleep(2) # é bem rápido.
                copiar_ultimo_pdf_baixado(info)
            except Exception as erro_pdf:
                print(f"[ERRO] Não foi possível clicar no ícone de PDF: {erro_pdf}")

            # Fecha a aba da entrevista e volta para a principal
            driver.close()
            driver.switch_to.window(driver.window_handles[1])
            print("[INFO] Aba da entrevista fechada e retornou para a principal.")
            time.sleep(1)
        except Exception as erro:
            print(f"[ERRO] Não foi possível processar a entrevista {indice}: {erro}")

def coletar_informacoes_entrevista(driver):
    """
    Coleta informações de ano, mês, semana, controle, domicílio e morador da página da entrevista.
    Retorna um dicionário com os dados coletados.
    """
    from selenium.webdriver.common.by import By
    info = {}
    try:
        # Busca todos os <div class="row dados">
        divs_dados = driver.find_elements(By.CSS_SELECTOR, "div.row.dados")
        for div in divs_dados:
            texto = div.text
            # Extrai informações usando buscas simples
            if "Ano:" in texto:
                for parte in texto.split("\n"):
                    if "Ano:" in parte:
                        info['ano'] = parte.split(":")[-1].strip()
                    if "Mês:" in parte:
                        info['mes'] = parte.split(":")[-1].strip()
                    if "Semana:" in parte:
                        info['semana'] = parte.split(":")[-1].strip()
            if "Controle:" in texto:
                for parte in texto.split("\n"):
                    if "Controle:" in parte:
                        info['controle'] = parte.split(":")[-1].strip()
                    if "Domicílio:" in parte:
                        info['domicilio'] = parte.split(":")[-1].strip()
                    if "Morador:" in parte:
                        info['morador'] = parte.split(":")[-1].strip()
    except Exception as erro:
        print(f"[ERRO] Não foi possível coletar informações da entrevista: {erro}")
    return info

def renomear_ultimo_pdf_baixado(info):
    """
    Renomeia o arquivo PDF baixado mais recente na pasta de downloads do perfil Selenium,
    usando as informações coletadas da entrevista.
    """
    import os
    import time
    import glob
    import re

    # Caminho do perfil do Chrome usado pelo Selenium
    pasta_downloads = os.path.abspath('./chrome_temp_profile/Default/Downloads')
    if not os.path.exists(pasta_downloads):
        print(f"[ERRO] Pasta de downloads não encontrada: {pasta_downloads}")
        return

    # Aguarda o arquivo PDF aparecer e o download terminar (não pode ter .crdownload)
    timeout = 30  # segundos
    tempo_inicial = time.time()
    arquivo_pdf = None
    while time.time() - tempo_inicial < timeout:
        arquivos = glob.glob(os.path.join(pasta_downloads, '*.pdf'))
        if arquivos:
            # Pega o PDF mais recente
            arquivo_pdf = max(arquivos, key=os.path.getctime)
            # Verifica se não existe o .crdownload correspondente
            if not os.path.exists(arquivo_pdf + '.crdownload'):
                break
        time.sleep(1)
    if not arquivo_pdf:
        print('[ERRO] Nenhum arquivo PDF encontrado para renomear.')
        return

    # Monta o novo nome do arquivo
    def limpar_nome(texto):
        # Remove caracteres inválidos para nome de arquivo
        return re.sub(r'[^a-zA-Z0-9_-]+', '_', str(texto))
    novo_nome = f"questionario_{limpar_nome(info.get('ano',''))}_{limpar_nome(info.get('mes',''))}_{limpar_nome(info.get('semana',''))}_{limpar_nome(info.get('controle',''))}_{limpar_nome(info.get('domicilio',''))}_{limpar_nome(info.get('morador',''))}.pdf"
    novo_caminho = os.path.join(pasta_downloads, novo_nome)

    try:
        os.rename(arquivo_pdf, novo_caminho)
        print(f"[SUCESSO] Arquivo PDF renomeado para: {novo_nome}")
    except Exception as erro:
        print(f"[ERRO] Não foi possível renomear o arquivo PDF: {erro}")

def executar(mes=None, ano=None, texto_input=None):
    global driver  
    print("Iniciando automação para baixar questionários...")

    # Solicita o mês e o ano antes de iniciar o WebDriver
    if not mes or not ano:
        mes, ano = solicitar_mes_ano()
    if not mes or not ano:
        return

    texto = texto_input
    # Solicita a lista de setores e domicílios usando interface gráfica centralizada
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
                return executar()
            lista_entradas.append({
                'numero_setor': partes[0].strip(),
                'numero_domicilio': partes[1].strip()
            })

    driver = util_selenium.inicializar_webdriver_com_perfil()
    sequencia_portal(lista_entradas, mes, ano)    
   
    # Terminou:
    driver.quit()
    print("Automação concluída.")