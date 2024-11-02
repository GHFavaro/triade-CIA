import sqlite3
import os
from cryptography.fernet import Fernet
import tkinter as tk
from tkinter import filedialog, messagebox

DBFILE = 'C:\\key\\key.db'
FILE = ''  # Variável global para armazenar o arquivo selecionado

def cria_db():
    list_dir = os.listdir('C:\\')
    if "key" not in list_dir:
        os.mkdir('C:\\key\\')
        with open(DBFILE, 'w') as file_db_creator:
            file_db_creator.close()
    return True

def cria_tabela():
    bool_key_exists = cria_db()
    if bool_key_exists:
        con = sqlite3.connect(DBFILE)
        cur = con.cursor()
        try:
            cur.execute('CREATE TABLE IF NOT EXISTS key (key_column TEXT)')
            con.commit()
        finally:
            con.close()

def checar_chave():
    con = sqlite3.connect(DBFILE)
    cur = con.cursor()
    key = cur.execute('SELECT * FROM key').fetchone()
    if key is None:
        chave = cria_chave()
        cur.execute('INSERT INTO key (key_column) VALUES (?)', (chave,))
        con.commit()
    con.close()

def cria_chave():
    chave = Fernet.generate_key().decode()
    return chave

def criptografa_arq():
    global FILE
    con = sqlite3.connect(DBFILE)
    cur = con.cursor()
    key = cur.execute('SELECT * FROM key').fetchone()
    if key:
        with open(FILE, "rb") as arq_cripto:
            conteudo = arq_cripto.read()
            if conteudo[0:5] == b"cript":
                messagebox.showinfo("Info", "O arquivo já está criptografado.")
                return
            arq_cripto.close()
        conteudo_criptografado = Fernet(key[0]).encrypt(conteudo)
        with open(FILE, "wb") as arq_cripto:
            arq_cripto.write(b"cript" + conteudo_criptografado)
            arq_cripto.close()
        messagebox.showinfo("Sucesso", "Arquivo criptografado com sucesso.")

def descriptografa_arq():
    global FILE
    con = sqlite3.connect(DBFILE)
    cur = con.cursor()
    key = cur.execute('SELECT * FROM key').fetchone()
    if key:
        with open(FILE, "rb") as arq_cripto:
            conteudo = arq_cripto.read()
            if conteudo[0:5] == b"cript":
                conteudo = conteudo[5:]
            else:
                messagebox.showinfo("Info", "O arquivo não está criptografado.")
                return
            arq_cripto.close()
        conteudo_descriptografado = Fernet(key[0]).decrypt(conteudo)
        with open(FILE, "wb") as arq_cripto:
            arq_cripto.write(conteudo_descriptografado)
            arq_cripto.close()
        messagebox.showinfo("Sucesso", "Arquivo descriptografado com sucesso.")

def selecionar_arquivo():
    global FILE
    FILE = filedialog.askopenfilename(title="Selecione o arquivo")
    if FILE:
        lbl_arquivo.config(text=f"Arquivo selecionado: {os.path.basename(FILE)}")

# Configuração da interface gráfica
root = tk.Tk()
root.title("Criptografia de Arquivos")

frm = tk.Frame(root, padx=10, pady=10)
frm.pack(padx=10, pady=10)

btn_selecionar = tk.Button(frm, text="Selecionar Arquivo", command=selecionar_arquivo)
btn_selecionar.grid(row=0, column=0, pady=5)

lbl_arquivo = tk.Label(frm, text="Nenhum arquivo selecionado")
lbl_arquivo.grid(row=0, column=1, pady=5)

btn_criptografar = tk.Button(frm, text="Criptografar", command=criptografa_arq)
btn_criptografar.grid(row=1, column=0, columnspan=2, pady=5)

btn_descriptografar = tk.Button(frm, text="Descriptografar", command=descriptografa_arq)
btn_descriptografar.grid(row=2, column=0, columnspan=2, pady=5)

# Inicializa o banco de dados e a chave
cria_tabela()
checar_chave()

root.mainloop()
