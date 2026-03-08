'''
Programa de Investimentos
Conexão com o Banco INV.DB e Queries
JC 01/2026
Ver 1
Banco de Dados inv.db

'''
#parte a
import sqlite3
from tkinter import messagebox
import inv00_1

# ============================================================
#   CONEXÃO COM O BANCO
# ============================================================
def conectar():
    return sqlite3.connect("inv.db")


# ============================================================
#   TABELA INV00
# ============================================================
def inserir_registro(conn, cod, desc, seg, perc):
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO inv00 (inv00_01, inv00_02, inv00_03, inv00_20) VALUES (?,?,?,?)",
        (cod, desc, seg, perc)
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
    cursor.execute("SELECT SUM(inv00_20) FROM inv00")
    resultado = cursor.fetchone()[0]
    return resultado if resultado else 0


def alterar_registro(conn, cod, desc, perc, seg):
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE inv00
            SET inv00_02 = ?, inv00_20 = ?, inv00_03 = ?
            WHERE inv00_01 = ?
        """, (desc, perc, seg, cod))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Erro ao alterar registro: {e}")


# ============================================================
#   TABELA INV01
# ============================================================
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
    cursor.execute("""
        SELECT COALESCE(SUM(INV01_20), 0)
        FROM INV01
        WHERE INV01_01 = ?
    """, (tipo_id,))
    return float(cursor.fetchone()[0])
#parte b
# ============================================================
#   TABELA INV02
# ============================================================

def listar_registros_inv02(conn):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT inv02_06, inv02_02, inv02_01, inv02_05,
               inv02_07, inv02_08, inv02_09, inv02_17,
               inv02_10, inv02_22, inv02_18, inv02_20, 
               inv02_21
        FROM inv02
    """)
    dados = cursor.fetchall()

    # Converter datas para DD/MM/AAAA antes de devolver
    dados_convertidos = []
    for row in dados:
        row = list(row)
        row[10] = inv00_1.iso_compacto_para_br(row[10])  # inv02_18
        dados_convertidos.append(tuple(row))

    return dados_convertidos


def existe_codigo_inv02(conn, cod):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM inv02 WHERE inv02_06=?", (cod,))
    return cursor.fetchone()[0] > 0


def inserir_registro_inv02(conn, cod, desc, tipo, segm, atv, vlr, data, peri, obs):

    cursor = conn.cursor()

    # Converter data DD/MM/AAAA → AAAAMMDD
    data_iso = inv00_1.br_para_iso_compacto(data)

    cursor.execute("""
        INSERT INTO inv02 (
            inv02_06, inv02_02, inv02_01, inv02_05,
            inv02_07, inv02_08, inv02_09, inv02_10,
            inv02_17, inv02_18, inv02_20, inv02_21
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        cod, desc, tipo, segm,
        0.00, 0.00, 0.00, 0.00,
        atv, data_iso, peri, obs
    ))

    conn.commit()

def soma_percentuais_inv02_segmento(conn, segmento_id):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COALESCE(SUM(Inv02_20), 0)
          FROM INV02
         WHERE Inv02_05 = ?
    """, (segmento_id,))
    resultado = cursor.fetchone()[0]
    return float(resultado or 0.0)

''' Substituida pela função acima
def soma_perc_inv02(conn, tipo_id):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COALESCE(SUM(INV02_20), 0)
        FROM INV02
        WHERE INV02_05 = ?
    """, (tipo_id,))
    resultado = cursor.fetchone()
    return float(resultado[0]) if resultado else 0.0
'''

