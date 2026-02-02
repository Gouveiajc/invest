'''
Programa de Conexão com Banco de Dados
JC 01/2026
Ver 1
Banco de Dados inv.db

'''
import sqlite3

def conectar():
    return sqlite3.connect("inv.db")

#Tabela INV00
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

#Tabela INV01
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

#Tabela INV02
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
    