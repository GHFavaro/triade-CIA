from tkinter import *
import customtkinter
import pandas as pd
from sqlalchemy import create_engine
import datetime
import glob
from customtkinter import filedialog

# Set the theme and color options
customtkinter.set_appearance_mode("dark")  # Modes: system (default), light, dark
customtkinter.set_default_color_theme("green")  # Themes: blue (default), dark-blue, green

class FirstScreen(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title('Sistema de backup')
        self.geometry('550x500')

        self.add_folder_button = Button(text="Adicionar Pasta", command=self.add_folder)
        self.add_folder_button.pack(pady=5)

        self.campo_texto_host = customtkinter.CTkLabel(self, text='HOST:')
        self.campo_texto_host.pack()

        self.campo_host = customtkinter.CTkEntry(self, height=10)
        self.campo_host.pack()

        self.campo_texto_porta = customtkinter.CTkLabel(self, text='PORTA:')
        self.campo_texto_porta.pack()

        self.campo_porta = customtkinter.CTkEntry(self, height=10)
        self.campo_porta.pack()

        self.campo_texto_usuario = customtkinter.CTkLabel(self, text='USUÁRIO:')
        self.campo_texto_usuario.pack()

        self.campo_usuario = customtkinter.CTkEntry(self, height=10)
        self.campo_usuario.pack()

        self.campo_texto_senha = customtkinter.CTkLabel(self, text='SENHA:')
        self.campo_texto_senha.pack()

        self.campo_senha = customtkinter.CTkEntry(self, height=10)
        self.campo_senha.pack()

        self.campo_texto_database = customtkinter.CTkLabel(self, text='DATABASE:')
        self.campo_texto_database.pack()

        self.campo_database = customtkinter.CTkEntry(self, height=10)
        self.campo_database.pack()

        self.button = customtkinter.CTkButton(self, text="Criar backup", command=self.Criar)
        self.button.pack(pady=10)

        self.button = customtkinter.CTkButton(self, text="Restaurar backup", command=self.Restaurar)
        self.button.pack(pady=10)

        # Create label for displaying result
        self.label = customtkinter.CTkLabel(self, text='')
        self.label.pack(pady=10)

    def add_folder(self):
        self.folder = filedialog.askdirectory()

    def Criar(self):
        database = self.campo_database.get()

        engine = self.conecta()

        df = pd.read_sql('SELECT table_schema, table_name, table_type FROM information_schema.tables', con=engine)

        tabelas = df.loc[df['TABLE_SCHEMA'] == database]
        for index, row in tabelas.iterrows():
            tabela = pd.read_sql(f'SELECT * FROM {row['TABLE_NAME']}', con=engine)
            tabela.to_parquet(f'{self.folder}\\{row['TABLE_NAME']}-{datetime.date.today()}.parquet', engine='pyarrow')

        # Update label text
        self.label.configure(text=f'O backup foi criado com sucesso!')

    def Restaurar(self):
        engine = self.conecta()

        backups = self.Backup_exato()

        for backup in backups:
            parquet = pd.read_parquet(f"{self.folder}\\{backup}", engine='pyarrow')
            parquet.to_sql(backup.split('-')[0], con=engine, if_exists='replace', index=False)

        self.label.configure(text=f'O banco foi restaurado com sucesso!')

    def Backups(self):
        parquets = glob.glob(f'{self.folder}\\*.parquet')
        print(parquets)
        return sorted(parquets)
    
    def Backup_exato(self):
            retorno = []

            backups = self.Backups()  # Supondo que a função Backups() retorna a lista de arquivos de backup
            for nome_arquivo in backups:
                # Extrai a data do nome do arquivo
                partes = nome_arquivo.split("\\")
                try:
                    retorno.append(partes[2])
                except ValueError:
                    pass
            return sorted(retorno)

    def conecta(self):
        usuario = self.campo_usuario.get()
        senha = self.campo_senha.get()
        host = self.campo_host.get()
        porta = self.campo_porta.get()
        database = self.campo_database.get()

        connection_string = f"mysql+mysqlconnector://{usuario}:{senha}@{host}:{porta}/{database}"
        engine = create_engine(connection_string, echo=True)
        return engine

# Define app and Create our app's mainloop
if __name__ == '__main__':
    app = FirstScreen()
    app.mainloop()