def atualizar_registro_inv02(conn, cod, desc, tipo_id, per, obs, vlr):
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE inv02
            SET inv02_05 = ?, inv02_02 = ?, inv02_20 = ?, inv02_21 = ?, inv02_22 = ?
            WHERE inv02_06 = ?
        """, (tipo_id, desc, per, obs, vlr, cod))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Erro ao alterar registro: {e}")


def excluir_registro_inv02(conn, cod):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM inv02 WHERE inv02_06=?", (cod,))
    conn.commit()


# ============================================================
#   ATUALIZAÇÃO DE POSIÇÃO (C, D, V)
# ============================================================
def atualizar_posicao_inv02(conn, codigo_ativo, tipo_mov, quantidade, total_rs, total_us, usa_dolar):
    cursor = conn.cursor()

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

    # COMPRA / DESDOBRO
    if tipo_mov in ["C", "D"]:
        nova_qtd = qtd_atual + quantidade
        novo_total_r = total_r_atual + total_rs

        if usa_dolar == "S":
            novo_total_us = total_us_atual + total_us
        else:
            novo_total_us = 0

        preco_r = novo_total_r / nova_qtd if nova_qtd > 0 else 0
        preco_us = novo_total_us / nova_qtd if (nova_qtd > 0 and usa_dolar == "S") else 0

    # VENDA
    elif tipo_mov == "V":
        custo_saida_r = preco_r_atual * quantidade
        nova_qtd = qtd_atual - quantidade
        novo_total_r = total_r_atual - custo_saida_r

        if usa_dolar == "S":
            custo_saida_us = preco_us_atual * quantidade
            novo_total_us = total_us_atual - custo_saida_us
        else:
            novo_total_us = 0

        preco_r = novo_total_r / nova_qtd if nova_qtd > 0 else 0
        preco_us = novo_total_us / nova_qtd if (nova_qtd > 0 and usa_dolar == "S") else 0

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

# ============================================================
#   REVERTER POSIÇÃO (C, V, D)
# ============================================================
def reverter_posicao_inv02(conn, codigo_ativo, tipo_mov, quantidade, total_rs, total_us):
    cur = conn.cursor()

    codigo_ativo = str(codigo_ativo).strip().upper()

    cur.execute("""
        SELECT INV02_07, INV02_09, INV02_10, INV02_17
        FROM INV02
        WHERE INV02_06 = ?
    """, (codigo_ativo,))
    row = cur.fetchone()

    if row is None:
        raise ValueError(f"Ativo '{codigo_ativo}' não encontrado na tabela INV02.")

    qtd_atual, custo_total, custo_total_usd, ativo_exterior = row

    # REVERTER COMPRA
    if tipo_mov == "C":
        nova_qtd = qtd_atual - quantidade
        novo_custo_total = custo_total - total_rs
        novo_custo_medio = novo_custo_total / nova_qtd if nova_qtd > 0 else 0
        novo_custo_total_usd = custo_total_usd - total_us if ativo_exterior == "S" else None

    # REVERTER VENDA
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

    # REVERTER DESDOBRO
    elif tipo_mov == "D":
        fator = quantidade
        nova_qtd = qtd_atual / fator
        novo_custo_medio = custo_total / nova_qtd if nova_qtd > 0 else 0
        novo_custo_total = custo_total
        novo_custo_total_usd = custo_total_usd if ativo_exterior == "S" else None

    cur.execute("""
        UPDATE INV02
        SET INV02_07 = ?,
            INV02_09 = ?,
            INV02_08 = ?,
            INV02_10 = ?
        WHERE INV02_06 = ?
    """, (nova_qtd, novo_custo_total, novo_custo_medio, novo_custo_total_usd, codigo_ativo))

    conn.commit()


# ============================================================
#   TABELA INV03
# ============================================================

def listar_registros_inv03(conn):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT inv03_00, inv03_06, inv03_02, inv03_12,
               inv03_07, inv03_13, inv03_14, inv03_15,
               inv03_22, inv03_16, inv03_18, inv03_19
        FROM inv03
    """)
    dados = cursor.fetchall()

    # Converter datas antes de devolver
    dados_convertidos = []
    for row in dados:
        row = list(row)
        row[10] = inv00_1.iso_compacto_para_br(row[10])  # inv03_18
        dados_convertidos.append(tuple(row))

    return dados_convertidos


