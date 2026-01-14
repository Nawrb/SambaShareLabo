# 📂 SambaShareLabo - Notice d'Installation
Documentation technique pour le déploiement des scripts de communication inter-systèmes (Linux & Windows).

---

## 1. Installation Côté Serveur (Linux / Docker)
Cette machine héberge le script serveur.py, surveille les fichiers Samba et héberge le Chat.

## A. Pré-requis système
Installez Python, le gestionnaire de paquets pip et les utilitaires Samba :

~~~
apt-get update
apt-get install -y python3 python3-pip samba
~~~

# B. Dépendances Python
Installez les librairies nécessaires pour le serveur Web et le WebSocket :

~~~
pip3 install flask flask-socketio
~~~

### Linux script client.py installer les paquets suivants:

~~~
sudo apt-get update
sudo apt-get install -y python3 python3-tk
~~~ 
⚠️ Autoriser le port 8080 et 5000 sur linux avec la commande suivante:

~~~
apt update && apt install ufw
sudo ufw allow 8080/tcp
sudo ufw allow 5000/tcp
~~~

### Windows script client.py installer les paquets suivants:

~~~
Télécharge Python sur python.org
TRÈS IMPORTANT : Lors de l'installation, coche la case "Add Python to PATH" en bas de la première fenêtre
~~~

---
