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

## B. Dépendances Python
Installez les librairies nécessaires pour le serveur Web et le WebSocket :

~~~
pip3 install flask flask-socketio
~~~

### C. Configuration du Pare-feu (Serveur)
Le serveur doit être accessible sur le port 5000 (Interface Web du Chat).

~~~
apt update && apt install ufw
ufw enable
ufw allow 5000/tcp
ufw allow ssh
~~~

## 2. Installation Côté Client (Utilisateurs)
Ces machines exécutent client.py pour recevoir les alertes et ouvrir le navigateur.

### A: Client Windows
### 1. Installation de Python

Téléchargez l'installateur sur python.org.

⚠️ TRÈS IMPORTANT : Lors de l'installation, cochez absolument la case "Add Python to PATH" en bas de la première fenêtre avant de cliquer sur "Install Now".

### 2. Pare-feu Windows

Au premier lancement du script (python client.py), une fenêtre de sécurité Windows apparaîtra.

Cochez "Réseaux privés" et cliquez sur "Autoriser l'accès".

### B: Client Linux
### 1. Installation des paquets Linux nécessite l'installation manuelle de la librairie graphique tkinter.

~~~
sudo apt-get update
sudo apt-get install -y python3 python3-tk
~~~

---
