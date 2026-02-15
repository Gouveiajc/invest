'''
Programa de Conexão com Banco de Dados
JC 01/2026
Ver 1
Banco de Dados inv.db

'''
import sqlite3
from tkinter import messagebox

def conectar():
    return sqlite3.connect("inv.db")

#--------------------------------------------------------------------------------------
#Tabela INV00
#--------------------------------------------------------------------------------------
def inserir_registro(conn, cod, desc, perc, seg):
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO inv00 (inv00_01, inv00_02, inv00_03, inv00_20) VALUES (?,?,?,?)",
        (cod, desc, perc, seg)
    )
    conn.commit()

def excluir_registro(conn, cod):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM inv00 WHERE inv00_01=?", (cod,))
    conn.commit()

def listar_registros(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT inv00_01, inv00_02, inv00_03, inv00_20 FROM inv00")
    return cursor.fetchall()

def existe_codigo(conn, cod):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM inv00 WHERE inv00_01=?", (cod,))
    return cursor.fetchone()[0] > 0

def soma_perc(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(inv00_03) FROM inv00")
    resultado = cursor.fetchone()[0]
    return resultado if resultado else 0

def alterar_registro(conn, cod, desc, perc, seg):
    """
    Atualiza um registro na tabela INV00.
    """
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE inv00
            SET inv00_02 = ?, inv00_03 = ?, inv00_20 = ?
            WHERE inv00_01 = ?
        """, (desc, perc, seg, cod))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Erro ao alterar registro: {e}")
#----------------------------------------------------------------------------------
#Tabela INV01
#----------------------------------------------------------------------------------
def listar_registros_inv01(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT inv01_05, inv01_02, inv01_01, inv01_20 FROM inv01")
    return cursor.fetchall()

def existe_codigo_inv01(conn, cod):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM inv01 WHERE inv01_05=?", (cod,))
    return cursor.fetchone()[0] > 0

def inserir_registro_inv01(conn, cod, desc, atv, per):
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO inv01 (inv01_05, inv01_02, inv01_01, inv01_20) VALUES (?,?,?,?)",
        (cod, desc, atv, per)
    )
    conn.commit()

def atualizar_registro_inv01(conn, cod, desc, atv, per):
     
    #Atualiza um registro na tabela INV01.
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE inv01
            SET inv01_02 = ?, inv01_01 = ?, inv01_20 = ?
            WHERE inv01_05 = ?
        """, (desc, atv, per, cod))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Erro ao alterar registro: {e}")

def excluir_registro_inv01(conn, cod):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM inv01 WHERE inv01_05=?", (cod,))
    conn.commit()

def soma_perc_inv01(conn, tipo_id): 
    cursor = conn.cursor() 
    cursor.execute(""" SELECT COALESCE(SUM(INV01_20), 0) FROM INV01 WHERE INV01_01 = ? """, (tipo_id,)) 
    return float(cursor.fetchone()[0]) 

#---------------------------------------------------------------------
#Tabela INV02
#---------------------------------------------------------------------
def listar_registros_inv02(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT inv02_06, inv02_02, inv02_01, inv02_05, inv02_07, inv02_08, inv02_09, inv02_17, inv02_10, inv02_18, inv02_20, inv02_21 FROM inv02")
    return cursor.fetchall()

def existe_codigo_inv02(conn, cod):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM inv02 WHERE inv02_06=?", (cod,))
    return cursor.fetchone()[0] > 0

def inserir_registro_inv02(conn, cod, desc, tipo, segm, atv, data, peri, obs):
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO inv02 (inv02_06, inv02_02, inv02_01, inv02_05, inv02_07, inv02_08, inv02_09, inv02_10, inv02_17, inv02_18, inv02_20, inv02_21) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
        (cod, desc, tipo, segm, 0.00, 0.00, 0.00, 0.00, atv, data, peri, obs)
    )
    conn.commit()

def soma_perc_inv02(conn, tipo_id):
    cursor = conn.cursor()
    cursor.execute(""" SELECT COALESCE(SUM(INV02_20), 0) FROM INV02 WHERE INV02_05 = ? """, (tipo_id,))
    resultado = cursor.fetchone()
    return float(resultado[0]) if resultado else 0.0

def atualizar_registro_inv02(conn, cod, desc, tipo_id, per,obs):
     
    #Atualiza um registro na tabela INV01.
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE inv02 SET inv02_05 = ?, inv02_02 = ?, inv02_20 = ?, inv02_21 = ? WHERE inv02_06 = ?
        """, (tipo_id, desc, per, obs, cod))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Erro ao alterar registro: {e}")

def excluir_registro_inv02(conn, cod):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM inv02 WHERE inv02_06=?", (cod,))
    conn.commit()

def atualizar_posicao_inv02(conn, codigo_ativo, tipo_mov, quantidade, total_rs, total_us, usa_dolar):
    """
    Atualiza posição do ativo para C, D ou V
    Inclui controle em R$ e US$ quando ativo do exterior.
    """

    cursor = conn.cursor()

    # Captura posição atual
    cursor.execute("""
        SELECT INV02_07, INV02_09, INV02_08,
               INV02_10, INV02_20
        FROM INV02
        WHERE INV02_06 = ?
    """, (codigo_ativo,))
    atual = cursor.fetchone()

    if not atual:
        return

    qtd_atual, total_r_atual, preco_r_atual, total_us_atual, preco_us_atual = atual

    if qtd_atual is None: qtd_atual = 0
    if total_r_atual is None: total_r_atual = 0
    if preco_r_atual is None: preco_r_atual = 0
    if total_us_atual is None: total_us_atual = 0
    if preco_us_atual is None: preco_us_atual = 0

    # ================================
    #      COMPRA / DESDOBRO
    # ================================
    if tipo_mov in ["C", "D"]:

        nova_qtd = qtd_atual + quantidade
        novo_total_r = total_r_atual + total_rs

        if usa_dolar == "S":
            novo_total_us = total_us_atual + total_us
        else:
            novo_total_us = 0

        # preço médio R$
        preco_r = novo_total_r / nova_qtd if nova_qtd > 0 else 0

        # preço médio US$
        if usa_dolar == "S":
            preco_us = novo_total_us / nova_qtd if nova_qtd > 0 else 0
        else:
            preco_us = 0

    # ================================
    #               VENDA
    # ================================
    elif tipo_mov == "V":

        # Custo proporcional R$
        custo_saida_r = preco_r_atual * quantidade
        nova_qtd = qtd_atual - quantidade
        novo_total_r = total_r_atual - custo_saida_r

        # Custo proporcional US$ (se ativo internacional)
        if usa_dolar == "S":
            custo_saida_us = preco_us_atual * quantidade
            novo_total_us = total_us_atual - custo_saida_us
        else:
            novo_total_us = 0

        # Recalcular preços médios
        preco_r = novo_total_r / nova_qtd if nova_qtd > 0 else 0
        preco_us = novo_total_us / nova_qtd if (nova_qtd > 0 and usa_dolar == "S") else 0

    # Grava no banco
    cursor.execute("""
        UPDATE INV02 SET
            INV02_07 = ?,
            INV02_09 = ?,
            INV02_08 = ?,
            INV02_10 = ?,
            INV02_20 = ?
        WHERE INV02_06 = ?
    """, (nova_qtd, novo_total_r, preco_r, novo_total_us, preco_us, codigo_ativo))

    conn.commit()

def reverter_posicao_inv02(conn, codigo_ativo, tipo_mov, quantidade, total_rs, total_us):
    cur = conn.cursor()

    # Normalizar código
    codigo_ativo = str(codigo_ativo).strip().upper()

    # Buscar posição atual
    cur.execute("""
        SELECT INV02_07, INV02_09, INV02_10, INV02_17
        FROM INV02
        WHERE INV02_06 = ?
    """, (codigo_ativo,))
    row = cur.fetchone()

    if row is None:
        raise ValueError(f"Ativo '{codigo_ativo}' não encontrado na tabela INV02.")

    qtd_atual, custo_total, custo_total_usd, ativo_exterior = row

    # -------------------------
    # 1) REVERTER COMPRA
    if tipo_mov == "C":
        nova_qtd = qtd_atual - quantidade
        novo_custo_total = custo_total - total_rs
        novo_custo_medio = novo_custo_total / nova_qtd if nova_qtd > 0 else 0
        novo_custo_total_usd = custo_total_usd - total_us if ativo_exterior == "S" else None

    # -------------------------
    # 2) REVERTER VENDA
    elif tipo_mov == "V":
        nova_qtd = qtd_atual + quantidade
        custo_medio = custo_total / qtd_atual if qtd_atual > 0 else 0
        novo_custo_total = custo_total + (custo_medio * quantidade)
        novo_custo_medio = novo_custo_total / nova_qtd if nova_qtd > 0 else 0

        if ativo_exterior == "S":
            custo_medio_usd = custo_total_usd / qtd_atual if qtd_atual > 0 else 0
            novo_custo_total_usd = custo_total_usd + (custo_medio_usd * quantidade)
        else:
            novo_custo_total_usd = None

    # -------------------------
    # 3) REVERTER DESDOBRAMENTO
    elif tipo_mov == "D":
        fator = quantidade
        nova_qtd = qtd_atual / fator
        novo_custo_medio = custo_total / nova_qtd if nova_qtd > 0 else 0
        novo_custo_total = custo_total
        novo_custo_total_usd = custo_total_usd if ativo_exterior == "S" else None

    # -------------------------
    # Atualizar INV02
    cur.execute("""
        UPDATE INV02
        SET INV02_07 = ?,
            INV02_09 = ?,
            INV02_08 = ?,
            INV02_10 = ?
        WHERE INV02_06 = ?
    """, (nova_qtd, novo_custo_total, novo_custo_medio, novo_custo_total_usd, codigo_ativo))

    conn.commit()
#-----------------------
# Conciliação de Ativos
def conciliar_ativo_inv02(codigo_ativo):

    conn = conectar()
    cur = conn.cursor()

    # Quantidade calculada
    cur.execute("""
        SELECT 
            SUM(
                CASE 
                    WHEN Inv03_12 IN ('C','D') THEN Inv03_07
                    WHEN Inv03_12 = 'V' THEN -Inv03_07
                END
            )
        FROM INV03
        WHERE Inv03_06 = ?
    """, (codigo_ativo,))
    qtd_calc = cur.fetchone()[0] or 0

    # Custo total calculado em R$
    cur.execute("""
        SELECT 
            SUM(
                CASE 
                    WHEN Inv03_12 IN ('C','D') THEN Inv03_14
                    WHEN Inv03_12 = 'V' THEN -Inv03_07 * (
                        SELECT Inv02_08 FROM INV02 WHERE Inv02_06 = INV03.Inv03_06
                    )
                END
            )
        FROM INV03
        WHERE Inv03_06 = ?
    """, (codigo_ativo,))
    custo_calc = cur.fetchone()[0] or 0

    # Buscar dados do ativo
    cur.execute("""
        SELECT Inv02_07, Inv02_09, Inv02_08, Inv02_17, Inv02_10
        FROM INV02
        WHERE Inv02_06 = ?
    """, (codigo_ativo,))
    qtd_atual, custo_atual, custo_medio_atual, ativo_exterior, custo_usd_atual = cur.fetchone()

    # Cálculo do custo médio R$
    custo_medio_calc = custo_calc / qtd_calc if qtd_calc > 0 else 0

    # Se ativo exterior, calcular custo total em US$
    if ativo_exterior == 'S':
        cur.execute("""
            SELECT 
                SUM(
                    CASE 
                        WHEN Inv03_12 IN ('C','D') THEN Inv03_16
                        WHEN Inv03_12 = 'V' THEN -Inv03_07 * (
                            SELECT Inv02_10 / Inv02_07
                            FROM INV02
                            WHERE Inv02_06 = INV03.Inv03_06
                        )
                    END
                )
            FROM INV03
            WHERE Inv03_06 = ?
        """, (codigo_ativo,))
        custo_usd_calc = cur.fetchone()[0] or 0
    else:
        custo_usd_calc = custo_usd_atual  # não altera

    # Verificar divergências
    divergencia = (
        qtd_calc != qtd_atual or
        custo_calc != custo_atual or
        round(custo_medio_calc, 6) != round(custo_medio_atual, 6) or
        (ativo_exterior == 'S' and custo_usd_calc != custo_usd_atual)
    )

    if divergencia:
        msg = (
            f"Divergência encontrada no ativo {codigo_ativo}\n\n"
            f"Quantidade atual: {qtd_atual} / Calculada: {qtd_calc}\n"
            f"Custo atual R$: {custo_atual:.2f} / Calculado: {custo_calc:.2f}\n"
            f"Custo médio atual R$: {custo_medio_atual:.6f} / Calculado: {custo_medio_calc:.6f}\n"
        )

        if ativo_exterior == 'S':
            msg += (
                f"Custo atual US$: {custo_usd_atual:.2f} / Calculado: {custo_usd_calc:.2f}\n"
            )

        msg += "\nDeseja atualizar?"

        if messagebox.askyesno("Conciliação", msg):
            if ativo_exterior == 'S':
                cur.execute("""
                    UPDATE INV02
                    SET Inv02_07 = ?, Inv02_09 = ?, Inv02_08 = ?, Inv02_10 = ?
                    WHERE Inv02_06 = ?
                """, (qtd_calc, custo_calc, custo_medio_calc, custo_usd_calc, codigo_ativo))
            else:
                cur.execute("""
                    UPDATE INV02
                    SET Inv02_07 = ?, Inv02_09 = ?, Inv02_08 = ?
                    WHERE Inv02_06 = ?
                """, (qtd_calc, custo_calc, custo_medio_calc, codigo_ativo))

            conn.commit()
         
    conn.close()


#--------------------------------------------------------
#Tabela INV03
#--------------------------------------------------------
def listar_registros_inv03(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT inv03_00, inv03_06, inv03_02, inv03_12, inv03_07, inv03_13, inv03_14, inv03_15, inv03_22, inv03_16, inv03_18, inv03_19 FROM inv03")
    return cursor.fetchall()

def inserir_registro_inv03(conn, registro):
    """
    Insere um registro na tabela INV03.
    'registro' é um dicionário contendo todos os campos da tela.
    """

    sql = """
        INSERT INTO INV03 (
            INV03_06,  -- Código do ativo
            INV03_02,  -- Descrição
            INV03_12,  -- Tipo de movimento
            INV03_07,  -- Quantidade
            INV03_13,  -- Valor Unitário
            INV03_14,  -- Valor Total R$
            INV03_15,  -- Cotação US$
            INV03_22,  -- Valor Unitário US$
            INV03_16,  -- Valor Total US$
            INV03_18,  -- Data Inclusão
            INV03_19   -- Nota Corretagem
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    valores = (
        registro["INV03_06"],
        registro["INV03_02"],
        registro["INV03_12"],
        registro["INV03_07"],
        registro["INV03_13"],
        registro["INV03_14"],
        registro["INV03_15"],
        registro["INV03_22"],
        registro["INV03_16"],
        registro["INV03_18"],
        registro["INV03_19"]
    )

    cursor = conn.cursor()
    cursor.execute(sql, valores)
    conn.commit()

def excluir_registro_inv03(conn, id_registro):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM INV03 WHERE INV03_00 = ?", (id_registro,))
    conn.commit()

