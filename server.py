"""ระบบเซิร์ฟเวอร์ห้องแชทกลุ่ม (Chat Server Control Panel)
พัฒนาด้วย Python TCP Socket, Multithreading และ Tkinter GUI
"""

import datetime
import hashlib
import json
import socket
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext
from typing import Optional

USER_COLORS = [
    "#E53935", "#1E88E5", "#43A047", "#FB8C00", "#8E24AA", "#00ACC1",
    "#D81B60", "#3949AB", "#00897B", "#F4511E", "#5E35B1", "#7CB342",
    "#6D4C41", "#0288D1", "#C0CA33", "#8D6E63",
]


def get_user_color(username: str) -> str:
    """คำนวณสีประจำตัวจากชื่อผู้ใช้แบบคงที่ (Deterministic Hashing)"""
    if not username:
        return "#1E88E5"
    h = int(hashlib.md5(username.strip().lower().encode("utf-8")).hexdigest(), 16)
    return USER_COLORS[h % len(USER_COLORS)]


class ChatServerGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Chat Server Control Panel - ระบบเซิร์ฟเวอร์ห้องแชท")
        self.root.geometry("860x600")
        self.root.minsize(750, 500)

        self.server_socket: Optional[socket.socket] = None
        self.is_running = False
        self.clients = {}  # {socket: {"username": str, "addr": tuple, "color": str}}
        self.lock = threading.Lock()

        self.setup_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_ui(self):
        self.root.configure(bg="#F0F2F5")
        f_font = "Segoe UI"

        # 1. แถบควบคุมด้านบน (Top Control Bar)
        top = tk.Frame(self.root, bg="#FFFFFF", padx=15, pady=12, bd=1, relief="solid")
        top.pack(fill="x", padx=15, pady=(15, 10))

        tk.Label(top, text="IP เซิร์ฟเวอร์:", font=(f_font, 10, "bold"), bg="#FFFFFF").pack(side="left", padx=(0, 5))
        self.entry_host = tk.Entry(top, font=(f_font, 10), width=12)
        self.entry_host.insert(0, "0.0.0.0")
        self.entry_host.pack(side="left", padx=(0, 15))

        tk.Label(top, text="Port:", font=(f_font, 10, "bold"), bg="#FFFFFF").pack(side="left", padx=(0, 5))
        self.entry_port = tk.Entry(top, font=(f_font, 10), width=6)
        self.entry_port.insert(0, "5000")
        self.entry_port.pack(side="left", padx=(0, 20))

        self.btn_toggle = tk.Button(
            top, text="▶ เริ่มเซิร์ฟเวอร์ (Start)", font=(f_font, 10, "bold"),
            bg="#2E7D32", fg="white", activebackground="#1B5E20", activeforeground="white",
            padx=12, pady=4, relief="flat", cursor="hand2", command=self.toggle_server,
        )
        self.btn_toggle.pack(side="left")

        self.lbl_status = tk.Label(
            top, text="● เซิร์ฟเวอร์: ปิดการทำงาน (Offline)", font=(f_font, 10, "bold"),
            fg="#D32F2F", bg="#FFFFFF",
        )
        self.lbl_status.pack(side="right")

        # 2. พื้นที่หลัก (Main Body)
        body = tk.Frame(self.root, bg="#F0F2F5")
        body.pack(fill="both", expand=True, padx=15, pady=5)

        # ฝั่งซ้าย: บันทึก Log การทำงาน
        left = tk.Frame(body, bg="#FFFFFF", bd=1, relief="solid")
        left.pack(side="left", fill="both", expand=True, padx=(0, 8))

        log_header = tk.Frame(left, bg="#FFFFFF", padx=10, pady=8)
        log_header.pack(fill="x")
        tk.Label(log_header, text="📋 บันทึกเหตุการณ์ (Server Logs)", font=(f_font, 11, "bold"), bg="#FFFFFF").pack(side="left")
        tk.Button(
            log_header, text="ล้างบันทึก", font=(f_font, 9), bg="#E0E0E0", relief="flat",
            padx=8, pady=2, cursor="hand2", command=self.clear_logs,
        ).pack(side="right")

        self.log_text = scrolledtext.ScrolledText(
            left, wrap="word", font=("Consolas", 10), bg="#1E1E1E", fg="#D4D4D4",
            insertbackground="white", padx=8, pady=8, bd=0,
        )
        self.log_text.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        for tag, fg in {
            "time": "#888888", "info": "#64B5F6", "join": "#81C784", "leave": "#E57373",
            "chat": "#FFFFFF", "sticker": "#FFB74D", "error": "#EF5350", "admin": "#BA68C8",
        }.items():
            self.log_text.tag_config(tag, foreground=fg)

        # ฝั่งขวา: รายชื่อผู้ใช้ออนไลน์
        right = tk.Frame(body, bg="#FFFFFF", bd=1, relief="solid", width=250)
        right.pack(side="right", fill="y", padx=(8, 0))
        right.pack_propagate(False)

        user_header = tk.Frame(right, bg="#FFFFFF", padx=10, pady=8)
        user_header.pack(fill="x")
        self.lbl_user_count = tk.Label(user_header, text="👥 ออนไลน์ (0 คน)", font=(f_font, 11, "bold"), bg="#FFFFFF")
        self.lbl_user_count.pack(side="left")

        self.user_listbox = tk.Listbox(
            right, font=(f_font, 10), bg="#FAFAFA", fg="#212121",
            selectbackground="#1E88E5", selectforeground="white", bd=1, relief="solid",
        )
        self.user_listbox.pack(fill="both", expand=True, padx=10, pady=(0, 8))

        tk.Button(
            right, text="⚠️ เตะผู้ใช้ที่เลือก (Kick)", font=(f_font, 9, "bold"),
            bg="#D32F2F", fg="white", activebackground="#B71C1C", activeforeground="white",
            relief="flat", padx=8, pady=5, cursor="hand2", command=self.kick_selected_user,
        ).pack(fill="x", padx=10, pady=(0, 10))

        # 3. แถบประกาศด้านล่าง (Bottom Announcement Bar)
        bottom = tk.Frame(self.root, bg="#FFFFFF", padx=15, pady=10, bd=1, relief="solid")
        bottom.pack(fill="x", padx=15, pady=(10, 15))

        tk.Label(bottom, text="📢 ประกาศ:", font=(f_font, 10, "bold"), bg="#FFFFFF").pack(side="left", padx=(0, 5))
        self.entry_broadcast = tk.Entry(bottom, font=(f_font, 10))
        self.entry_broadcast.pack(side="left", fill="x", expand=True, padx=5)
        self.entry_broadcast.bind("<Return>", lambda _: self.send_broadcast_message())

        tk.Button(
            bottom, text="ส่งประกาศ", font=(f_font, 10, "bold"),
            bg="#1976D2", fg="white", activebackground="#0D47A1", activeforeground="white",
            padx=15, pady=3, relief="flat", cursor="hand2", command=self.send_broadcast_message,
        ).pack(side="right", padx=(5, 0))

    def log(self, category: str, message: str):
        """บันทึกลงใน ScrolledText แบบ Thread-safe"""
        def _append():
            now = datetime.datetime.now().strftime("%H:%M:%S")
            cat = category.lower()
            self.log_text.insert("end", f"[{now}] ", "time")
            self.log_text.insert("end", f"[{category.upper()}] ", cat)
            self.log_text.insert("end", f"{message}\n", cat)
            self.log_text.see("end")

        self.root.after(0, _append)

    def clear_logs(self):
        self.log_text.delete("1.0", "end")

    def toggle_server(self):
        self.stop_server() if self.is_running else self.start_server()

    def start_server(self):
        host = self.entry_host.get().strip()
        port_str = self.entry_port.get().strip()

        if not port_str.isdigit():
            messagebox.showerror("ข้อผิดพลาด", "กรุณาระบุ Port เป็นตัวเลข")
            return

        port = int(port_str)
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((host, port))
            self.server_socket.listen(10)
            self.is_running = True

            self.btn_toggle.configure(text="⏹ หยุดเซิร์ฟเวอร์ (Stop)", bg="#C62828", activebackground="#8E0000")
            self.lbl_status.configure(text=f"● เซิร์ฟเวอร์: กำลังทำงานที่ {host}:{port}", fg="#2E7D32")
            self.entry_host.configure(state="disabled")
            self.entry_port.configure(state="disabled")

            self.log("INFO", f"เริ่มต้นเซิร์ฟเวอร์สำเร็จที่ {host}:{port}")
            threading.Thread(target=self.accept_loop, daemon=True).start()

        except Exception as err:
            messagebox.showerror("ข้อผิดพลาด", f"ไม่สามารถเปิดเซิร์ฟเวอร์ได้:\n{err}")
            if self.server_socket:
                try: self.server_socket.close()
                except Exception: pass
            self.server_socket = None
            self.is_running = False

    def stop_server(self):
        if not self.is_running:
            return

        self.is_running = False
        self.log("INFO", "กำลังปิดเซิร์ฟเวอร์...")
        self.broadcast_packet({"type": "system", "content": "⚠️ เซิร์ฟเวอร์ปิดให้บริการแล้ว", "time": self.get_time_str()})

        with self.lock:
            for sock in self.clients:
                try: sock.close()
                except Exception: pass
            self.clients.clear()

        if self.server_socket:
            try: self.server_socket.close()
            except Exception: pass
            self.server_socket = None

        self.btn_toggle.configure(text="▶ เริ่มเซิร์ฟเวอร์ (Start)", bg="#2E7D32", activebackground="#1B5E20")
        self.lbl_status.configure(text="● เซิร์ฟเวอร์: ปิดการทำงาน (Offline)", fg="#D32F2F")
        self.entry_host.configure(state="normal")
        self.entry_port.configure(state="normal")

        self.update_user_list_ui()
        self.log("INFO", "เซิร์ฟเวอร์หยุดการทำงานเรียบร้อยแล้ว")

    def accept_loop(self):
        while self.is_running and self.server_socket:
            try:
                conn, addr = self.server_socket.accept()
                threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True).start()
            except Exception:
                break

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

            with self.lock:
                if req_username.lower() in [u["username"].lower() for u in self.clients.values()]:
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

    def process_client_packet(self, packet: dict, username: str, user_color: str) -> bool:
        p_type = packet.get("type")
        if p_type == "leave":
            return False

        now = self.get_time_str()
        if p_type == "chat" and (content := packet.get("content", "").strip()):
            self.log("CHAT", f"<{username}> {content}")
            self.broadcast_packet({"type": "chat", "sender": username, "color": user_color, "content": content, "time": now})
        elif p_type == "sticker":
            self.log("STICKER", f"<{username}> ส่งสติ๊กเกอร์ [{packet.get('emoji')} {packet.get('title')}]")
            self.broadcast_packet({**packet, "sender": username, "color": user_color, "time": now})

        return True

    def remove_client(self, conn: socket.socket, username: Optional[str] = None):
        with self.lock:
            self.clients.pop(conn, None)

        try: conn.close()
        except Exception: pass

        if not username:
            return

        self.log("LEAVE", f"🔴 คุณ {username} ออกจากห้องแชท")
        self.update_user_list_ui()

        if self.is_running:
            self.broadcast_packet({"type": "system", "content": f"🔴 คุณ {username} ได้ออกจากห้องแชท", "time": self.get_time_str()})
            self.broadcast_user_list()

    def send_to_socket(self, sock: Optional[socket.socket], data: dict):
        if sock:
            try:
                sock.sendall((json.dumps(data, ensure_ascii=False) + "\n").encode("utf-8"))
            except Exception:
                pass

    def broadcast_packet(self, data: dict, sender_conn: Optional[socket.socket] = None):
        raw = (json.dumps(data, ensure_ascii=False) + "\n").encode("utf-8")
        dead_sockets = []

        with self.lock:
            for sock in self.clients:
                if sock != sender_conn:
                    try: sock.sendall(raw)
                    except Exception: dead_sockets.append(sock)

            for dead in dead_sockets:
                try: dead.close()
                except Exception: pass
                self.clients.pop(dead, None)

    def broadcast_user_list(self):
        with self.lock:
            users = [{"username": info["username"], "color": info["color"]} for info in self.clients.values()]
        self.broadcast_packet({"type": "user_list", "users": users, "count": len(users)})

    def update_user_list_ui(self):
        def _update():
            self.user_listbox.delete(0, "end")
            with self.lock:
                self.lbl_user_count.configure(text=f"👥 ออนไลน์ ({len(self.clients)} คน)")
                for info in self.clients.values():
                    self.user_listbox.insert("end", f"{info['username']} ({info['addr'][0]}:{info['addr'][1]})")

        self.root.after(0, _update)

    def kick_selected_user(self):
        sel = self.user_listbox.curselection()
        if not sel:
            messagebox.showinfo("แจ้งเตือน", "กรุณาเลือกผู้ใช้งานที่ต้องการเตะจากรายการ")
            return

        target_username = self.user_listbox.get(sel[0]).split(" (")[0]
        if not messagebox.askyesno("ยืนยัน", f"คุณต้องการเตะคุณ '{target_username}' ออกจากเซิร์ฟเวอร์ใช่หรือไม่?"):
            return

        target_sock = None
        with self.lock:
            for sock, info in self.clients.items():
                if info["username"] == target_username:
                    target_sock = sock
                    break

        if target_sock:
            self.send_to_socket(target_sock, {"type": "kicked", "reason": "คุณถูกเตะออกจากห้องโดยผู้ดูแลระบบ"})
            self.log("ADMIN", f"⚠️ ผู้ดูแลระบบได้เตะคุณ {target_username} ออกจากห้องแชท")
            self.remove_client(target_sock, target_username)

    def send_broadcast_message(self):
        msg = self.entry_broadcast.get().strip()
        if not msg:
            return

        if not self.is_running:
            messagebox.showwarning("แจ้งเตือน", "เซิร์ฟเวอร์ยังไม่ได้เปิดใช้งาน")
            return

        self.entry_broadcast.delete(0, "end")
        self.log("ADMIN", f"📢 ส่งประกาศ: {msg}")
        self.broadcast_packet({
            "type": "chat",
            "sender": "👑 Server Admin",
            "color": "#D32F2F",
            "content": f"📢 [ประกาศ]: {msg}",
            "time": self.get_time_str(),
        })

    def get_time_str(self) -> str:
        return datetime.datetime.now().strftime("%H:%M")

    def on_closing(self):
        if self.is_running and not messagebox.askyesno("ยืนยันการปิด", "เซิร์ฟเวอร์กำลังทำงานอยู่ คุณต้องการปิดเซิร์ฟเวอร์และออกจากโปรแกรมใช่หรือไม่?"):
            return
        if self.is_running:
            self.stop_server()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    ChatServerGUI(root)
    root.mainloop()
