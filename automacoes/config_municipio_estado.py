# Classe para manipulação de configurações de município e estado
import os
import json

class ConfiguracaoMunicipioEstado:
    """
    Classe responsável por salvar, carregar e alterar as configurações de município e estado.
    As configurações são persistidas em um arquivo JSON.
    """
    CAMINHO_ARQUIVO = os.path.join(os.path.dirname(__file__), 'config_municipio_estado.json')

    def __init__(self):
        # Valores padrão
        self.estado = "41 - PARANÁ"
        self.municipio = "411520000 - Maringá"
        self.carregar()

    def salvar(self):
        """Salva as configurações atuais no arquivo JSON."""
        dados = {
            'estado': self.estado,
            'municipio': self.municipio
        }
        with open(self.CAMINHO_ARQUIVO, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)

    def carregar(self):
        """Carrega as configurações do arquivo JSON, se existir."""
        if os.path.exists(self.CAMINHO_ARQUIVO):
            try:
                with open(self.CAMINHO_ARQUIVO, 'r', encoding='utf-8') as f:
                    dados = json.load(f)
                    self.estado = dados.get('estado', self.estado)
                    self.municipio = dados.get('municipio', self.municipio)
            except Exception as e:
                print(f"[ERRO] Falha ao carregar configurações: {e}")

    def alterar(self, novo_estado, novo_municipio):
        """Altera os valores de estado e município e salva automaticamente."""
        self.estado = novo_estado
        self.municipio = novo_municipio
        self.salvar()

# Instância global para uso em todo o sistema
config_municipio_estado = ConfiguracaoMunicipioEstado()
