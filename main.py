import os
import pandas  # Garante inclusão do pandas no build do PyInstaller
from automacoes import relatorioMensais
from automacoes.autorizacaoDirigir import autorizacao_dirigir
from automacoes.pnadC import baixarQuestionario, liberarCodificacao
import sys

'''
#############


Liberar Codificação está funcionando?

# Melhorias para depois:
- No Liberar codificação não precisa escolher o mês/ano, só tentar o atual, e o anterior. Será?

#############
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
    print("      \033[1;36mBem-vindo ao My IBGE Auto Clicker\033[0m")
    print("="*50)
    print("\n\033[1;33mMENU PRINCIPAL\033[0m\n")
    print("\033[1;32m1.\033[0m  \033[1mDownload Relatórios Mensais\033[0m")
    print("\n\033[1;34m--- PnadC ---\033[0m")
    print("\033[1;32m2.\033[0m  Liberar Codificação")    
    print("\033[1;32m3.\033[0m  Baixar Questionário")
    print("\n\033[1;34m--- Administração ---\033[0m")
    print("\033[1;32m4.\033[0m  Relatório de Autorização para Dirigir")
    print("\n\033[1;34m--- Outros ---\033[0m")
    print("\033[1;32m8.\033[0m  Configurar Município e Estado")
    print("\033[1;32m9.\033[0m  Limpar credenciais salvas")
    print("\033[1;31m0.\033[0m  Sair")
    print("="*50)

def executar_opcao(opcao):
    """
    Executa a ação correspondente à opção escolhida, seja por argumento ou menu.
    Parâmetros:
        opcao (str ou int): Opção escolhida pelo usuário.
    """
    from automacoes.config_municipio_estado import config_municipio_estado
    if str(opcao) == "1":
        relatorioMensais.executar()
    elif str(opcao) == "2":
        liberarCodificacao.executar()
    elif str(opcao) == "3":
        baixarQuestionario.executar()
    elif str(opcao) == "4":
        autorizacao_dirigir.executar()
    elif str(opcao) == "8":
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
    elif str(opcao) == "9":
        limpar_credenciais_criptografadas()
    elif str(opcao) == "0":
        print("\nSaindo do programa...")
        return False
    else:
        print("\nOpção inválida! Digite 1, 2, 3, 8, 9 ou 0.")
    return True

def main():    
    executando = True
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