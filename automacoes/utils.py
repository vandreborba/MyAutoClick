import os
import pyautogui
import time
from cryptography.fernet import Fernet
import base64

# Chave fixa para criptografia (ATENÇÃO: visível no código, use apenas em ambiente controlado)
CHAVE_FIXA = b'2Qw1v7Qw1v7Kw1v7Qw1v7Qw1v7Hw1v8Qw1v7Qw1v7Qw='

CAMINHO_ARQUIVO_CREDENCIAIS = os.path.join(os.path.expanduser('~'), '.myautoclicer')
# Não é mais necessário CAMINHO_ARQUIVO_CHAVE

def preparar_navegador(url):
    """ 
    Função para orientar o usuário e garantir que o navegador está pronto.
    """
    print("\n=== PREPARAÇÃO ===")
    input("Certifique-se de que o navegador está ABERTO e LOGADO em segundo plano. Pressione ENTER para continuar...\n(Teste com: Alt+Tab, o navegador deve abrir)")
    time.sleep(1)
    minimizar_janela_atual()
    #nova aba:
    pyautogui.hotkey('ctrl', 't')
    time.sleep(0.2)
    pyautogui.write(url)
    pyautogui.press('enter')



def minimizar_janela_atual():
    """ 
    Minimiza APENAS a janela atual (ex: terminal/IDE) usando Alt + Space → N.
    """
    print("\nMinimizando janela atual...")
    pyautogui.hotkey('alt', 'space')  # Abre o menu de controle
    time.sleep(0.5)  # Tempo para o menu abrir
    pyautogui.press('n')              # Pressiona "N" para minimizar
    time.sleep(1)  

def localizar_e_clicar(nome_imagem, offset_x=0, offset_y=0, tentativas=3):
    """
    Localiza uma imagem na tela e clica com um deslocamento opcional.
    
    Args:
        nome_imagem (str): Nome do arquivo da imagem (ex: 'botao.png').
        offset_x (int): Deslocamento horizontal em pixels (negativo = esquerda, positivo = direita).
        offset_y (int): Deslocamento vertical em pixels (negativo = cima, positivo = baixo).
        tentativas (int): Quantidade de tentativas antes de falhar.
    """
    for _ in range(tentativas):
        try:
            # Localiza a imagem com 80% de precisão
            posicao = pyautogui.locateOnScreen(
                f'imagens/{nome_imagem}',
                confidence=0.8,
                grayscale=True
            )
            if posicao:
                x, y = pyautogui.center(posicao)
                pyautogui.click(x + offset_x, y + offset_y)
                print(f"Clicado em {x + offset_x}, {y + offset_y} (offset aplicado).")
                return True
        except Exception as e:
            print(f"Erro ao localizar {nome_imagem}: {e}")
        time.sleep(1)
    print(f"Imagem '{nome_imagem}' não encontrada após {tentativas} tentativas.")
    return False

def aguardar_carregamento_pagina(
    imagem_confirmacao,       # Nome da imagem que indica que a página carregou (ex: 'logo_pagina.png')
    timeout=30,               # Tempo máximo de espera (segundos)
    intervalo=1,              # Intervalo entre verificações (segundos)
    confidence=0.8            # Precisão da imagem (0.8 é recomendado)
):
    """
    Aguarda até que uma imagem específica (ex: logo da página) seja encontrada na tela,
    indicando que o navegador terminou de carregar a página.

    Args:
        imagem_confirmacao (str): Nome do arquivo da imagem (ex: 'logo.png').
        timeout (int): Tempo máximo de espera em segundos.
        intervalo (int): Intervalo entre as verificações.
        confidence (float): Precisão mínima para a correspondência da imagem.

    Returns:
        bool: True se a imagem foi encontrada, False se o timeout foi atingido.
    """
    tempo_inicial = time.time()
    caminho_imagem = os.path.abspath(f"imagens/{imagem_confirmacao}")
    
    # Verifica se a imagem existe no sistema
    if not os.path.exists(caminho_imagem):
        print(f"\nERRO: A imagem '{caminho_imagem}' não existe no sistema.")
        return False

    while True:
        # Verifica timeout
        if time.time() - tempo_inicial > timeout:
            print(f"\nERRO: Timeout de {timeout}s atingido. Imagem '{imagem_confirmacao}' não encontrada.")
            return False

        try:
            # Tenta localizar a imagem
            posicao = pyautogui.locateCenterOnScreen(
                caminho_imagem,
                confidence=confidence,
                grayscale=True
            )
            
            if posicao:
                print("Página carregada!")                
                return True
            
            # Se não encontrou, aguarda e continua
            print(f"Aguardando... ({int(time.time() - tempo_inicial)}s/{timeout}s)")
            time.sleep(intervalo)
        
        except Exception as e:
            print(f"Tipo de erro: {type(e).__name__}")
            print(f"Mensagem: {str(e)}")
            print(f"Argumentos: {e.args}")
            return False

