import tkinter as tk
from tkinter import ttk
from automacoes.caixas_dialogo import exibir_caixa_dialogo
import datetime

def solicitar_mes_ano_interface():
    """
    Exibe uma interface gráfica para o usuário selecionar mês e ano de forma intuitiva.
    Retorna:
        tuple: (mes, ano) como strings, ou (None, None) se cancelado.
    """
    resultado = {"mes": None, "ano": None}

    def confirmar():
        mes = combo_mes.get()
        ano = entry_ano.get().strip()
        if not mes or not ano or not ano.isdigit() or len(ano) != 4:
            exibir_caixa_dialogo("Atenção", "Informe um mês e um ano válidos (ex: Maio, 2025).", tipo="erro")
            return
        resultado["mes"] = str(int(meses.index(mes) + 1))  # mês como número sem zero à esquerda
        resultado["ano"] = ano
        janela.destroy()

    janela = tk.Toplevel()
    janela.title("Selecione Mês e Ano")
    janela.geometry("340x220")
    janela.configure(bg="#f0f4f7")
    janela.grab_set()
    janela.transient(janela.master)
    janela.lift()
    janela.attributes('-topmost', True)

    label = tk.Label(janela, text="Selecione o mês e informe o ano:", font=("Segoe UI", 11, "bold"), bg="#f0f4f7", fg="#0077b6")
    label.pack(pady=(22, 8))

    frame = tk.Frame(janela, bg="#f0f4f7")
    frame.pack(pady=8)

    meses = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
    tk.Label(frame, text="Mês:", font=("Segoe UI", 10), bg="#f0f4f7").grid(row=0, column=0, sticky="e", padx=(0, 6))
    combo_mes = ttk.Combobox(frame, values=meses, font=("Segoe UI", 10), state="readonly", width=16)
    combo_mes.grid(row=0, column=1, pady=4)

    tk.Label(frame, text="Ano:", font=("Segoe UI", 10), bg="#f0f4f7").grid(row=1, column=0, sticky="e", padx=(0, 6))
    entry_ano = ttk.Entry(frame, font=("Segoe UI", 10), width=10)
    entry_ano.grid(row=1, column=1, pady=4)

    hoje = datetime.date.today()
    mes_atual = hoje.month
    ano_atual = hoje.year

    combo_mes.current(mes_atual - 1)
    entry_ano.insert(0, str(ano_atual))

    btn_ok = ttk.Button(janela, text="OK", command=confirmar)
    btn_ok.pack(pady=18)
    combo_mes.focus_set()
    janela.bind('<Return>', lambda e: confirmar())
    janela.wait_window()

    return resultado["mes"], resultado["ano"]
