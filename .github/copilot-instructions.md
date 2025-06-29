# Diretrizes para o GitHub Copilot

## Organização do Código
- **Separação por Funções:** Sempre que possível, separe a lógica em funções pequenas, reutilizáveis e com responsabilidade única.
- **Arquivos Auxiliares:** Crie e utilize arquivos auxiliares para centralizar funcionalidades específicas (ex: manipulação de arquivos, tratamento de dados, utilitários de interface, etc.), evitando códigos longos e monolíticos.
- **Modularização:** Prefira importar funções de módulos auxiliares ao invés de duplicar código.

## Convenções de Nomeação
- **Funções e Variáveis:** Todos os nomes de funções e variáveis devem ser escritos em português e descritivos, refletindo claramente sua finalidade.

## Comentários no Código
- **Explicativos:** Sempre inclua comentários explicativos no código para descrever a lógica, o propósito e o funcionamento de trechos específicos.
- **Manutenção:** Certifique-se de que os comentários sejam atualizados ao modificar o código.

## Boas Práticas
- **Clareza:** Priorize a clareza e a legibilidade do código.
- **Consistência:** Siga um estilo de codificação consistente em todo o projeto.

## Dependências
- **Atualização do requirements.txt:** Sempre que uma nova biblioteca for instalada, certifique-se de adicioná-la ao arquivo `requirements.txt` para manter as dependências do projeto atualizadas.

## Selenium Utilities
- **Centralização de Funções:** Todas as funções relacionadas ao Selenium devem ser centralizadas no arquivo `util_selenium.py` para facilitar a reutilização e manutenção.
- **Boas Práticas:** Utilize as funções de `util_selenium.py` sempre que possível para evitar duplicação de código.

## Imports
- **Localização:** Sempre coloque todos os imports no início do arquivo, exceto quando houver uma justificativa técnica clara para importar dentro de funções (ex: evitar dependências circulares, otimizar carregamento condicional, etc.).

## Diálogos e Interação com o Usuário
- **Centralização de Diálogos:** Todas as solicitações, avisos e caixas de diálogo para o usuário devem ser feitas exclusivamente pelo arquivo `automacoes/caixas_dialogo.py`, garantindo padronização visual e centralização da comunicação com o usuário.

# Para compilar o projeto e gerar um único arquivo .exe na pasta 'dist' e copiar para a área de trabalho, execute:
#
# Opção recomendada (PowerShell):
#
#   powershell -ExecutionPolicy Bypass -File .\compilar_e_copiar.ps1
#
#
# O executável será gerado na pasta 'dist' do projeto e uma cópia será feita para a área de trabalho.
# Utilize este comando sempre que solicitar a compilação do projeto com ícone personalizado.