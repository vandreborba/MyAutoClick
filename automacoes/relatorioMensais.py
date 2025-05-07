import pyautogui
import time
from automacoes import utils

def executar():
    print("Automação \"Relatórios Mensais\" iniciada.")
    urlPMC = "https://portalweb.ibge.gov.br/f5-w-687474703a2f2f77332e706d632e696267652e676f762e6272$$/"
    utils.preparar_navegador(urlPMC)
    if not utils.aguardar_carregamento_pagina("acesso-PMC.jpg"):        
        return
    
    pyautogui.hotkey('alt', 'tab')
    print("Automação concluída.")