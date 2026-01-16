import subprocess
import time
import socket
import re
import threading
from flask import Flask, render_template_string, request
from flask_socketio import SocketIO, emit, join_room

CHECK_INTERVAL = 3
CLIENT_PORT = 8080 #port utiliser pour communiquer entre les machines
CONTAINER_NAME = "samba"
TARGET_EXT = [".docx", ".xlsx", ".xls", ".odt"]
WEB_PORT = 5000 #port web
SERVER_IP = "xx.xx.xx.xx" #addresse ip du serveur utilisé

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key_samba'
socketio = SocketIO(app, cors_allowed_origins="*")

active_conflicts = {}

#HTML de la page web qui s'ouvre lors du conflit
CHAT_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Conflit : {{ filename }}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background-color: #f0f2f5; margin: 0; display: flex; flex-direction: column; height: 100vh; }
        header { background-color: #d32f2f; color: white; padding: 15px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.2); }
        h2 { margin: 0; font-size: 1.2rem; }
        #chat-container { flex: 1; padding: 20px; overflow-y: auto; display: flex; flex-direction: column; gap: 10px; }
        .msg { padding: 10px 15px; border-radius: 20px; max-width: 70%; word-wrap: break-word; font-size: 0.95rem; }
        .msg.me { align-self: flex-end; background-color: #0084ff; color: white; border-bottom-right-radius: 5px; }
        .msg.other { align-self: flex-start; background-color: #e4e6eb; color: black; border-bottom-left-radius: 5px; }
        .sys { align-self: center; background-color: #fff3cd; color: #856404; font-size: 0.8rem; padding: 5px 10px; border-radius: 10px; }
        footer { padding: 15px; background: white; display: flex; gap: 10px; border-top: 1px solid #ddd; }
        input { flex: 1; padding: 10px; border-radius: 20px; border: 1px solid #ccc; outline: none; }
        button { padding: 10px 20px; border-radius: 20px; border: none; background-color: #0084ff; color: white; font-weight: bold; cursor: pointer; }
    </style>
</head>
<body>
    <header>
        <h2>⚠️ Fichier déjà ouvert !</h2>
        <small>{{ filename }}</small>
    </header>
    <div id="chat-container">
        <div class="sys">Discussion ouverte avec les autres utilisateurs.</div>
    </div>
    <footer>
        <input id="msgInput" type="text" placeholder="Envoyer un message..." autofocus>
        <button onclick="send()">Envoyer</button>
    </footer>
    <script>
        const socket = io();
        const room = "{{ filename }}";
        const myIp = "{{ user_ip }}";
        const chatBox = document.getElementById('chat-container');
        socket.emit('join', {room: room, ip: myIp});
        socket.on('message', (data) => {
            const div = document.createElement('div');
            if (data.ip === 'SYS') {
                div.className = 'sys';
                div.textContent = data.msg;
            } else {
                div.className = 'msg ' + (data.ip === myIp ? 'me' : 'other');
                div.textContent = (data.ip !== myIp ? data.ip + ': ' : '') + data.msg;
            }
            chatBox.appendChild(div);
            chatBox.scrollTop = chatBox.scrollHeight;
        });
        function send() {
            const input = document.getElementById('msgInput');
            if (input.value.trim()) {
                socket.emit('message', {room: room, msg: input.value, ip: myIp});
                input.value = '';
            }
        }
        document.getElementById('msgInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') send();
        });
    </script>
</body>
</html>
"""

@app.route('/chat/<filename>')
def chat_room(filename):
    return render_template_string(CHAT_HTML, filename=filename, user_ip=request.remote_addr)

@socketio.on('join')
def on_join(data):
    join_room(data['room'])

@socketio.on('message')
def handle_msg(data):
    emit('message', data, room=data['room'])

def send_open_url(ip, url):
    try:
        msg = f"URL|{url}"
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            s.connect((ip, CLIENT_PORT))
            s.sendall(msg.encode('utf-8'))
            print(f"-> Ordre URL envoyé à {ip}")
    except Exception as e:
        print(f"-> Echec connexion {ip}: {e}")

def get_docker_locks():
    pid_ip_map = {}
    file_users = {}
    try:
        # 1. On récupère les IPs sans afficher les erreurs Samba
        cmd_p = ['docker', 'exec', CONTAINER_NAME, 'smbstatus', '-s', '/etc/samba/smb.conf', '-p', '-n']
        out_p = subprocess.check_output(cmd_p, text=True, stderr=subprocess.DEVNULL)
        for line in out_p.splitlines():
            parts = line.split()
            if len(parts) >= 4 and parts[0].isdigit():
                pid_ip_map[parts[0]] = parts[3]

        # 2. On récupère les fichiers verrouillés
        cmd_l = ['docker', 'exec', CONTAINER_NAME, 'smbstatus', '-s', '/etc/samba/smb.conf', '-L', '-n']
        out_l = subprocess.check_output(cmd_l, text=True, stderr=subprocess.DEVNULL)
        
        for line in out_l.splitlines():
            # On vérifie si la ligne contient l'une de nos extensions
            if any(ext in line for ext in TARGET_EXTS):
                if 'DENY_NONE' in line and 'RDONLY' in line: continue
                
                parts = line.split()
                if len(parts) >= 5 and parts[0].isdigit():
                    pid = parts[0]
                    # On extrait le nom du fichier dynamiquement selon l'extension trouvée
                    # Cette regex cherche n'importe quel nom finissant par une de nos extensions
                    match = re.search(r'([^/]+\.(docx|xlsx|xls|odt))', line)
                    if match:
                        fname = match.group(1)
                        if fname.startswith('~$'): continue
                        
                        if pid in pid_ip_map:
                            ip = pid_ip_map[pid]
                            if fname not in file_users: file_users[fname] = []
                            if ip not in file_users[fname]: file_users[fname].append(ip)
                            
    except Exception:
        pass 
    return file_users

def monitor_loop():
    global active_conflicts
    print(f"--- Surveillance Active (Web: http://{SERVER_IP}:{WEB_PORT}) ---")
    while True:
        try:
            current_locks = get_docker_locks()
            for fname, ips in current_locks.items():
                unique_ips = list(set(ips))
                if len(unique_ips) > 1:
                    unique_ips.sort()
                    if active_conflicts.get(fname) != unique_ips:
                        print(f"[!] CONFLIT {fname} : {unique_ips}")
                        url = f"http://{SERVER_IP}:{WEB_PORT}/chat/{fname}"
                        for target_ip in unique_ips:
                            send_open_url(target_ip, url)
                        active_conflicts[fname] = unique_ips
                else:
                    if fname in active_conflicts:
                        del active_conflicts[fname]
        except Exception as e:
            print(f"Erreur Loop: {e}")
        socketio.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    socketio.start_background_task(monitor_loop)

    socketio.run(app, host='0.0.0.0', port=WEB_PORT, allow_unsafe_werkzeug=True)

