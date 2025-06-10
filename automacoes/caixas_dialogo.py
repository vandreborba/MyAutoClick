import tkinter as tk
from tkinter import ttk

# Todas as solicitações, avisos e caixas de diálogo para o usuário devem ser feitas exclusivamente pelo arquivo automacoes/caixas_dialogo.py, garantindo padronização visual e centralização da comunicação com o usuário.

# Função utilitária para exibir uma caixa de diálogo personalizada
# Todas as solicitações e avisos ao usuário devem ser feitas por aqui

def exibir_caixa_dialogo(titulo, mensagem, tipo="info"):
    """
    Exibe uma caixa de diálogo estilizada para avisos, erros ou confirmações.
    O tamanho da janela é ajustado dinamicamente conforme o tamanho da mensagem.
    Parâmetros:
        titulo (str): Título da janela de diálogo.
        mensagem (str): Mensagem a ser exibida.
        tipo (str): 'info', 'erro' ou 'sucesso'.
    """
    import textwrap
    dialogo = tk.Toplevel()
    dialogo.title(titulo)
    dialogo.configure(bg="#f0f4f7")
    dialogo.resizable(False, False)
    dialogo.grab_set()  # Modal

    # Cores e ícones por tipo
    cores = {
        "info": ("#0077b6", "ℹ️"),
        "erro": ("#d90429", "❌"),
        "sucesso": ("#43aa8b", "✔️")
    }
    cor, icone = cores.get(tipo, ("#0077b6", "ℹ️"))

    # Ícone
    label_icone = tk.Label(dialogo, text=icone, font=("Segoe UI", 32), bg="#f0f4f7", fg=cor)
    label_icone.pack(pady=(18, 0))

    # Mensagem
    # Calcula largura e altura ideais
    linhas = mensagem.split('\n')
    max_linha = max((len(l) for l in linhas), default=40)
    largura = min(max(340, max_linha * 8), 900)  # 8px por caractere, limite máximo
    n_linhas = len(linhas) + sum(len(l)//80 for l in linhas)  # considera quebras
    altura = min(max(80 + n_linhas * 22, 120), 600)  # Altura mínima/máxima

    label_msg = tk.Label(dialogo, text=mensagem, font=("Segoe UI", 11), bg="#f0f4f7", fg="#222", wraplength=largura, justify="center")
    label_msg.pack(pady=(10, 0), padx=18)

    # Botão OK estilizado
    style = ttk.Style()
    style.theme_use('clam')
    style.configure(
        "Dialog.TButton",
        font=("Segoe UI", 10, "bold"),
        foreground="#fff",
        background=cor,
        borderwidth=0,
        padding=8
    )
    style.map(
        "Dialog.TButton",
        background=[('active', cor), ('pressed', cor)],
        foreground=[('disabled', '#adb5bd')]
    )

    btn_ok = ttk.Button(dialogo, text="OK", style="Dialog.TButton", command=dialogo.destroy)
    btn_ok.pack(pady=18)
    dialogo.bind('<Return>', lambda e: dialogo.destroy())
    btn_ok.focus_set()
    dialogo.transient(dialogo.master)
    dialogo.lift()  # Traz para frente
    dialogo.attributes('-topmost', True)  # Mantém no topo

    # Define tamanho dinâmico
    dialogo.update_idletasks()
    largura_final = max(label_msg.winfo_reqwidth() + 60, 340)
    altura_final = max(label_icone.winfo_reqheight() + label_msg.winfo_reqheight() + btn_ok.winfo_reqheight() + 90, altura)
    dialogo.geometry(f"{largura_final}x{altura_final}")

    dialogo.wait_window()

def solicitar_credenciais_interface(nome_sistema=""):
    """
    Solicita ao usuário o login e a senha usando interface gráfica, com opção de salvar e reutilizar as credenciais criptografadas.
    Retorna:
        tuple: Uma tupla contendo o login e a senha fornecidos pelo usuário.
    """
    import os
    from automacoes.utils import carregar_credenciais_criptografadas, salvar_credenciais_criptografadas
    import tkinter as tk
    from tkinter import ttk

    # Tenta carregar credenciais salvas para o sistema
    login, senha = carregar_credenciais_criptografadas(nome_sistema)
    if login and senha:
        return login, senha

    # Cria janela modal para solicitar login e senha
    root = tk.Toplevel()
    root.title(f"Credenciais - {nome_sistema}")
    root.geometry("400x240")
    root.configure(bg="#f0f4f7")
    root.resizable(False, False)
    root.grab_set()
    root.transient(root.master)
    root.lift()
    root.attributes('-topmost', True)

    ttk.Style().theme_use('clam')

    label_titulo = tk.Label(root, text=f"Acesso ao sistema {nome_sistema}", font=("Segoe UI", 13, "bold"), bg="#f0f4f7", fg="#0077b6")
    label_titulo.pack(pady=(18, 6))

    frame = tk.Frame(root, bg="#f0f4f7")
    frame.pack(pady=8, padx=18, fill="x")

    tk.Label(frame, text="Login:", font=("Segoe UI", 10), bg="#f0f4f7").grid(row=0, column=0, sticky="w", pady=4)
    entry_login = ttk.Entry(frame, font=("Segoe UI", 10))
    entry_login.grid(row=0, column=1, pady=4, padx=6)

    tk.Label(frame, text="Senha:", font=("Segoe UI", 10), bg="#f0f4f7").grid(row=1, column=0, sticky="w", pady=4)
    entry_senha = ttk.Entry(frame, font=("Segoe UI", 10), show="*")
    entry_senha.grid(row=1, column=1, pady=4, padx=6)

    resultado = {"login": None, "senha": None}

    def confirmar():
        resultado["login"] = entry_login.get().strip()
        resultado["senha"] = entry_senha.get().strip()
        if resultado["login"] and resultado["senha"]:
            root.destroy()
        else:
            exibir_caixa_dialogo("Atenção", "Preencha login e senha.", tipo="erro")

    btn_ok = ttk.Button(root, text="OK", style="Dialog.TButton", command=confirmar)
    btn_ok.pack(pady=36)
    entry_login.focus_set()
    root.bind('<Return>', lambda e: confirmar())
    root.wait_window()

    login, senha = resultado["login"], resultado["senha"]
    if login and senha:
        salvar_credenciais_criptografadas(login, senha, nome_sistema)
        return login, senha
    return None, None

def solicitar_texto_multilinha(titulo, mensagem, texto_exemplo=None):
    """
    Exibe uma caixa de diálogo para o usuário colar/editar um texto multilinha.
    Retorna o texto informado (ou None se cancelado).
    """
    import tkinter as tk
    from tkinter import ttk
    
    # Dicionário para armazenar o resultado
    resultado = {"texto": None}

    def confirmar():
        texto = text_input.get("1.0", tk.END).strip()
        if not texto:
            exibir_caixa_dialogo("Atenção", "O campo não pode estar vazio.", tipo="erro")
            return
        resultado["texto"] = texto
        janela.destroy()

    # Criação da janela principal
    janela = tk.Toplevel()
    janela.title(titulo)
    janela.geometry("520x420")
    janela.configure(bg="#f0f4f7")
    janela.grab_set()
    janela.transient(janela.master)
    janela.lift()
    janela.attributes('-topmost', True)

    # Label de instrução com quebra automática de linha
    label = tk.Label(janela, text=mensagem, font=("Segoe UI", 10), bg="#f0f4f7", fg="#0077b6", justify="left", wraplength=440)
    label.pack(pady=(18, 6), padx=12, anchor="w")

    # Frame para o campo de texto e scrollbar
    frame_texto = tk.Frame(janela, bg="#f0f4f7")
    frame_texto.pack(padx=16, pady=6, fill="both", expand=True)

    # Scrollbar vertical
    scrollbar = tk.Scrollbar(frame_texto)
    scrollbar.pack(side="right", fill="y")

    # Campo de texto multilinha com quebra automática de linha por palavra
    text_input = tk.Text(frame_texto, height=12, font=("Consolas", 11), wrap="word", bg="#fff", fg="#222", borderwidth=2, relief="groove", yscrollcommand=scrollbar.set)
    text_input.pack(side="left", fill="both", expand=True)
    scrollbar.config(command=text_input.yview)

    if texto_exemplo:
        text_input.insert("1.0", texto_exemplo)

    # Frame para o botão OK, fixando-o na parte inferior
    frame_botoes = tk.Frame(janela, bg="#f0f4f7")
    frame_botoes.pack(fill="x", side="bottom", pady=(0, 14))

    btn_ok = ttk.Button(frame_botoes, text="OK", command=confirmar)
    btn_ok.pack(pady=0)
    text_input.focus_set()
    janela.bind('<Return>', lambda e: confirmar())
    janela.wait_window()

    return resultado["texto"]

def solicitar_config_municipio_estado(estado_atual, municipio_atual):
    """
    Exibe uma interface gráfica para o usuário informar o Estado e Município.
    Retorna (novo_estado, novo_municipio) ou (None, None) se cancelado.
    """
    import tkinter as tk
    from tkinter import ttk
    resultado = {"estado": estado_atual, "municipio": municipio_atual}

    def confirmar():
        estado = entry_estado.get().strip()
        municipio = entry_municipio.get().strip()
        if not estado or not municipio:
            exibir_caixa_dialogo("Atenção", "Preencha o Estado e o Município.", tipo="erro")
            return
        resultado["estado"] = estado
        resultado["municipio"] = municipio
        janela.destroy()

    janela = tk.Toplevel()
    janela.title("Configurar Município e Estado")
    janela.geometry("420x220")
    janela.configure(bg="#f0f4f7")
    janela.grab_set()
    janela.transient(janela.master)
    janela.lift()
    janela.attributes('-topmost', True)

    label = tk.Label(janela, text="Informe o Estado e o Município:", font=("Segoe UI", 11, "bold"), bg="#f0f4f7", fg="#0077b6")
    label.pack(pady=(22, 8))

    frame = tk.Frame(janela, bg="#f0f4f7")
    frame.pack(pady=8)

    tk.Label(frame, text="Estado:", font=("Segoe UI", 10), bg="#f0f4f7").grid(row=0, column=0, sticky="e", padx=(0, 6))
    entry_estado = ttk.Entry(frame, font=("Segoe UI", 10), width=20)
    entry_estado.grid(row=0, column=1, pady=4)
    entry_estado.insert(0, estado_atual)

    tk.Label(frame, text="Município:", font=("Segoe UI", 10), bg="#f0f4f7").grid(row=1, column=0, sticky="e", padx=(0, 6))
    entry_municipio = ttk.Entry(frame, font=("Segoe UI", 10), width=20)
    entry_municipio.grid(row=1, column=1, pady=4)
    entry_municipio.insert(0, municipio_atual)

    btn_ok = ttk.Button(janela, text="OK", command=confirmar)
    btn_ok.pack(pady=18)
    entry_estado.focus_set()
    janela.bind('<Return>', lambda e: confirmar())
    janela.wait_window()

    return resultado["estado"], resultado["municipio"]
