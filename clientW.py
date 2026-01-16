import socket
import threading
import tkinter as tk
from tkinter import messagebox
import webbrowser

# Harmonisé avec le serveur
HOST = '0.0.0.0'
PORT = 8080 

def show_popup(msg):
    """Affiche une popup classique"""
    try:
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        messagebox.showwarning("Alerte Samba", msg)
        root.destroy()
    except:
        pass

def handle_command(data_str):
    """Décide quoi faire selon le message reçu"""
    if data_str.startswith("URL|"):
        # Format: URL|http://192.168.1.50:5000/chat/contrat.docx
        url = data_str.split("|", 1)[1]
        print(f"Ouverture navigateur : {url}")
        webbrowser.open(url)
    else:
        # Message texte simple
        show_popup(data_str)

def listener():
    print(f"Client Samba Alert en écoute sur le port {PORT}...")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((HOST, PORT))
            s.listen()
            while True:
                conn, addr = s.accept()
                with conn:
                    data = conn.recv(2048) # Buffer un peu plus grand pour les URL
                    if data:
                        msg = data.decode('utf-8')
                        # On traite ça dans un thread pour ne pas bloquer le socket
                        threading.Thread(target=handle_command, args=(msg,)).start()
        except OSError as e:
            print(f"Erreur Port {PORT} occupé ? {e}")
            input("Appuyez sur Entrée pour quitter...")

if __name__ == "__main__":
    listener()