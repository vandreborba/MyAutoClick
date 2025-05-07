from automacoes import relatorioMensais

def mostrar_menu():
    print("\n--- MENU ---")
    print("1. Download Relatórios Mensais")
    print("2. Teste 2")
    print("0. Sair")

def main():
    executando = True
    while executando:
        mostrar_menu()
        try:
            opcao = int(input("\nEscolha uma opção (1/2/3): "))
            
            if opcao == 1: relatorioMensais.executar()
            elif opcao == 2: print( "\nTeste 2" )
            elif opcao == 0:
                print("\nSaindo do programa...")
                executando = False
            else:
                print("\nOpção inválida! Digite 1, 2 ou 3.")
                
        except ValueError:
            print("\nErro: Digite um número válido!")

if __name__ == "__main__":
    main()