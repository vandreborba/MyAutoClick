import logging
import os

# Caminho do arquivo de log (na pasta do usuário, subpasta oculta .myautoclicker)
PASTA_LOG = os.path.join(os.path.expanduser('~'), '.myautoclicker')
if not os.path.exists(PASTA_LOG):
    os.makedirs(PASTA_LOG)
CAMINHO_LOG = os.path.join(PASTA_LOG, 'myautoclicker.log')

# Configuração básica do logging
logging.basicConfig(
    level=logging.INFO,  # Nível padrão para o arquivo de log
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(CAMINHO_LOG, encoding='utf-8'),
        logging.StreamHandler()  # Console (ajustado abaixo)
    ]
)

# Reduz o nível do console para WARNING (apenas avisos e erros aparecem para o usuário)
logging.getLogger().handlers[1].setLevel(logging.WARNING)

# Reduz verbosidade do Selenium e urllib3
for lib in ['selenium', 'urllib3', 'httpx']:
    logging.getLogger(lib).setLevel(logging.ERROR)

# Função utilitária para obter logger

def obter_logger(nome=None):
    return logging.getLogger(nome)

# Exemplo de uso:
# logger = obter_logger(__name__)
# logger.info('Mensagem informativa')
# logger.error('Mensagem de erro')
