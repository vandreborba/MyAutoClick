import os
from automacoes import liberarCodificacao, relatorioMensais

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
    print("\n--- MENU ---")
    print("1. Download Relatórios Mensais")
    print("2. Liberar Codificação")    
    print("9. Limpar credenciais salvas (PMS/PMC)")
    print("0. Sair")

def main():    
    executando = True
    while executando:       
        mostrar_menu()
        try:
            opcao = int(input("\nEscolha uma opção: "))
            
            if opcao == 1: relatorioMensais.executar()
            elif opcao == 2: liberarCodificacao.executar()
            elif opcao == 9: limpar_credenciais_criptografadas()
            elif opcao == 0:
                print("\nSaindo do programa...")
                executando = False
            else:
                print("\nOpção inválida! Digite 1, 2 ou 3.")
                
        except ValueError:
            print("\nErro: Digite um número válido!")

if __name__ == "__main__":
    main()