import os
import pandas  # Garante inclusão do pandas no build do PyInstaller
from automacoes import relatorioMensais
from automacoes.autorizacaoDirigir import autorizacao_dirigir
from automacoes.pnadC import baixarQuestionario, cancelarCodificacao, liberarCodificacao
from automacoes.pnadC import associarEntrevistas
import sys
import colorama  # Adiciona suporte a cores ANSI no Windows

# Importa a função para iniciar a interface gráfica
from automacoes.interface_grafica import iniciar_interface
from automacoes.config_interface import VERSAO_SISTEMA, INSTRUCOES_SISTEMA, executar_opcao

'''
#############

- Criar o cadastro do rev. sev.
- Criar um "retornar entrevistas". Tem que cancelar a codificação, baixar o questionário e associar as entrevistas.
- Criar um "conferir se a empresa está nas econômicas anuais", o script receberia uma lista de CNPJs e verificaria se estão na base de econômicas anuais, retornando os que estão.

#############
'''

colorama.init(autoreset=True)  # Inicializa o colorama para garantir cores no terminal Windows

def limpar_credenciais_criptografadas():
    """
    Remove os arquivos de credenciais e chave de criptografia salvos localmente e exibe o resultado em caixa de diálogo.
    """
    import os
    from automacoes.utils import CAMINHO_ARQUIVO_CREDENCIAIS, CAMINHO_ARQUIVO_CHAVE
    from automacoes.caixas_dialogo import exibir_caixa_dialogo
    arquivos_removidos = []
    for caminho in [CAMINHO_ARQUIVO_CREDENCIAIS, CAMINHO_ARQUIVO_CHAVE]:
        if os.path.exists(caminho):
            os.remove(caminho)
            arquivos_removidos.append(caminho)
    if arquivos_removidos:
        mensagem = "Credenciais e chave de criptografia removidas com sucesso:\n" + "\n".join(f"- {arq}" for arq in arquivos_removidos)
        exibir_caixa_dialogo("Limpeza de Credenciais", mensagem, tipo="sucesso")
    else:
        exibir_caixa_dialogo("Limpeza de Credenciais", "Nenhum arquivo de credencial ou chave encontrado para remover.", tipo="info")

def mostrar_menu():
    """
    Exibe o menu principal do My IBGE Auto Clicker com formatação visual aprimorada.
    """
    print("\n" + "="*50)    
    print(f"      \033[1;36mBem-vindo ao My IBGE Auto Clicker v{VERSAO_SISTEMA}\033[0m")    
    print("="*50)
    print(f"\033[0;90mInstruções: \n{INSTRUCOES_SISTEMA}\033[0m")

    print("\n\033[1;33mMENU PRINCIPAL\033[0m\n")
    print("\n\033[1;34m--- Econômicas ---\033[0m")
    print("\033[1;32m10.\033[0m  Download Relatórios Mensais")
    print("\n\033[1;34m--- PnadC ---\033[0m")
    print("\033[1;32m20.\033[0m  Liberar Codificação (Todos)")    
    print("\033[1;32m21.\033[0m  Cancelar Liberação Codificação")
    print("\033[1;32m22.\033[0m  Baixar Questionários")
    print("\033[1;32m23.\033[0m  Associar Entrevistas")
    print("\n\033[1;34m--- Administração ---\033[0m")
    print("\033[1;32m30.\033[0m  Relatório de Autorização para Dirigir")    
    print("\n\033[1;34m--- Outros ---\033[0m")
    print("\033[1;32m98.\033[0m  Configurar Município e Estado")
    print("\033[1;32m99.\033[0m  Limpar credenciais salvas")
    print("\033[1;31m0.\033[0m  Sair")
    print("="*50)

def executar_opcao(opcao):
    # Função movida para automacoes/config_interface.py
    from automacoes.config_interface import executar_opcao as executar_opcao_interface
    return executar_opcao_interface(opcao)

def main():    
    executando = True
    # Aviso sobre o Chrome Portable
    from automacoes.util_selenium import CAMINHO_CHROME_PORTABLE
    if not os.path.exists(CAMINHO_CHROME_PORTABLE):
        print("\n\033[1;31mATENÇÃO:\033[0m Para automação funcionar corretamente, baixe a versão 135 do Google Chrome Portable e extraia na área de trabalho, na pasta 'GoogleChromePortable'.\nO executável deve estar em: 'GoogleChromePortable/App/Chrome-bin/chrome.exe'\nLink recomendado: https://portableapps.com/apps/internet/google_chrome_portable (verifique a versão 124)")
    # Verifica se foi passado argumento na linha de comando
    if len(sys.argv) > 1:
        argumento = sys.argv[1]
        print(f"[INFO] Argumento recebido: {argumento}")
        executar_opcao(argumento)
        return  # Sai após executar a opção por argumento

    while executando:       
        mostrar_menu()
        try:
            opcao = input("\nEscolha uma opção: ")
            executando = executar_opcao(opcao)
        except ValueError:
            print("\nErro: Digite um número válido!")

if __name__ == "__main__":
    # Se desejar iniciar pela interface gráfica, descomente a linha abaixo:
    iniciar_interface()
    # main()