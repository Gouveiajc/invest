'''
Programa de Cadastro de Ativos
JC 02/2026
Ver 1
Banco de Dados inv.db
Tabela inv02
'''

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

import inv00_0
import inv00_1

def abrir_janela_inv02(root, tree):
    # Evita abrir mais de uma janela de inclusão
    for widget in root.winfo_children():
        if isinstance(widget, tk.Toplevel) and widget.title() == "Inclusão de Ativos":
            widget.lift()
            widget.focus_force()
            return

    janela = tk.Toplevel(root)
    janela.title("Inclusão de Ativos")
    janela.geometry("550x490")

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

# --- COMBOBOX Tipo Ativo ---
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

    # --- COMBOBOX Segmento ---
    ttk.Label(frame, text="Segmento:").grid(row=3, column=0, sticky="w", pady=5)

    # Busca Segmento com tratamento de erro
    try:
        conn = inv00_0.conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT INV01_05, INV01_02 FROM INV01 ORDER BY INV01_02")
        segm = cursor.fetchall()
        lista_segm = [f"{s[0]} - {s[1]}" for s in segm]
    except Exception as f:
        messagebox.showerror("Erro", f"Erro ao carregar Segmentos: {f}")
        lista_segm = []
    finally:
        if conn:
            conn.close()

    combo_segm = ttk.Combobox(frame, values=lista_segm, state="readonly", width=30)
    combo_segm.grid(row=3, column=1, sticky="w", pady=5)

    ttk.Label(frame, text="Quantid.Ativo:").grid(row=4, column=0, sticky="w", pady=5)
    entry_qtd = ttk.Entry(frame, width=30,state="disabled" )
    entry_qtd.grid(row=4, column=1, sticky="w", pady=5)
    
    ttk.Label(frame, text="Custo Médio Ativo:").grid(row=5, column=0, sticky="w", pady=5)
    entry_cusm = ttk.Entry(frame, width=30,state="disabled")
    entry_cusm.grid(row=5, column=1, sticky="w", pady=5)
    
    ttk.Label(frame, text="Custo Aquisição:").grid(row=6, column=0, sticky="w", pady=5)
    entry_cusa = ttk.Entry(frame, width=30,state="disabled")
    entry_cusa.grid(row=6, column=1, sticky="w", pady=5)
        
    ttk.Label(frame, text="Ativo Exterior:").grid(row=7, column=0, sticky="w", pady=5) 
    lista_atv = ["S - Sim", "N - Não"] 
    combo_atv = ttk.Combobox(frame, values=lista_atv, state="readonly", width=30) 
    combo_atv.grid(row=7, column=1, sticky="w", pady=5) 
    combo_atv.set("N - Não") # Valor Inicial Padrão

    # Custo Aquisição US$ como Entry inicialmente desabilitado se Ativo Exterior for N
    ttk.Label(frame, text="Custo Aquisição US$:").grid(row=8, column=0, sticky="w", pady=5)
    entry_cusus = ttk.Entry(frame, width=30,state="disabled")
    entry_cusus.grid(row=8, column=1, sticky="w", pady=5)
   
    ttk.Label(frame, text="Data da Inclusão:").grid(row=9, column=0, sticky="w", pady=5)
    entry_data = ttk.Entry(frame, width=30)
    entry_data.grid(row=9, column=1, sticky="w", pady=5)
    
    ttk.Label(frame, text="Percentual Investir:").grid(row=10, column=0, sticky="w", pady=5)
    entry_peri = ttk.Entry(frame, width=10)
    entry_peri.grid(row=10, column=1, sticky="w", pady=5)

    ttk.Label(frame, text="Observação:").grid(row=11, column=0, sticky="w", pady=5)
    entry_obs = ttk.Entry(frame, width=30)
    entry_obs.grid(row=11, column=1, sticky="w", pady=5)

    #Função Generica Converte Letras Minusculas em Maiusculas
    def to_uppercase_generic(event):
        widget = event.widget
        # se estiver desabilitado, não faz nada
        if widget.cget("state") == "disabled":
            return
        pos = widget.index(tk.INSERT)
        texto = widget.get().upper()
        widget.delete(0, tk.END)
        widget.insert(0, texto)
        widget.icursor(pos)

    # vincular aos entries
    entry_descricao.bind("<KeyRelease>", to_uppercase_generic)
    entry_codigo.bind("<KeyRelease>", to_uppercase_generic)

    # --- FUNÇÃO SALVAR ---
    def salvar():
        cod = entry_codigo.get().strip()
        desc = entry_descricao.get().strip()
        tipo = combo_tipo.get().strip()
        segm = combo_segm.get().strip()
        atv = combo_atv.get().strip() 
        if not atv: 
            messagebox.showwarning("Atenção", "Selecione se é Ativo no Exterior.", parent=janela) 
            return 
        # extrai o código S ou N (ou use o texto inteiro conforme sua tabela) 
        atv_flag = atv.split(" - ")[0] # 'S' ou 'N'
        data  = entry_data.get().strip()
        peri = entry_peri.get().strip()
        obs = entry_obs.get().strip()

        #Verifica Combo Tipo de Ativo
        tipo_selecionado = combo_tipo.get()
        if not tipo_selecionado:
            messagebox.showwarning("Atenção", "Selecione um Tipo de Ativo.", parent=janela)
            return

        tipo = tipo_selecionado.split(" - ")[0]

        #Verifica Combo Segmento
        segm_selecionado = combo_segm.get()
        if not segm_selecionado:
            messagebox.showwarning("Atenção", "Selecione um Segmento.", parent=janela)
            return

        segm = segm_selecionado.split(" - ")[0]

        ok, mensagem, campo = inv00_1.validar_campos_inv02(cod, desc, tipo, segm, atv, data, peri)

        if not ok:
            messagebox.showwarning("Atenção", mensagem, parent=janela)
            return

        try:
            peri = float(peri.replace(',', '.')) # Aceita vírgula ou ponto
            
            conn = inv00_0.conectar()
            
            # 1. Verifica duplicidade de código
            if inv00_0.existe_codigo_inv02(conn, cod):
                messagebox.showwarning("Atenção", f"O código {cod} já existe.", parent=janela)
                return

            # 3. Grava registro
            inv00_0.inserir_registro_inv02(conn, cod, desc, tipo, segm, atv, data, peri, obs)
            
            # 4. Atualiza o Treeview (Inserindo apenas o novo para performance)
            # Se preferir recarregar tudo, mantenha seu loop de delete/insert aqui
            #tree.insert("", tk.END, values=(cod, desc, tipo, segm, atv, data, peri, obs))
            tree.insert("", tk.END, values=(cod, desc, tipo, segm, 0.00, 0.00, 0.00, 0.00, atv, data, peri, obs))
            messagebox.showinfo("Sucesso", "Registro incluído com sucesso!", parent=janela)

            # Limpa campos e foca no código
            entry_codigo.delete(0, tk.END)
            entry_descricao.delete(0, tk.END)
            combo_tipo.set("")
            combo_segm.set("")
            combo_atv.set("N")
            entry_data.delete(0, tk.END)
            entry_peri.delete(0, tk.END)
            entry_obs.delete(0, tk.END)
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