def gerar_e_salvar_chave_criptografia():
    """
    Retorna a chave fixa definida no código.
    """
    return CHAVE_FIXA

def carregar_chave_criptografia():
    """
    Retorna a chave fixa definida no código.
    """
    return CHAVE_FIXA

def salvar_credenciais_criptografadas(login, senha):
    """
    Salva o login e a senha criptografados em um arquivo local.
    """
    chave = carregar_chave_criptografia()
    fernet = Fernet(chave)
    dados = f"{login}\n{senha}".encode('utf-8')
    dados_criptografados = fernet.encrypt(dados)
    with open(CAMINHO_ARQUIVO_CREDENCIAIS, 'wb') as arquivo:
        arquivo.write(dados_criptografados)

def carregar_credenciais_criptografadas():
    """
    Carrega o login e a senha criptografados do arquivo local.
    Retorna uma tupla (login, senha) ou (None, None) se não existir.
    """
    if not os.path.exists(CAMINHO_ARQUIVO_CREDENCIAIS):
        return None, None
    chave = carregar_chave_criptografia()
    fernet = Fernet(chave)
    with open(CAMINHO_ARQUIVO_CREDENCIAIS, 'rb') as arquivo:
        dados_criptografados = arquivo.read()
    try:
        dados = fernet.decrypt(dados_criptografados).decode('utf-8')
        login, senha = dados.split('\n', 1)
        return login, senha
    except Exception as erro:
        print(f"[ERRO] Não foi possível descriptografar as credenciais: {erro}")
        return None, None

def solicitar_credenciais(nome_sistema=""):
    """
    Solicita ao usuário o login e a senha, com opção de salvar e reutilizar as credenciais criptografadas.

    Retorna:
        tuple: Uma tupla contendo o login e a senha fornecidos pelo usuário.
    """
    # Tenta carregar credenciais salvas
    login, senha = carregar_credenciais_criptografadas()
    if login and senha:
        return login, senha
    
    # Solicita o login ao usuário
    login = pyautogui.prompt(f"Digite seu login para acessar o sistema {nome_sistema}:")
    # Solicita a senha ao usuário
    senha = pyautogui.password(f"Digite sua senha para acessar o sistema {nome_sistema}:")
    # Pergunta se deseja salvar as credenciais
    salvar = pyautogui.confirm(text="Deseja salvar estas credenciais criptografadas para uso futuro?", buttons=["Sim", "Não"])
    if salvar == "Sim":
        salvar_credenciais_criptografadas(login, senha)
        print("[INFO] Credenciais salvas com criptografia.")
    return login, senha

def pressionar_tab(vezes):
    """
    Pressiona a tecla TAB um número específico de vezes.

    Args:
        vezes (int): Número de vezes que a tecla TAB deve ser pressionada.
    """
    for _ in range(vezes):
        pyautogui.press('tab')
    print(f"Tecla TAB pressionada {vezes} vezes.")

def copiar_ultimo_pdf_baixado(info):
    """
    Copia o arquivo PDF baixado mais recente na pasta de downloads do usuário para o novo nome,
    usando as informações coletadas da entrevista. O arquivo original é mantido.

    Usado no baixarQuestionario.py... 
    """
    import os
    import time
    import glob
    import re
    import shutil

    # Caminho da pasta de downloads do usuário
    pasta_downloads = os.path.expanduser("~\\Downloads")
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
        print('[ERRO] Nenhum arquivo PDF encontrado para copiar.')
        return

    # Monta o novo nome do arquivo
    def limpar_nome(texto):
        # Remove caracteres inválidos para nome de arquivo
        return re.sub(r'[^a-zA-Z0-9_-]+', '_', str(texto))
    novo_nome = f"questionario_{limpar_nome(info.get('ano',''))}_{limpar_nome(info.get('mes',''))}_{limpar_nome(info.get('semana',''))}_{limpar_nome(info.get('controle',''))}_{limpar_nome(info.get('domicilio',''))}_{limpar_nome(info.get('morador',''))}.pdf"
    novo_caminho = os.path.join(pasta_downloads, novo_nome)

    try:
        shutil.copy2(arquivo_pdf, novo_caminho)
        print(f"[SUCESSO] Arquivo PDF copiado para: {novo_nome}")
    except Exception as erro:
        print(f"[ERRO] Não foi possível copiar o arquivo PDF: {erro}")
