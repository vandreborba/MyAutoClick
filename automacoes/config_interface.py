# Centraliza constantes e funções compartilhadas entre main.py e interface_grafica.py
from automacoes import relatorioMensais
from automacoes.autorizacaoDirigir import autorizacao_dirigir
from automacoes.pnadC import baixarQuestionario, cancelarCodificacao, liberarCodificacao
from automacoes.pnadC import associarEntrevistas

# Número da versão do sistema
VERSAO_SISTEMA = "0.10"

# Instruções de uso do sistema
INSTRUCOES_SISTEMA = '''
- Este programa automatiza algumas atividades usando o navegador de forma autônoma,
  porém algumas vezes é necessário fazer login manualmente nos sistemas.
- Você pode usar computador enquanto o robô executa as tarefas, mas não minimize o navegador.
- Usar somente em rede da agência (Computadores da agência).
'''

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
        from automacoes.caixas_dialogo import solicitar_config_municipio_estado
        estado_atual = config_municipio_estado.estado
        municipio_atual = config_municipio_estado.municipio
        novo_estado, novo_municipio = solicitar_config_municipio_estado(estado_atual, municipio_atual)
        if novo_estado:
            config_municipio_estado.estado = novo_estado
        if novo_municipio:
            config_municipio_estado.municipio = novo_municipio
        config_municipio_estado.salvar()
        print("[SUCESSO] Configuração salva!")
    elif str(opcao) == "99":
        from main import limpar_credenciais_criptografadas
        limpar_credenciais_criptografadas()
    elif str(opcao) == "0":
        print("\nSaindo do programa...")
        return False
    else:
        print("\nOpção inválida! Digite 1, 2, 3, 8, 9 ou 0.")
    return True
