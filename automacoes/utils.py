import os
import pyautogui
import time

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
            