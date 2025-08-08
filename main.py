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
Todo:
- Receber uma lista de cnpj's e conferir dados da rais (PO e Sal).
- Criar o cadastro do rev. sev.
- Criar um "conferir se a empresa está nas econômicas anuais", o script receberia uma lista de CNPJs e verificaria se estão na base de econômicas anuais, retornando os que estão.
- Cadastro de divórcios.

- Melhorar fluxo do retornarDMC (não precisa ficar abrindo pnadC toda hora... só a primeira vez).

#############
'''

colorama.init(autoreset=True)  # Inicializa o colorama para garantir cores no terminal Windows

def limpar_credenciais_criptografadas():
    """
    Remove os arquivos de credenciais e chave de criptografia salvos localmente e exibe o resultado em caixa de diálogo.
    """
    import os
    from automacoes.utils import CAMINHO_ARQUIVO_CHAVE
    from automacoes.caixas_dialogo import exibir_caixa_dialogo
    arquivos_removidos = []
    for caminho in [CAMINHO_ARQUIVO_CHAVE]:
        if os.path.exists(caminho):
            os.remove(caminho)
            arquivos_removidos.append(caminho)
    if arquivos_removidos:
        mensagem = "Credenciais e chave de criptografia removidas com sucesso:\n" + "\n".join(f"- {arq}" for arq in arquivos_removidos)
        exibir_caixa_dialogo("Limpeza de Credenciais", mensagem, tipo="sucesso")
    else:
        exibir_caixa_dialogo("Limpeza de Credenciais", "Nenhum arquivo de credencial ou chave encontrado para remover.", tipo="info")


if __name__ == "__main__":
    # Se desejar iniciar pela interface gráfica, descomente a linha abaixo:
    iniciar_interface()    