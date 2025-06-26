import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import colorama
from automacoes.config_interface import VERSAO_SISTEMA, INSTRUCOES_SISTEMA, executar_opcao

# Função para exibir o menu principal na interface gráfica
def exibir_interface_principal():
    janela = tk.Tk()
    janela.title(f"My IBGE Auto Clicker v{VERSAO_SISTEMA}")
    janela.geometry("800x650")  # Janela maior para melhor visualização
    janela.configure(bg="#f0f4f7")

    # Título
    titulo = tk.Label(
        janela,
        text=f"My IBGE Auto Clicker v{VERSAO_SISTEMA}",
        font=("Segoe UI", 18, "bold"),  # Fonte menor
        fg="#ffffff",
        bg="#0077b6",
        pady=15
    )
    titulo.pack(fill="x")

    # Exibe o ícone do programa no topo da interface
    try:
        from PIL import Image, ImageTk
        import os
        import sys
        if hasattr(sys, '_MEIPASS'):
            # Executando via PyInstaller
            caminho_icone = os.path.join(sys._MEIPASS, 'icon.ico')
        else:
            # Executando via script normal
            caminho_icone = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'icon.ico')
        if os.path.exists(caminho_icone):
            imagem_icone = Image.open(caminho_icone)
            imagem_icone = imagem_icone.resize((48, 48), Image.LANCZOS)
            icone_tk = ImageTk.PhotoImage(imagem_icone)
            label_icone = tk.Label(janela, image=icone_tk, bg="#0077b6")
            label_icone.image = icone_tk  # Mantém referência
            label_icone.place(x=20, y=10)
    except Exception as e:
        pass  # Se não conseguir exibir o ícone, apenas ignora

    # Instruções (em um frame com borda)
    frame_instrucoes = tk.Frame(janela, bg="#caf0f8", bd=2, relief="groove")
    frame_instrucoes.pack(pady=8, padx=24, fill="x")
    instrucoes = tk.Label(
        frame_instrucoes,
        text=INSTRUCOES_SISTEMA,
        font=("Segoe UI", 9),  # Fonte menor
        fg="#495057",
        bg="#caf0f8",
        justify="left",
        anchor="w"
    )
    instrucoes.pack(padx=8, pady=6, fill="x")

    # Frame para botões (com fundo branco e sombra)
    frame_botoes = tk.Frame(janela, bg="#ffffff", bd=3, relief="ridge")
    frame_botoes.pack(pady=12, padx=24, fill="both", expand=True)

    # Dicionário de opções do menu
    opcoes = {
        "Econômicas": [
            ("Download Relatórios Mensais", "10"),
            ("Conferir Rais", "11")
        ],
        "PnadC": [
            ("Liberar Codificação (Todos)", "20"),
            ("Cancelar Liberação Codificação", "21"),
            ("Baixar Questionários", "22"),
            ("Associar Entrevistas", "23"),
            ("Retornar ao DMC", "24")
        ],
        "Administração": [
            ("Autorização para Dirigir", "30")
        ],
        "Outros": [
            ("Configurar Município e Estado", "98"),
            ("Limpar credenciais salvas", "99"),
            ("Sair", "0")
        ]
    }

    def ao_clicar_opcao(codigo):
        # Função chamada ao clicar em um botão do menu
        if codigo == "0":
            janela.destroy()
        else:
            try:
                resultado = executar_opcao(codigo)
                if resultado is False:
                    janela.destroy()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao executar opção: {e}")

    # Criação dos botões de menu em três colunas
    colunas = 3
    linha = 0
    for secao, lista_opcoes in opcoes.items():
        label_secao = tk.Label(
            frame_botoes,
            text=secao,
            font=("Segoe UI", 11, "bold"),  # Fonte menor
            fg="#0096c7",
            bg="#ffffff",
            pady=4
        )
        label_secao.grid(row=linha, column=0, columnspan=colunas, sticky="w", pady=(12, 0), padx=8)
        linha += 1
        for idx, (texto, codigo) in enumerate(lista_opcoes):
            col = idx % colunas
            row = linha + idx // colunas
            btn = ttk.Button(
                frame_botoes,
                text=texto,
                width=28,
                style="Modern.TButton",
                command=lambda c=codigo: ao_clicar_opcao(c)
            )
            btn.grid(row=row, column=col, sticky="w", pady=3, padx=12)
        linha += (len(lista_opcoes) + colunas - 1) // colunas

    # Estilo moderno para os botões
    style = ttk.Style()
    style.theme_use('clam')
    style.configure(
        "Modern.TButton",
        font=("Segoe UI", 9, "bold"),  # Fonte menor
        foreground="#ffffff",
        background="#00b4d8",
        borderwidth=0,
        focusthickness=2,
        focuscolor="#90e0ef",
        padding=6
    )
    style.map(
        "Modern.TButton",
        background=[('active', '#0096c7'), ('pressed', '#0077b6')],
        foreground=[('disabled', '#adb5bd')]
    )

    janela.mainloop()

# Função para iniciar a interface gráfica
def iniciar_interface():
    exibir_interface_principal()
