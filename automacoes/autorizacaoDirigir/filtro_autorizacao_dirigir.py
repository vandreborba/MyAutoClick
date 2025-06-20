import os
import glob
import time
import pandas as pd
import datetime

def obter_arquivo_relatorio_mais_recente(pasta_downloads=None, timeout=120, aguardar_download=True, minutos_max=30):
    """
    Procura o arquivo mais recente que começa com 'RelValidadeCNH' e termina com .xls ou .xlsx na pasta Downloads.
    Aguarda até o arquivo aparecer ou até o tempo limite (timeout).
    Se aguardar_download=True, espera o arquivo ser baixado completamente (sem .crdownload).
    Só retorna arquivos modificados nos últimos 'minutos_max' minutos.
    Retorna o caminho do arquivo encontrado ou None.
    """
    if not pasta_downloads:
        pasta_downloads = os.path.join(os.path.expanduser('~'), 'Downloads')
    padrao = os.path.join(pasta_downloads, 'RelValidadeCNH*.xls*')
    tempo_inicial = time.time()
    arquivo_encontrado = None
    while time.time() - tempo_inicial < timeout:
        arquivos = glob.glob(padrao)
        # Remove arquivos temporários de download
        arquivos_validos = [a for a in arquivos if not a.endswith('.crdownload') and os.path.exists(a)]
        # Filtra por data de modificação (últimos minutos_max minutos)
        agora = time.time()
        arquivos_validos = [a for a in arquivos_validos if (agora - os.path.getmtime(a)) <= minutos_max*60]
        if arquivos_validos:
            # Seleciona o arquivo mais recente
            arquivo_encontrado = max(arquivos_validos, key=os.path.getctime)
            # Se for para aguardar download, verifica se não existe o .crdownload correspondente
            if aguardar_download:
                if not os.path.exists(arquivo_encontrado + '.crdownload'):
                    break
                else:
                    print(f"[INFO] Aguardando download finalizar: {arquivo_encontrado}.crdownload")
            else:
                break
        else:
            print("[INFO] Nenhum arquivo de relatório recente encontrado ainda. Aguardando...")
        time.sleep(5)  # Aguarda 1 segundo antes de tentar novamente
    if not arquivo_encontrado or not os.path.exists(arquivo_encontrado):
        print("[ERRO] Arquivo de relatório não encontrado ou não disponível para leitura.")
        return None
    return arquivo_encontrado

def processar_dados(dados, siapes):
    """
    Processa os dados do relatório, filtrando por SIAPEs e status 'PEDIDO_CONCLUIDO',
    calcula o tempo restante para o vencimento da CNH e salva o resultado em Excel.
    Parâmetros:
        dados: dicionário de DataFrames lido pelo pandas (sheet_name=None)
        siapes: lista de SIAPEs a serem filtrados (inteiros ou strings)
    """
    # Concatena todos os DataFrames das abas do arquivo
    if isinstance(dados, dict):
        lista_df = [df for df in dados.values()]
        dados = pd.concat(lista_df, axis=0, ignore_index=True)
    else:
        # Caso já seja um DataFrame
        dados = dados

    # Seleciona e renomeia as colunas relevantes
    colunas_esperadas = ['Nome Condutor','SIAPE Condutor','Unnamed: 2','Unnamed: 14','Unnamed: 12']
    dados = dados[colunas_esperadas].dropna()
    dados.columns = ['condutor', 'siape','status','Validade CNH', 'data_fim']
    dados.reset_index(drop=True, inplace=True)

    # Trata SIAPE para garantir que seja inteiro
    dados['siape'] = dados['siape'].apply(lambda x: int(str(x).split('.')[0]))

    # Filtra apenas SIAPEs informados e status 'PEDIDO_CONCLUIDO'
    dados = dados[dados['siape'].isin([int(s) for s in siapes]) & (dados['status'] == 'PEDIDO_CONCLUIDO')]

    # Calcula dias restantes para o vencimento da CNH
    tempo_restante = []
    for data in dados['data_fim']:
        try:
            dia, mes, ano = map(int, str(data).split('/'))
            dias = (datetime.date(ano, mes, dia) - datetime.date.today()).days
            if dias <= 0:
                tempo_restante.append('VENCIDO')
            else:
                tempo_restante.append(dias)
        except Exception:
            tempo_restante.append('ERRO_DATA')

    dados['Dias restantes'] = tempo_restante
    dados.drop_duplicates('siape', keep='last', inplace=True)
    dados = dados[['condutor', 'siape', 'Validade CNH', 'data_fim', 'Dias restantes']]
    dados.columns = ['Funcionário', 'Siape', 'Validade CNH', 'Vencimento', 'Dias restantes']
    dados.sort_values('Funcionário', inplace=True)

    # Exibe e salva os resultados
    print(f'Tabela geral:\n{dados.to_string(index=False)}\n\n\n\n')
    # Salva o arquivo Excel no Desktop do usuário
    caminho_desktop = os.path.join(os.path.expanduser('~'), 'Desktop', 'Vencimento Carteiras.xlsx')
    dados.to_excel(caminho_desktop, index=False)
    # Copia o conteúdo do DataFrame para a área de transferência, facilitando a colagem no Excel
    dados.to_clipboard(index=False, excel=True)

    # Exibe o resultado final em uma caixa de diálogo estilizada
    from automacoes.caixas_dialogo import exibir_caixa_dialogo
    vencidos = dados[dados['Dias restantes'] == 'VENCIDO']
    if not vencidos.empty:
        nomes_vencidos = '\n'.join(vencidos['Funcionário'].tolist())
    else:
        nomes_vencidos = 'Nenhum servidor com carteira vencida.'
    mensagem = (
        'Conteúdo do relatório copiado para a área de transferência (formato Excel).\n'
        'Arquivo salvo na área de trabalho como "Vencimento Carteiras.xlsx".\n\n'
        'Os seguintes servidores estão com a carteira vencida:\n\n'
        f'{nomes_vencidos}'
    )
    exibir_caixa_dialogo(
        titulo="Relatório de CNH - Vencidos",
        mensagem=mensagem,
        tipo="info"
    )

def filtrar(lista_siapes):
    """
    Lê o arquivo de relatório mais recente baixado e executa o filtro desejado.
    Garante que o download do arquivo esteja completo antes de processar.
    """
    # Obtém o arquivo mais recente de relatório
    caminho_arquivo = obter_arquivo_relatorio_mais_recente()
    if not caminho_arquivo:
        print("[ERRO] Arquivo de relatório não encontrado na pasta Downloads.")
        return
    # Aguarda o término do download caso ainda exista o arquivo .crdownload
    while os.path.exists(caminho_arquivo + '.crdownload'):
        print(f"[INFO] Aguardando download finalizar: {caminho_arquivo}.crdownload")
        time.sleep(1)
    print(f"[INFO] Lendo arquivo: {caminho_arquivo}")
    dados = pd.read_excel(caminho_arquivo, None)
    processar_dados(dados, lista_siapes)