def inserir_registro_inv03(conn, registro):
    """
    Insere um registro na tabela INV03.
    'registro' é um dicionário contendo todos os campos da tela.
    """

    # Converter data DD/MM/AAAA → AAAAMMDD
    data_iso = inv00_1.br_para_iso_compacto(registro["INV03_18"])

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
        data_iso,                 # <-- data convertida
        registro["INV03_19"]
    )

    cursor = conn.cursor()
    cursor.execute(sql, valores)
    conn.commit()


def excluir_registro_inv03(conn, id_registro):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM INV03 WHERE INV03_00 = ?", (id_registro,))
    conn.commit()

#parte d
# ============================================================
#   TABELA INV04 — DIVIDENDOS
# ============================================================

# ------------------------------------------------------------
# Buscar ativos que pagam dividendos (Inv02_22 = 'S')
# ------------------------------------------------------------
def buscar_ativos_pagadores():
    con = conectar()
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    sql = """
        SELECT 
            Inv02_05 AS CodigoSegmento,
            Inv02_06 AS CodigoAtivo,
            Inv02_07 AS Quantidade,
            Inv02_17 AS AtivoExterior
        FROM INV02
        WHERE Inv02_22 = 'S'
    """

    cur.execute(sql)
    dados = cur.fetchall()
    con.close()
    return dados


# ------------------------------------------------------------
# Verificar se dividendo já existe (chave: ativo + data pagamento)
# ------------------------------------------------------------
def buscar_dividendo_existente(codigo_ativo, data_pagamento):
    con = conectar()
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    # Converter DD/MM/AAAA → AAAAMMDD
    data_iso = inv00_1.br_para_iso_compacto(data_pagamento)

    sql = """
        SELECT 
            Inv04_00,
            Inv04_06,
            Inv04_18
        FROM INV04
        WHERE Inv04_06 = ?
          AND Inv04_18 = ?
    """

    cur.execute(sql, (codigo_ativo, data_iso))
    dado = cur.fetchone()
    con.close()
    return dado


# ------------------------------------------------------------
# Inserir dividendo na INV04
# ------------------------------------------------------------
def inserir_dividendo(reg):
    con = conectar()
    cur = con.cursor()

    # Converter data DD/MM/AAAA → AAAAMMDD
    data_iso = inv00_1.br_para_iso_compacto(reg["DataPagamento"])

    sql = """
        INSERT INTO INV04 (
            Inv04_05,  -- Código Segmento
            Inv04_06,  -- Código Ativo
            Inv04_23,  -- Valor Dividendo R$
            Inv04_07,  -- Quantidade
            Inv04_24,  -- Total Dividendo R$
            Inv04_15,  -- Cotação US$
            Inv04_25,  -- Valor Dividendo US$
            Inv04_26,  -- Total Dividendo US$
            Inv04_18   -- Data Pagamento
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    cur.execute(sql, (
        reg["CodigoSegmento"],
        reg["CodigoAtivo"],
        reg["ValorRS"],
        reg["Quantidade"],
        reg["TotalRS"],
        reg["CotacaoUS"],
        reg["ValorUS"],
        reg["TotalUS"],
        data_iso
    ))

    con.commit()
    con.close()


# ------------------------------------------------------------
# Atualizar dividendo existente
# ------------------------------------------------------------
def atualizar_dividendo(reg, id_registro):
    con = conectar()
    cur = con.cursor()

    sql = """
        UPDATE INV04 SET
            Inv04_23 = ?,   -- Valor R$
            Inv04_07 = ?,   -- Quantidade
            Inv04_24 = ?,   -- Total R$
            Inv04_15 = ?,   -- Cotação US$
            Inv04_25 = ?,   -- Valor US$
            Inv04_26 = ?    -- Total US$
        WHERE Inv04_00 = ?
    """

    cur.execute(sql, (
        reg["ValorRS"],
        reg["Quantidade"],
        reg["TotalRS"],
        reg["CotacaoUS"],
        reg["ValorUS"],
        reg["TotalUS"],
        id_registro
    ))

    con.commit()
    con.close()
