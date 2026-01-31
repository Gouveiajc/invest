'''
Programa de Cadastro de Segmentos
JC 01/2026
Ver 1
Banco de Dados inv.db
Tabela inv01
'''
#Codigo com as Sugestões do Gemini
'''
Lógica do if novo_total > 100: Agora o return acontece imediatamente se o usuário clicar em "Não", evitando o erro de variável não definida.
Tratamento de Erros (try/except/finally): Garante que a conexão com o banco de dados seja fechada (conn.close()) mesmo se o programa travar no meio do processo.
Flexibilidade Numérica: Adicionei .replace(',', '.') para evitar que o programa quebre se o usuário digitar o percentual com vírgula.
Melhoria no to_uppercase: Adicionei icursor(posicao) para que, ao digitar, o cursor não pule para o final do campo toda vez que uma letra for convertida.
'''
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

import inv00_0
import inv00_1

def abrir_janela_inv01(root, tree):
    # Evita abrir mais de uma janela de inclusão
    for widget in root.winfo_children():
        if isinstance(widget, tk.Toplevel) and widget.title() == "Inclusão de Segmentos":
            widget.lift()
            widget.focus_force()
            return

    janela = tk.Toplevel(root)
    janela.title("Inclusão de Segmentos")
    janela.geometry("550x350")

    janela.transient(root)
    janela.grab_set()
    janela.bind("<Escape>", lambda e: janela.destroy())

    frame = ttk.Frame(janela, padding=20)
    frame.pack(fill="both", expand=True)

    # --- CAMPOS ---
    ttk.Label(frame, text="Código:").grid(row=0, column=0, sticky="w", pady=5)
    entry_codigo = ttk.Entry(frame, width=10)
    entry_codigo.grid(row=0, column=1, sticky="w", pady=5)

    ttk.Label(frame, text="Descrição:").grid(row=1, column=0, sticky="w", pady=5)
    entry_descricao = ttk.Entry(frame, width=30)
    entry_descricao.grid(row=1, column=1, sticky="w", pady=5)

    # --- COMBOBOX ---
    ttk.Label(frame, text="Tipo Ativo:").grid(row=2, column=0, sticky="w", pady=5)

    # Busca tipos de ativos com tratamento de erro
    try:
        conn = inv00_0.conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT INV00_01, INV00_02 FROM INV00 ORDER BY INV00_02")
        tipos = cursor.fetchall()
        lista_tipos = [f"{t[0]} - {t[1]}" for t in tipos]
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao carregar tipos: {e}")
        lista_tipos = []
    finally:
        conn.close()

    combo_tipo = ttk.Combobox(frame, values=lista_tipos, state="readonly", width=30)
    combo_tipo.grid(row=2, column=1, sticky="w", pady=5)

    ttk.Label(frame, text="Percentual Ativo:").grid(row=3, column=0, sticky="w", pady=5)
    entry_per = ttk.Entry(frame, width=10)
    entry_per.grid(row=3, column=1, sticky="w", pady=5)

    def to_uppercase(event):
        # Transforma em maiúsculo sem perder a posição do cursor
        posicao = entry_descricao.index(tk.INSERT)
        texto = entry_descricao.get().upper()
        entry_descricao.delete(0, tk.END)
        entry_descricao.insert(0, texto)
        entry_descricao.icursor(posicao)

    entry_descricao.bind("<KeyRelease>", to_uppercase)

    # --- FUNÇÃO SALVAR ---
    def salvar():
        cod = entry_codigo.get().strip()
        desc = entry_descricao.get().strip()
        per = entry_per.get().strip()

        tipo_selecionado = combo_tipo.get()
        if not tipo_selecionado:
            messagebox.showwarning("Atenção", "Selecione um Tipo de Ativo.", parent=janela)
            return

        tipo_id = tipo_selecionado.split(" - ")[0]

        ok, mensagem, campo = inv00_1.validar_campos_inv01(cod, desc, tipo_id, per)
        if not ok:
            messagebox.showwarning("Atenção", mensagem, parent=janela)
            return

        try:
            per_float = float(per.replace(',', '.')) # Aceita vírgula ou ponto
            
            conn = inv00_0.conectar()
            
            # 1. Verifica duplicidade de código
            if inv00_0.existe_codigo_inv01(conn, cod):
                messagebox.showwarning("Atenção", f"O código {cod} já existe.", parent=janela)
                return

            # 2. Verifica soma de percentuais (Correção da lógica do 'continuar')
            soma_atual = inv00_0.soma_perc_tipo(conn, tipo_id)
            novo_total = soma_atual + per_float

            if novo_total > 100:
                msg = f"A soma para o tipo {tipo_id} chegará a {novo_total:.2f}%.\nContinua?"
                if not messagebox.askyesno("Confirmação", msg, parent=janela):
                    return
            
            # 3. Grava registro
            inv00_0.inserir_registro_inv01(conn, cod, desc, tipo_id, per_float)
            
            # 4. Atualiza o Treeview (Inserindo apenas o novo para performance)
            # Se preferir recarregar tudo, mantenha seu loop de delete/insert aqui
            tree.insert("", tk.END, values=(cod, desc, tipo_id, per_float))
            
            messagebox.showinfo("Sucesso", "Registro incluído com sucesso!", parent=janela)

            # Limpa campos e foca no código
            entry_codigo.delete(0, tk.END)
            entry_descricao.delete(0, tk.END)
            combo_tipo.set("")
            entry_per.delete(0, tk.END)
            entry_codigo.focus()

        except ValueError:
            messagebox.showwarning("Atenção", "Percentual deve ser um número.", parent=janela)
        except Exception as e:
            messagebox.showerror("Erro Fatal", f"Erro ao salvar: {e}", parent=janela)
        finally:
            if conn:
                conn.close()

    # --- BOTÕES ---
    frame_botoes = ttk.Frame(janela, padding=10)
    frame_botoes.pack()

    ttk.Button(frame_botoes, text="Salvar", width=12, command=salvar).grid(row=0, column=0, padx=10)
    ttk.Button(frame_botoes, text="Retornar", width=12, command=janela.destroy).grid(row=0, column=1, padx=10)

    entry_codigo.focus()

