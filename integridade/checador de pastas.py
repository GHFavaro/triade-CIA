import os
import hashlib
import time
import logging
from datetime import datetime
from tkinter import *
from tkinter import filedialog, messagebox
from threading import Thread

logger = logging.getLogger(__name__)
logging.basicConfig(filename='checagem.log', encoding='utf-8', level=logging.DEBUG)

def hash_file(filepath):
    """Calcula o hash SHA-256 de um arquivo."""
    sha256 = hashlib.sha256()
    try:
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
    except FileNotFoundError:
        print(f"Arquivo {filepath} não encontrado. Ignorando...")
        return None
    return sha256.hexdigest()

def hash_folder(folder_path):
    """Calcula um hash único para uma pasta e seus arquivos."""
    json_name_hashes = {}
    
    for root, _, files in sorted(os.walk(folder_path)):
        for file in sorted(files):
            file_path = os.path.join(root, file)
            file_hash = hash_file(file_path)
            
            if file_hash is not None:
                relative_path = os.path.relpath(file_path, folder_path)  # Caminho relativo ao diretório raiz
                json_name_hashes[relative_path] = file_hash
    
    return json_name_hashes

class FolderMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Monitor de Arquivos")
        self.root.geometry("800x600")  # Define um tamanho maior para a janela principal
        self.folder_paths = []
        self.monitoring = False

        # Criação dos elementos da GUI
        self.create_widgets()
    
    def create_widgets(self):
        self.add_folder_button = Button(self.root, text="Adicionar Pasta", command=self.add_folder)
        self.add_folder_button.pack(pady=5)

        self.start_button = Button(self.root, text="Iniciar Monitoramento", command=self.start_monitoring)
        self.start_button.pack(pady=5)

        self.stop_button = Button(self.root, text="Parar Monitoramento", command=self.stop_monitoring, state=DISABLED)
        self.stop_button.pack(pady=5)

        self.output_text = Text(self.root, height=30, width=100)  # Define uma área de texto maior
        self.output_text.pack(pady=10)
        self.output_text.insert(END, "Log do monitoramento será exibido aqui...\n")

    def add_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_paths.append(folder)
            self.output_text.insert(END, f"Pasta adicionada para monitoramento: {folder}\n")
    
    def start_monitoring(self):
        if not self.folder_paths:
            messagebox.showwarning("Aviso", "Adicione pelo menos uma pasta para monitoramento.")
            return
        self.monitoring = True
        self.start_button.config(state=DISABLED)
        self.stop_button.config(state=NORMAL)
        self.output_text.insert(END, "Monitoramento iniciado...\n")
        self.monitor_thread = Thread(target=self.monitor_folders)
        self.monitor_thread.start()

    def stop_monitoring(self):
        self.monitoring = False
        self.start_button.config(state=NORMAL)
        self.stop_button.config(state=DISABLED)
        self.output_text.insert(END, "Monitoramento parado.\n")

    def monitor_folders(self):
        folder_hashes = {folder: hash_folder(folder) for folder in self.folder_paths}
        
        while self.monitoring:
            for folder in self.folder_paths:
                current_hashes = hash_folder(folder)
                previous_hashes = folder_hashes[folder]
                
                for file in current_hashes.keys():
                    if file not in previous_hashes:
                        self.log_change(folder, f"Arquivo adicionado: {file}")
                
                for file in previous_hashes.keys():
                    if file not in current_hashes:
                        self.log_change(folder, f"Arquivo removido: {file}")

                for file, hash_value in current_hashes.items():
                    if file in previous_hashes and previous_hashes[file] != hash_value:
                        self.log_change(folder, f"Arquivo alterado: {file}")
                
                folder_hashes[folder] = current_hashes
            
            time.sleep(1)

    def log_change(self, folder, message):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] [{folder}] {message}"
        logger.info(log_message)
        self.output_text.insert(END, log_message + "\n")
        self.output_text.see(END)

if __name__ == "__main__":
    root = Tk()
    app = FolderMonitorApp(root)
    root.mainloop()
