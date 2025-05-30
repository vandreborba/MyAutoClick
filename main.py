import os
import pandas  # Garante inclusão do pandas no build do PyInstaller
from automacoes import relatorioMensais
from automacoes.autorizacaoDirigir import autorizacao_dirigir
from automacoes.pnadC import baixarQuestionario, cancelarCodificacao, liberarCodificacao
from automacoes.pnadC import associarEntrevistas
import sys

'''
#############

- Criar o cadastro do rev. sev.

#############
'''

# Número da versão do sistema
VERSAO_SISTEMA = "0.8"

# INSTRUÇÕES DE USO DO SISTEMA
INSTRUCOES_SISTEMA = '''
- Este programa automatiza algumas atividades usando o navegador de forma autônoma,
  porém algumas vezes é necessário fazer login manualmente nos sistemas.
- Você pode usar computador enquanto o robô executa as tarefas, mas não minimize o navegador.
- Usar somente em rede da agência (Computadores da agência).
'''

def limpar_credenciais_criptografadas():
    """
    Remove os arquivos de credenciais e chave de criptografia salvos localmente.
    """
    import os
    from automacoes.utils import CAMINHO_ARQUIVO_CREDENCIAIS, CAMINHO_ARQUIVO_CHAVE
    arquivos_removidos = []
    for caminho in [CAMINHO_ARQUIVO_CREDENCIAIS, CAMINHO_ARQUIVO_CHAVE]:
        if os.path.exists(caminho):
            os.remove(caminho)
            arquivos_removidos.append(caminho)
    if arquivos_removidos:
        print("\n[INFO] Credenciais e chave de criptografia removidas com sucesso:")
        for arq in arquivos_removidos:
            print(f" - {arq}")
    else:
        print("\n[INFO] Nenhum arquivo de credencial ou chave encontrado para remover.")

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
    """
    Executa a ação correspondente à opção escolhida, seja por argumento ou menu.
    Parâmetros:
        opcao (str ou int): Opção escolhida pelo usuário.
    """
    from automacoes.config_municipio_estado import config_municipio_estado
    if str(opcao) == "10":
        relatorioMensais.executar()
    elif str(opcao) == "20":
        liberarCodificacao.executar()
    elif str(opcao) == "21":
        cancelarCodificacao.executar()
    elif str(opcao) == "22":
        baixarQuestionario.executar()
    elif str(opcao) == "23":
        associarEntrevistas.executar()
    elif str(opcao) == "30":
        autorizacao_dirigir.executar()    
    elif str(opcao) == "98":
        print("\n--- Configuração de Município e Estado ---")
        print(f"Estado atual: {config_municipio_estado.estado}")
        print(f"Município atual: {config_municipio_estado.municipio}")
        novo_estado = input("Digite o novo Estado (ex: 41 - PARANÁ) ou pressione Enter para manter: ").strip()
        novo_municipio = input("Digite o novo Município (ex: 411520000 - Maringá) ou pressione Enter para manter: ").strip()
        if novo_estado:
            config_municipio_estado.estado = novo_estado
        if novo_municipio:
            config_municipio_estado.municipio = novo_municipio
        config_municipio_estado.salvar()
        print("[SUCESSO] Configuração salva!")
    elif str(opcao) == "99":
        limpar_credenciais_criptografadas()
    elif str(opcao) == "0":
        print("\nSaindo do programa...")
        return False
    else:
        print("\nOpção inválida! Digite 1, 2, 3, 8, 9 ou 0.")
    return True

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
    main()