'''
#Codigo Antes das Sugestões do Gemini.
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

import inv00_0
import inv00_1

def abrir_janela_inv01(root, tree):

    # Evita abrir mais de uma janela de inclusão
    for widget in root.winfo_children():
        if isinstance(widget, tk.Toplevel) and widget.title() == "Inclusão de Segmentos":
            widget.lift()
            widget.focus_force()
            return

    janela = tk.Toplevel(root)
    janela.title("Inclusão de Segmentos")
    janela.geometry("550x350")

    janela.transient(root)
    janela.grab_set()
    janela.bind("<Escape>", lambda e: janela.destroy())

    # -----------------------------
    # CAMPOS
    # -----------------------------
    frame = ttk.Frame(janela, padding=20)
    frame.pack(fill="both", expand=True)

    # Código
    ttk.Label(frame, text="Código:").grid(row=0, column=0, sticky="w", pady=5)
    entry_codigo = ttk.Entry(frame, width=5)
    entry_codigo.grid(row=0, column=1, sticky="w", pady=5)

    # Descrição
    ttk.Label(frame, text="Descrição:").grid(row=1, column=0, sticky="w", pady=5)
    entry_descricao = ttk.Entry(frame, width=30)
    entry_descricao.grid(row=1, column=1, sticky="w", pady=5)

    # -----------------------------
    # COMBOBOX – TIPOS DE ATIVOS
    # -----------------------------
    ttk.Label(frame, text="Tipo Ativo:").grid(row=2, column=0, sticky="w", pady=5)

    conn = inv00_0.conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT INV00_01, INV00_02 FROM INV00 ORDER BY INV00_02")
    tipos = cursor.fetchall()
    conn.close()

    lista_tipos = [f"{t[0]} - {t[1]}" for t in tipos]

    combo_tipo = ttk.Combobox(frame, values=lista_tipos, state="readonly", width=30)
    combo_tipo.grid(row=2, column=1, sticky="w", pady=5)

    # Percentual
    ttk.Label(frame, text="Percentual Ativo:").grid(row=3, column=0, sticky="w", pady=5)
    entry_per = ttk.Entry(frame, width=10)
    entry_per.grid(row=3, column=1, sticky="w", pady=5)

    # Converte descrição para maiúsculas
    def to_uppercase(event):
        texto = entry_descricao.get()
        entry_descricao.delete(0, tk.END)
        entry_descricao.insert(0, texto.upper())

    entry_descricao.bind("<KeyRelease>", to_uppercase)

    # -----------------------------
    # FUNÇÃO SALVAR
    # -----------------------------
    def salvar():
        cod = entry_codigo.get().strip()
        desc = entry_descricao.get().strip()
        per = entry_per.get().strip()

        # Extrai o ID do tipo de ativo selecionado
        tipo_selecionado = combo_tipo.get()
        if tipo_selecionado == "":
            messagebox.showwarning("Atenção", "Selecione um Tipo de Ativo.", parent=janela)
            return

        tipo_id = tipo_selecionado.split(" - ")[0]  # pega o INV00_01

        ok, mensagem, campo = inv00_1.validar_campos_inv01(cod, desc, tipo_id, per)
        if not ok:
            messagebox.showwarning("Atenção", mensagem, parent=janela)
            return

        # -----------------------------
        # VERIFICA SOMA DOS PERCENTUAIS
        # -----------------------------
        try:
            per_float = float(per)
        except:
            messagebox.showwarning("Atenção", "Percentual inválido.", parent=janela)
            return

        conn = inv00_0.conectar()
        soma_atual = inv00_0.soma_perc_tipo(conn, tipo_id)
        conn.close()

        novo_total = soma_atual + per_float

        if novo_total > 100:
            if not messagebox.askyesno("Atenção", f"Soma chegará a {novo_total:.2f}%. Continua?", parent=janela):
                return

        # -----------------------------
        # GRAVA REGISTRO
        # -----------------------------
        conn = inv00_0.conectar()
        if inv00_0.existe_codigo_inv01(conn, cod):
            conn.close()
            messagebox.showwarning("Atenção", f"O código {cod} já está cadastrado.", parent=janela)
            return

        inv00_0.inserir_registro_inv01(conn, cod, desc, tipo_id, per_float)
        conn.close()

        messagebox.showinfo("Sucesso", "Registro incluído com sucesso!", parent=janela)

        # RECARREGA O GRID
        for i in tree.get_children():
            tree.delete(i)

        conn = inv00_0.conectar()
        registros = inv00_0.listar_registros_inv01(conn)
        conn.close()

        for reg in registros:
            tree.insert("", tk.END, values=reg)

        # Limpa campos
        entry_codigo.delete(0, tk.END)
        entry_descricao.delete(0, tk.END)
        combo_tipo.set("")
        entry_per.delete(0, tk.END)

        entry_codigo.focus()

    # -----------------------------
    # BOTÕES
    # -----------------------------
    frame_botoes = ttk.Frame(janela, padding=10)
    frame_botoes.pack()

    ttk.Button(frame_botoes, text="Salvar", width=12, command=salvar).grid(row=0, column=0, padx=10)
    ttk.Button(frame_botoes, text="Retornar", width=12, command=janela.destroy).grid(row=0, column=1, padx=10)

    entry_codigo.focus()
    janela.lift()
    janela.focus_force()

'''
'''
#Versão com Consulta a tabela INV00
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

import inv00_0
import inv00_1

def abrir_janela_inv01(root, tree):

    # Evita abrir mais de uma janela de inclusão
    for widget in root.winfo_children():
        if isinstance(widget, tk.Toplevel) and widget.title() == "Inclusão de Segmentos":
            widget.lift()
            widget.focus_force()
            return

    janela = tk.Toplevel(root)
    janela.title("Inclusão de Segmentos")
    janela.geometry("550x350")

    janela.transient(root)
    janela.grab_set()
    janela.bind("<Escape>", lambda e: janela.destroy())

    # -----------------------------
    # CAMPOS
    # -----------------------------
    frame = ttk.Frame(janela, padding=20)
    frame.pack(fill="both", expand=True)

    # Código
    ttk.Label(frame, text="Código:").grid(row=0, column=0, sticky="w", pady=5)
    entry_codigo = ttk.Entry(frame, width=5)
    entry_codigo.grid(row=0, column=1, sticky="w", pady=5)

    # Descrição
    ttk.Label(frame, text="Descrição:").grid(row=1, column=0, sticky="w", pady=5)
    entry_descricao = ttk.Entry(frame, width=30)
    entry_descricao.grid(row=1, column=1, sticky="w", pady=5)

    # -----------------------------
    # COMBOBOX – TIPOS DE ATIVOS
    # -----------------------------
    ttk.Label(frame, text="Tipo Ativo:").grid(row=2, column=0, sticky="w", pady=5)

    conn = inv00_0.conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT INV00_01, INV00_02 FROM INV00 ORDER BY INV00_02")
    tipos = cursor.fetchall()
    conn.close()

    lista_tipos = [f"{t[0]} - {t[1]}" for t in tipos]

    combo_tipo = ttk.Combobox(frame, values=lista_tipos, state="readonly", width=30)
    combo_tipo.grid(row=2, column=1, sticky="w", pady=5)

    # Percentual
    ttk.Label(frame, text="Percentual Ativo:").grid(row=3, column=0, sticky="w", pady=5)
    entry_per = ttk.Entry(frame, width=10)
    entry_per.grid(row=3, column=1, sticky="w", pady=5)

    # Converte descrição para maiúsculas
    def to_uppercase(event):
        texto = entry_descricao.get()
        entry_descricao.delete(0, tk.END)
        entry_descricao.insert(0, texto.upper())

    entry_descricao.bind("<KeyRelease>", to_uppercase)

    # -----------------------------
    # FUNÇÃO SALVAR
    # -----------------------------
    def salvar():
        cod = entry_codigo.get().strip()
        desc = entry_descricao.get().strip()
        per = entry_per.get().strip()

        # Extrai o ID do tipo de ativo selecionado
        tipo_selecionado = combo_tipo.get()
        if tipo_selecionado == "":
            messagebox.showwarning("Atenção", "Selecione um Tipo de Ativo.", parent=janela)
            return

        tipo_id = tipo_selecionado.split(" - ")[0]  # pega o INV00_01

        ok, mensagem, campo = inv00_1.validar_campos_inv01(cod, desc, tipo_id, per)
        if not ok:
            messagebox.showwarning("Atenção", mensagem, parent=janela)
            return

        conn = inv00_0.conectar()
        if inv00_0.existe_codigo_inv01(conn, cod):
            conn.close()
            messagebox.showwarning("Atenção", f"O código {cod} já está cadastrado.", parent=janela)
            return

        inv00_0.inserir_registro_inv01(conn, cod, desc, tipo_id, per)
        conn.close()

        messagebox.showinfo("Sucesso", "Registro incluído com sucesso!", parent=janela)

        # RECARREGA O GRID
        for i in tree.get_children():
            tree.delete(i)

        conn = inv00_0.conectar()
        registros = inv00_0.listar_registros_inv01(conn)
        conn.close()

        for reg in registros:
            tree.insert("", tk.END, values=reg)

        # Limpa campos
        entry_codigo.delete(0, tk.END)
        entry_descricao.delete(0, tk.END)
        combo_tipo.set("")
        entry_per.delete(0, tk.END)

        entry_codigo.focus()

    # -----------------------------
    # BOTÕES
    # -----------------------------
    frame_botoes = ttk.Frame(janela, padding=10)
    frame_botoes.pack()

    ttk.Button(frame_botoes, text="Salvar", width=12, command=salvar).grid(row=0, column=0, padx=10)
    ttk.Button(frame_botoes, text="Retornar", width=12, command=janela.destroy).grid(row=0, column=1, padx=10)

    entry_codigo.focus()
    janela.lift()
    janela.focus_force()



#Versão Anterior sem Consulta a Tabela INV00 Tipo de Ativos

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

import inv00_0
import inv00_1
def abrir_janela_inv01(root, tree):

    # Evita abrir mais de uma janela de inclusão
    for widget in root.winfo_children():
        if isinstance(widget, tk.Toplevel) and widget.title() == "Inclusão de Segmentos":
            widget.lift()
            widget.focus_force()
            return

    janela = tk.Toplevel(root)
    janela.title("Inclusão de Segmentos")
    janela.geometry("550x350")

    janela.transient(root)
    janela.grab_set()
    janela.bind("<Escape>", lambda e: janela.destroy())

    # -----------------------------
    # CAMPOS
    # -----------------------------
    frame = ttk.Frame(janela, padding=20)
    frame.pack(fill="both", expand=True)

    ttk.Label(frame, text="Código:").grid(row=0, column=0, sticky="w", pady=5)
    entry_codigo = ttk.Entry(frame, width=5)
    entry_codigo.grid(row=0, column=1, sticky="w", pady=5)

    ttk.Label(frame, text="Descrição:").grid(row=1, column=0, sticky="w", pady=5)
    entry_descricao = ttk.Entry(frame, width=30)
    entry_descricao.grid(row=1, column=1, sticky="w", pady=5)

    ttk.Label(frame, text="Tipo Ativo:").grid(row=2, column=0, sticky="w", pady=5)
    entry_tipo = ttk.Entry(frame, width=5)
    entry_tipo.grid(row=2, column=1, sticky="w", pady=5)

    ttk.Label(frame, text="Percentual Ativo:").grid(row=3, column=0, sticky="w", pady=5)
    entry_per = ttk.Entry(frame, width=30)
    entry_per.grid(row=3, column=1, sticky="w", pady=5)


    # Converte para maiúsculas em tempo real
    def to_uppercase(event):
        texto = entry_descricao.get()
        entry_descricao.delete(0, tk.END)
        entry_descricao.insert(0, texto.upper())

    entry_descricao.bind("<KeyRelease>", to_uppercase)

    # -----------------------------
    # FUNÇÃO SALVAR
    # -----------------------------
    def salvar():
        cod = entry_codigo.get().strip()
        desc = entry_descricao.get().strip()
        atv = entry_tipo.get().strip()
        per = entry_per.get().strip()

        ok, mensagem, campo = inv00_1.validar_campos_inv01(cod, desc, atv, per)
        if not ok:
            messagebox.showwarning("Atenção", mensagem, parent=janela)
            return

        conn = inv00_0.conectar()
        if inv00_0.existe_codigo_inv01(conn, cod):
            conn.close()
            messagebox.showwarning("Atenção", f"O código {cod} já está cadastrado.", parent=janela)
            return

        inv00_0.inserir_registro_inv01(conn, cod, desc, atv, per)
        conn.close()

        messagebox.showinfo("Sucesso", "Registro incluído com sucesso!", parent=janela)

        # RECARREGA O GRID NA TELA PRINCIPAL
        for i in tree.get_children():
            tree.delete(i)

        conn = inv00_0.conectar()
        registros = inv00_0.listar_registros_inv01(conn)
        conn.close()

        for reg in registros:
            tree.insert("", tk.END, values=reg)

        # Limpa campos
        entry_codigo.delete(0, tk.END)
        entry_descricao.delete(0, tk.END)
        entry_tipo.delete(0, tk.END)
        entry_per.delete(0, tk.END) 

        entry_codigo.focus()

    # -----------------------------
    # BOTÕES
    # -----------------------------
    frame_botoes = ttk.Frame(janela, padding=10)
    frame_botoes.pack()

    ttk.Button(frame_botoes, text="Salvar", width=12, command=salvar).grid(row=0, column=0, padx=10)
    ttk.Button(frame_botoes, text="Retornar", width=12, command=janela.destroy).grid(row=0, column=1, padx=10)

    entry_codigo.focus()
    janela.lift()
    janela.focus_force()
'''
