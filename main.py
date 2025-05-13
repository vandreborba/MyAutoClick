import os
from automacoes import relatorioMensais
from automacoes.pnadC import baixarQuestionario, liberarCodificacao

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
    print("--- PnadC ---")
    print("2. Liberar Codificação")    
    print("3. Baixar Questionário")
    print("--- Outros ---")
    print("8. Configurar Município e Estado")
    print("9. Limpar credenciais salvas (PMS/PMC)")
    print("0. Sair")

def main():    
    executando = True
    from automacoes.config_municipio_estado import config_municipio_estado
    while executando:       
        mostrar_menu()
        try:
            opcao = int(input("\nEscolha uma opção: "))
            
            if opcao == 1: relatorioMensais.executar()
            elif opcao == 2: liberarCodificacao.executar()
            elif opcao == 3: baixarQuestionario.executar()
            elif opcao == 8:
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
            elif opcao == 9: limpar_credenciais_criptografadas()
            elif opcao == 0:
                print("\nSaindo do programa...")
                executando = False
            else:
                print("\nOpção inválida! Digite 1, 2, 3 ou 4.")
                
        except ValueError:
            print("\nErro: Digite um número válido!")

if __name__ == "__main__":
    main()