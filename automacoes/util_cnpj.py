"""
Módulo utilitário para manipulação e validação de CNPJs.
Todas as funções relacionadas a CNPJ devem ser centralizadas aqui.
"""
import re

# Função para limpar e padronizar CNPJs, removendo pontos, barras e traços
def limpar_cnpj(cnpj):
    """
    Remove todos os caracteres não numéricos de um CNPJ.
    Parâmetros:
        cnpj (str): CNPJ possivelmente formatado.
    Retorna:
        str: CNPJ apenas com números (14 dígitos) ou string vazia se inválido.
    """
    if not isinstance(cnpj, str):
        return ''
    cnpj_numeros = re.sub(r'\D', '', cnpj)
    if len(cnpj_numeros) == 14:
        return cnpj_numeros
    return ''

# Função para processar uma lista de CNPJs (um por linha ou separados por vírgula)
def processar_lista_cnpjs(texto):
    """
    Recebe um texto com múltiplos CNPJs (um por linha ou separados por vírgula) e retorna uma lista de CNPJs limpos e válidos.
    Parâmetros:
        texto (str): Texto contendo CNPJs.
    Retorna:
        list: Lista de CNPJs (apenas números, 14 dígitos).
    """
    if not isinstance(texto, str):
        return []
    # Divide por vírgula ou quebra de linha
    candidatos = re.split(r'[\n,;]+', texto)
    cnpjs = []
    for c in candidatos:
        cnpj_limpo = limpar_cnpj(c)
        if cnpj_limpo:
            cnpjs.append(cnpj_limpo)
    return cnpjs

def extrair_raiz_cnpj(cnpj):
    """
    Extrai a raiz do CNPJ (8 primeiros dígitos antes da barra).
    Parâmetros:
        cnpj (str): CNPJ limpo (apenas números ou formatado).
    Retorna:
        str: Raiz do CNPJ (8 dígitos) ou string vazia se inválido.
    """
    if not isinstance(cnpj, str):
        return ''
    cnpj_numeros = re.sub(r'\D', '', cnpj)
    if len(cnpj_numeros) >= 8:
        return cnpj_numeros[:8]
    return ''

# Função para processar uma lista de CNPJs e retornar apenas as raízes
# Comentário: Garante que a lista retornada contenha apenas as raízes dos CNPJs válidos, sem duplicidade.
def processar_lista_raiz_cnpjs(texto):
    """
    Recebe um texto com múltiplos CNPJs e retorna uma lista das raízes (8 dígitos) únicas.
    Parâmetros:
        texto (str): Texto contendo CNPJs.
    Retorna:
        list: Lista de raízes de CNPJs (8 dígitos).
    """
    if not isinstance(texto, str):
        return []
    candidatos = re.split(r'[\n,;]+', texto)
    raizes = set()
    for c in candidatos:
        raiz = extrair_raiz_cnpj(c)
        if raiz and len(raiz) == 8:
            raizes.add(raiz)
    return list(raizes)
