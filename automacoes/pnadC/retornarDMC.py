# Método para retornar a entrevista a um DMC.
from automacoes import util_selenium
from automacoes.pnadC import baixarQuestionario, cancelarCodificacao, liberarCodificacao
from automacoes.caixas_dialogo import solicitar_texto_multilinha, exibir_caixa_dialogo
from automacoes.pnadC import associarEntrevistas

def solicitar_lista():
    """
    Solicita ao usuário a lista de setores, domicílios e SIAPE (opcional),
    aceitando apenas uma combinação de setor, domicílio e SIAPE (opcional) por linha.
    Realiza validação do formato da entrada e exibe aviso para linhas inválidas,
    mas retorna o texto bruto informado pelo usuário, sem processamento.
    """
    mensagem = (
        "Cole a lista de setores, domicílios e SIAPE (numeroSetor numeroDomicilio [siapeEntrevistador]),\n"
        "separados por espaço ou tabulação, uma linha por registro.\n\nExemplo:\n410730605000009 1 1234567\n412625605000054 2 7654321"
    )
    texto = solicitar_texto_multilinha(
        titulo="Setores, Domicílios e SIAPE",
        mensagem=mensagem,
        texto_exemplo=""
    )    

    # Validação apenas para avisar sobre linhas inválidas
    linhas_invalidas = []
    if texto:
        linhas = texto.strip().split('\n')
        for i, linha in enumerate(linhas, 1):
            partes = linha.strip().split()
            if not (len(partes) == 2 or len(partes) == 3):
                if linha.strip() != '':
                    linhas_invalidas.append(f"Linha {i}: {linha}")
            else:
                # Verifica se setor e domicílio são numéricos
                if not (partes[0].isdigit() and partes[1].isdigit() and (len(partes) == 2 or partes[2].isdigit())):
                    linhas_invalidas.append(f"Linha {i}: {linha}")
    if linhas_invalidas:
        mensagem_erro = (
            "Algumas linhas estão em formato inválido e foram ignoradas:\n\n" +
            '\n'.join(linhas_invalidas) +
            "\n\nO formato correto é: numeroSetor numeroDomicilio [siapeEntrevistador]"
        )
        exibir_caixa_dialogo(
            titulo="Linhas inválidas",
            mensagem=mensagem_erro
        )
    return texto

def remover_siape_das_linhas(texto_lista):
    """
    Recebe o texto da lista (várias linhas) e remove o SIAPE (terceiro elemento) de cada linha, se existir.
    Retorna uma string, cada linha no formato: numeroSetor numeroDomicilio, separadas por '\n'.
    """
    linhas_sem_siape = []
    if texto_lista:
        linhas = texto_lista.strip().split('\n')
        for linha in linhas:
            partes = linha.strip().split()
            # Mantém apenas setor e domicílio se houver pelo menos dois elementos
            if len(partes) >= 2:
                linhas_sem_siape.append(f"{partes[0]} {partes[1]}")
    return '\n'.join(linhas_sem_siape)

def executar():
    """
    Executa o fluxo de retorno DMC: cancela codificação e associa entrevistas, usando a lista já pronta.
    """
    # Solicita a lista:
    lista_dados = solicitar_lista()
    if not lista_dados:
        return  # Se a lista estiver vazia, não faz nada
    # criar lista sem siape:
    lista_sem_siape = remover_siape_das_linhas(lista_dados)    
    

    # Solicita mês e ano apenas uma vez
    mes, ano = liberarCodificacao.solicitar_mes_ano()
    
    driver = util_selenium.inicializar_webdriver_com_perfil()

    if lista_sem_siape and lista_dados:
        driver = cancelarCodificacao.executar(mes, ano, lista_sem_siape, driver, fechar_driver=False)    
        driver = associarEntrevistas.executar(lista_dados, driver, fechar_driver=False)
        baixarQuestionario.executar(mes, ano, lista_sem_siape, driver)

    print("Processamento concluído com sucesso.")


