"""
Dedicated Server Runner with remote control hook on port 5001.
"""
import sys
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import socket
import threading
import tkinter as tk
from tkinter import messagebox
import json
from server import ChatServerGUI, get_user_color

class ControlledServerGUI(ChatServerGUI):
    def handle_client(self, conn: socket.socket, addr: tuple):
        username = None
        try:
            f = conn.makefile("r", encoding="utf-8")
            first_line = f.readline()
            if not first_line:
                return

            handshake = json.loads(first_line.strip())
            if handshake.get("type") != "join":
                return

            req_username = handshake.get("username", "").strip()
            if not req_username:
                self.send_to_socket(conn, {"type": "join_ack", "success": False, "message": "ชื่อผู้ใช้ต้องไม่ว่างเปล่า"})
                return

            if "simulated_ip" in handshake:
                addr = (handshake["simulated_ip"], handshake.get("simulated_port", addr[1]))

            with self.lock:
                if req_username.lower() in [u["username"].lower() for u in self.clients.values()] or req_username.lower() == self.server_name.lower():
                    self.send_to_socket(
                        conn,
                        {"type": "join_ack", "success": False, "message": f"ชื่อ '{req_username}' มีผู้ใช้งานแล้ว กรุณาเลือกชื่ออื่น"},
                    )
                    return

                username = req_username
                user_color = get_user_color(username)
                self.clients[conn] = {"username": username, "addr": addr, "color": user_color}

            self.send_to_socket(
                conn,
                {"type": "join_ack", "success": True, "username": username, "color": user_color, "message": f"ยินดีต้อนรับคุณ {username} เข้าสู่ห้องแชท!"},
            )

            self.log("JOIN", f"🟢 คุณ {username} ({addr[0]}:{addr[1]}) เข้าร่วมห้องแชท")
            self.update_user_list_ui()
            self.broadcast_packet({"type": "system", "content": f"🟢 คุณ {username} ได้เข้าร่วมห้องแชท", "time": self.get_time_str()})
            self.broadcast_user_list()

            while self.is_running:
                line = f.readline()
                if not line or not self.process_client_packet(json.loads(line.strip()), username, user_color):
                    break

        except Exception:
            pass
        finally:
            self.remove_client(conn, username)

    def start_control_listener(self):
        t = threading.Thread(target=self._control_loop, daemon=True)
        t.start()

    def _control_loop(self):
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind(("127.0.0.1", 5001))
        srv.listen(5)
        while True:
            try:
                conn, _ = srv.accept()
                f = conn.makefile("r", encoding="utf-8")
                line = f.readline()
                if not line:
                    continue
                cmd = line.strip()
                if cmd == "START":
                    self.root.after(0, self.start_server)
                    conn.sendall(b"OK\n")
                elif cmd.startswith("CHAT "):
                    msg = cmd[len("CHAT "):]
                    def _do_chat(m=msg):
                        self.entry_msg.delete(0, "end")
                        self.entry_msg.insert(0, m)
                        self.send_chat_message()
                    self.root.after(0, _do_chat)
                    conn.sendall(b"OK\n")
                elif cmd.startswith("STICKER "):
                    parts = cmd[len("STICKER "):].split(" ", 1)
                    emo = parts[0]
                    title = parts[1] if len(parts) > 1 else ""
                    self.root.after(0, lambda e=emo, t=title: self.send_sticker(e, t))
                    conn.sendall(b"OK\n")
                elif cmd.startswith("KICK "):
                    conn.sendall(b"OK\n")
                elif cmd == "STOP":
                    self.root.after(0, self.stop_server)
                    conn.sendall(b"OK\n")
                elif cmd == "QUIT":
                    conn.sendall(b"OK\n")
                    self.root.after(100, self.root.destroy)
                    break
                conn.close()
            except Exception:
                pass


if __name__ == "__main__":
    root = tk.Tk()
    app = ControlledServerGUI(root)
    app.start_control_listener()
    root.mainloop()
