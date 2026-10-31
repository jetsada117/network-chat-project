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

STICKERS = [
    ("👍", "สุดยอดเลย!", "#E8F5E9", "#2E7D32"),
    ("❤️", "รักเลย", "#FFEBEE", "#C62828"),
    ("🎉", "ยินดีด้วย!", "#FFF8E1", "#F57F17"),
    ("😂", "ขำกลิ้ง", "#FFFDE7", "#FBC02D"),
    ("🔥", "ไฟลุก!", "#FBE9E7", "#D84315"),
    ("😴", "ง่วงนอนแล้ว", "#EDE7F6", "#512DA8"),
    ("🙏", "ขอบคุณครับ", "#E0F7FA", "#00838F"),
    ("🍕", "หิวข้าวมาก", "#FBE9E7", "#E64A19"),
    ("☕", "พักดื่มกาแฟ", "#EFEBE9", "#4E342E"),
    ("💻", "กำลังปั่นงาน", "#E3F2FD", "#1565C0"),
    ("🥳", "ฉลองกัน!", "#FCE4EC", "#AD1457"),
    ("🏃", "ขอตัวก่อนนะ", "#E0F2F1", "#00695C"),
]

STICKER_PALETTE = {emoji: (bg, fg) for emoji, title, bg, fg in STICKERS}

POPULAR_EMOJIS = [
    "😀", "😃", "😄", "😁", "😆", "😅", "😂", "🤣", "😊", "😇",
    "🙂", "😉", "😍", "🥰", "😘", "😋", "😜", "😎", "🥳", "🥺",
    "😭", "😱", "😡", "💩", "👍", "👎", "👏", "🙌", "🙏", "🤝",
    "❤️", "🧡", "💛", "💚", "💙", "💜", "💔", "💖", "✨", "🔥",
    "💯", "🚀", "💡", "☕", "🍕", "🍔", "🐱", "🐶", "💻", "🎮",
]


def get_user_color(username: str) -> str:
    """คำนวณสีประจำตัวจากชื่อผู้ใช้แบบคงที่ (Deterministic Hashing)"""
    if not username:
        return "#1E88E5"
    h = int(hashlib.md5(username.strip().lower().encode("utf-8")).hexdigest(), 16)
    return USER_COLORS[h % len(USER_COLORS)]


def get_lan_ip() -> str:
    """ค้นหา IPv4 Address ของเครื่องในวง LAN แบบอัตโนมัติ"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        try:
            ip = socket.gethostbyname(socket.gethostname())
        except Exception:
            ip = "127.0.0.1"
    finally:
        s.close()
    return ip


class ChatServerGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Chat Server Control Panel - ระบบเซิร์ฟเวอร์ห้องแชท")
        self.root.geometry("880x700")
        self.root.minsize(820, 580)

        self.server_socket: Optional[socket.socket] = None
        self.is_running = False
        self.clients = {}  # {socket: {"username": str, "addr": tuple, "color": str}}
        self.lock = threading.Lock()
        self.server_name = "Server"
        self.server_color = get_user_color(self.server_name)
        self.emoji_window: Optional[tk.Toplevel] = None
        self.sticker_window: Optional[tk.Toplevel] = None

        self.setup_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_ui(self):
        self.root.configure(bg="#F0F2F5")
        f_font = "Segoe UI"

        # 1. แถบควบคุมด้านบน (Top Control Bar)
        top = tk.Frame(self.root, bg="#FFFFFF", padx=15, pady=12, bd=1, relief="solid")
        top.pack(fill="x", padx=15, pady=(15, 10))

        # แถวที่ 1: แถบตั้งค่าและสถานะ (Row 1: Controls & Status)
        row_ctrl = tk.Frame(top, bg="#FFFFFF")
        row_ctrl.pack(fill="x")

        tk.Label(row_ctrl, text="IP เซิร์ฟเวอร์:", font=(f_font, 10, "bold"), bg="#FFFFFF").pack(side="left", padx=(0, 5))
        self.entry_host = tk.Entry(row_ctrl, font=(f_font, 10), width=10)
        self.entry_host.insert(0, "0.0.0.0")
        self.entry_host.pack(side="left", padx=(0, 15))

        tk.Label(row_ctrl, text="Port:", font=(f_font, 10, "bold"), bg="#FFFFFF").pack(side="left", padx=(0, 5))
        self.entry_port = tk.Entry(row_ctrl, font=(f_font, 10), width=6)
        self.entry_port.insert(0, "5000")
        self.entry_port.pack(side="left", padx=(0, 15))

        self.btn_toggle = tk.Button(
            row_ctrl, text="▶ เริ่มเซิร์ฟเวอร์ (Start)", font=(f_font, 10, "bold"),
            bg="#2E7D32", fg="white", activebackground="#1B5E20", activeforeground="white",
            padx=14, pady=4, relief="flat", cursor="hand2", command=self.toggle_server,
        )
        self.btn_toggle.pack(side="left")

        self.lbl_status = tk.Label(
            row_ctrl, text="● เซิร์ฟเวอร์: ปิดการทำงาน (Offline)", font=(f_font, 10, "bold"),
            fg="#D32F2F", bg="#FFFFFF",
        )
        self.lbl_status.pack(side="right")

        # แถวที่ 2: แถบแสดง IP สำหรับเพื่อนในวง LAN (Row 2: LAN IP Banner มีระยะเว้นว่างชัดเจน)
        self.frame_lan_banner = tk.Frame(top, bg="#E8F0FE", padx=14, pady=8, bd=1, relief="solid")

        tk.Label(
            self.frame_lan_banner, text="🌐 IP ในวง LAN สำหรับให้เพื่อนเชื่อมต่อ:",
            font=(f_font, 10, "bold"), bg="#E8F0FE", fg="#1565C0",
        ).pack(side="left", padx=(0, 10))

        self.lbl_lan_ip_val = tk.Label(
            self.frame_lan_banner, text="", font=("Consolas", 12, "bold"),
            bg="#FFFFFF", fg="#0D47A1", padx=12, pady=3, bd=1, relief="solid",
        )
        self.lbl_lan_ip_val.pack(side="left", padx=(0, 15))

        self.lbl_lan_hint = tk.Label(
            self.frame_lan_banner, text="💡 (แจ้งเลข IP นี้ให้เพื่อนกรอกที่ช่อง 'IP เซิร์ฟเวอร์' ในโปรแกรม Client)",
            font=(f_font, 9), bg="#E8F0FE", fg="#424242",
        )
        self.lbl_lan_hint.pack(side="left")

        # 2. แถบส่งข้อความและสติ๊กเกอร์ด้านล่าง (Bottom Chat & Action Bar)
        # ประกาศและ pack side="bottom" ก่อน body เพื่อให้อยู่ด้านล่างเสมอ ไม่ถูกดันหายเมื่อเปิด LAN banner
        bottom = tk.Frame(self.root, bg="#FFFFFF", padx=12, pady=10, bd=1, relief="solid")
        bottom.pack(side="bottom", fill="x", padx=15, pady=(5, 12))

        self.btn_emoji = tk.Button(
            bottom,
            text="😀 อีโมจิ",
            font=(f_font, 9, "bold"),
            bg="#FFF8E1",
            fg="#F57F17",
            activebackground="#FFECB3",
            relief="flat",
            padx=10,
            pady=5,
            cursor="hand2",
            command=self.toggle_emoji_picker,
        )
        self.btn_emoji.pack(side="left", padx=(0, 5))

        self.btn_sticker = tk.Button(
            bottom,
            text="🏷️ สติ๊กเกอร์",
            font=(f_font, 9, "bold"),
            bg="#E8F5E9",
            fg="#2E7D32",
            activebackground="#C8E6C9",
            relief="flat",
            padx=10,
            pady=5,
            cursor="hand2",
            command=self.toggle_sticker_picker,
        )
        self.btn_sticker.pack(side="left", padx=(0, 8))

        self.entry_msg = tk.Entry(
            bottom, font=(f_font, 11), bg="#F8F9FA", bd=1, relief="solid"
        )
        self.entry_msg.pack(side="left", fill="x", expand=True, padx=(0, 8), ipady=4)
        self.entry_msg.bind("<Return>", lambda _: self.send_chat_message())
        self.entry_broadcast = self.entry_msg

        self.btn_send = tk.Button(
            bottom,
            text="ส่ง (Send) ✈️",
            font=(f_font, 10, "bold"),
            bg="#1976D2",
            fg="white",
            activebackground="#0D47A1",
            activeforeground="white",
            relief="flat",
            padx=15,
            pady=5,
            cursor="hand2",
            command=self.send_chat_message,
        )
        self.btn_send.pack(side="right")

        # 3. พื้นที่หลัก (Main Body) - expand เติมเต็มพื้นที่ระหว่าง top กับ bottom
        body = tk.Frame(self.root, bg="#F0F2F5")
        body.pack(fill="both", expand=True, padx=15, pady=5)

        # ฝั่งซ้าย: บันทึก Log การทำงาน
        left = tk.Frame(body, bg="#FFFFFF", bd=1, relief="solid")
        left.pack(side="left", fill="both", expand=True, padx=(0, 8))

        log_header = tk.Frame(left, bg="#FFFFFF", padx=10, pady=8)
        log_header.pack(fill="x")
        tk.Label(log_header, text="📋 การสนทนาและบันทึกเหตุการณ์ (Live Chat & Logs)", font=(f_font, 11, "bold"), bg="#FFFFFF").pack(side="left")

        self.log_text = scrolledtext.ScrolledText(
            left, wrap="word", font=(f_font, 10), bg="#FFFFFF", fg="#212121",
            insertbackground="black", padx=12, pady=10, bd=0, state="disabled", cursor="arrow",
        )
        self.log_text.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        for tag, (fg, bold) in {
            "time": ("#888888", False),
            "info": ("#1976D2", True),
            "join": ("#2E7D32", True),
            "leave": ("#D32F2F", True),
            "chat": ("#212121", False),
            "error": ("#C62828", True),
            "admin": ("#7B1FA2", True),
            "admin_badge": ("#D32F2F", True),
            "admin_msg": ("#B71C1C", True),
        }.items():
            font_prop = (f_font, 10, "bold") if bold else (f_font, 10)
            self.log_text.tag_config(tag, foreground=fg, font=font_prop)

        # ฝั่งขวา: รายชื่อผู้ใช้ออนไลน์
        right = tk.Frame(body, bg="#FFFFFF", bd=1, relief="solid", width=250)
        right.pack(side="right", fill="y", padx=(8, 0))
        right.pack_propagate(False)

        user_header = tk.Frame(right, bg="#FFFFFF", padx=10, pady=8)
        user_header.pack(fill="x")
        self.lbl_user_count = tk.Label(user_header, text="👥 ออนไลน์ (0 คน)", font=(f_font, 11, "bold"), bg="#FFFFFF")
        self.lbl_user_count.pack(side="left")

        self.users_display = tk.Text(
            right, font=(f_font, 10), bg="#FAFAFA", fg="#212121",
            padx=10, pady=8, bd=1, relief="solid", state="disabled", cursor="hand2",
            wrap="none",
        )
        self.users_display.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.users_display.tag_config("user_text", font=(f_font, 10, "bold"), foreground="#212121")
        self.users_display.tag_config("ip_text", font=(f_font, 9), foreground="#616161")
        self.users_display.tag_config("host_text", font=(f_font, 10, "bold"), foreground="#1976D2")

        # สำหรับ backward compatibility
        self.user_listbox = self.users_display


    def _write_log(self, fn):
        """จัดการเขียนข้อความลง ScrolledText แบบ Read-only ป้องกันผู้ใช้แก้ไขหรือลบแชทบนหน้าจอ"""
        self.log_text.configure(state="normal")
        fn()
        self.log_text.configure(state="disabled")
        self.log_text.see("end")

    def log(self, category: str, message: str):
        """บันทึกลงใน ScrolledText แบบ Thread-safe"""
        def _append():
            def _insert():
                now = datetime.datetime.now().strftime("%H:%M:%S")
                cat = category.lower()
                self.log_text.insert("end", f"[{now}] ", "time")
                self.log_text.insert("end", f"[{category.upper()}] ", cat)
                self.log_text.insert("end", f"{message}\n", cat)
            self._write_log(_insert)

        self.root.after(0, _append)

    def append_chat_message(self, sender: str, color: str, content: str, time_str: str):
        """แสดงข้อความแชทของผู้ใช้พร้อมสีประจำตัวในหน้าต่าง Server แบบ Thread-safe"""
        def _append():
            def _insert():
                self.log_text.insert("end", f"[{time_str}] ", "time")
                tag_name = f"u_{sender}_{abs(hash(color))}"
                self.log_text.tag_config(tag_name, foreground=color, font=("Segoe UI", 10, "bold"))
                self.log_text.insert("end", f"{sender}: ", tag_name)
                self.log_text.insert("end", f"{content}\n", "chat")
            self._write_log(_insert)

        self.root.after(0, _append)

    def append_sticker_message(self, sender: str, color: str, emoji: str, title: str, time_str: str):
        """แสดงสติ๊กเกอร์การ์ดกราฟิกในหน้าต่าง Server เหมือนฝั่ง Client แบบ Thread-safe"""
        def _append():
            def _insert():
                self.log_text.insert("end", f"[{time_str}] ", "time")
                tag_name = f"u_{sender}_{abs(hash(color))}"
                self.log_text.tag_config(tag_name, foreground=color, font=("Segoe UI", 10, "bold"))
                self.log_text.insert("end", f"{sender} ส่งสติ๊กเกอร์:\n", tag_name)

                bg_col, badge_col = STICKER_PALETTE.get(emoji, ("#F5F6F8", "#333333"))
                card = tk.Frame(self.log_text, bg=bg_col, bd=1, relief="solid", padx=16, pady=8)
                tk.Label(card, text=emoji, font=("Segoe UI Emoji", 26), bg=bg_col).pack()
                tk.Label(
                    card,
                    text=f" {title} ",
                    font=("Segoe UI", 9, "bold"),
                    bg="#FFFFFF",
                    fg=badge_col,
                    padx=8,
                    pady=2,
                    relief="solid",
                    bd=1,
                ).pack(pady=(3, 0))

                self.log_text.insert("end", "   ")
                self.log_text.window_create("end", window=card)
                self.log_text.insert("end", "\n\n")
            self._write_log(_insert)

        self.root.after(0, _append)

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
            self.lbl_status.configure(text="● เซิร์ฟเวอร์: กำลังทำงาน (Online)", fg="#2E7D32")
            self.entry_host.configure(state="disabled")
            self.entry_port.configure(state="disabled")

            lan_ip = get_lan_ip()
            self.lbl_lan_ip_val.configure(text=f"{lan_ip}")
            self.frame_lan_banner.pack(fill="x", pady=(10, 0))
            self.update_user_list_ui()

            self.log("INFO", f"เริ่มต้นเซิร์ฟเวอร์สำเร็จที่ {host}:{port}")
            self.log("INFO", f"🌐 IP เครื่องคุณในวง LAN คือ: {lan_ip} (Port: {port})")
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
        self.frame_lan_banner.pack_forget()
        self.entry_host.configure(state="normal")
        self.entry_port.configure(state="normal")

        if self.emoji_window and self.emoji_window.winfo_exists():
            try: self.emoji_window.destroy()
            except Exception: pass
            self.emoji_window = None
        if self.sticker_window and self.sticker_window.winfo_exists():
            try: self.sticker_window.destroy()
            except Exception: pass
            self.sticker_window = None

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

    def process_client_packet(self, packet: dict, username: str, user_color: str) -> bool:
        p_type = packet.get("type")
        if p_type == "leave":
            return False

        now = self.get_time_str()
        if p_type == "chat" and (content := packet.get("content", "").strip()):
            self.append_chat_message(username, user_color, content, now)
            self.broadcast_packet({"type": "chat", "sender": username, "color": user_color, "content": content, "time": now})
        elif p_type == "sticker":
            emoji = packet.get("emoji", "🏷️")
            title = packet.get("title", "สติ๊กเกอร์")
            self.append_sticker_message(username, user_color, emoji, title, now)
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
            client_users = [
                {
                    "username": info["username"],
                    "color": info["color"],
                    "ip": info["addr"][0],
                    "port": info["addr"][1],
                    "addr_str": f"{info['addr'][0]}:{info['addr'][1]}",
                    "is_host": False,
                }
                for info in self.clients.values()
            ]
        server_info = []
        if self.is_running:
            port_val = 5000
            try:
                port_val = int(self.entry_port.get().strip())
            except Exception:
                pass
            server_info = [{
                "username": self.server_name,
                "color": self.server_color,
                "ip": get_lan_ip(),
                "port": port_val,
                "addr_str": "โฮสต์",
                "is_host": True,
            }]
        users = server_info + client_users
        self.broadcast_packet({"type": "user_list", "users": users, "count": len(users)})

    def update_user_list_ui(self):
        def _update():
            self.users_display.configure(state="normal")
            self.users_display.delete("1.0", "end")

            with self.lock:
                total_count = len(self.clients) + (1 if self.is_running else 0)
                self.lbl_user_count.configure(text=f"👥 ออนไลน์ ({total_count} คน)")

                displayed = []
                if self.is_running:
                    displayed.append({
                        "username": self.server_name,
                        "color": self.server_color,
                        "addr_str": "โฮสต์",
                        "is_host": True,
                    })
                for info in self.clients.values():
                    displayed.append({
                        "username": info["username"],
                        "color": info["color"],
                        "addr_str": f"{info['addr'][0]}:{info['addr'][1]}",
                        "is_host": False,
                    })

            for u in displayed:
                name = u["username"]
                color = u["color"]
                tag_name = f"dot_{name}_{abs(hash(color))}"
                self.users_display.tag_config(
                    tag_name, foreground=color, font=("Segoe UI", 11, "bold")
                )
                self.users_display.insert("end", " ● ", tag_name)

                if u["is_host"]:
                    self.users_display.insert("end", f"{name}", "host_text")
                else:
                    self.users_display.insert("end", f"{name}", "user_text")
                self.users_display.insert("end", f" ({u['addr_str']})\n", "ip_text")

            self.users_display.configure(state="disabled")



        self.root.after(0, _update)

    def send_chat_message(self):
        if not self.is_running:
            messagebox.showwarning("แจ้งเตือน", "กรุณาเปิดเซิร์ฟเวอร์ก่อนส่งข้อความ")
            return

        msg = self.entry_msg.get().strip()
        if not msg:
            return

        self.entry_msg.delete(0, "end")
        now = self.get_time_str()

        self.append_chat_message(self.server_name, self.server_color, msg, now)

        self.broadcast_packet({
            "type": "chat",
            "sender": self.server_name,
            "color": self.server_color,
            "content": msg,
            "time": now,
        })

    def send_broadcast_message(self):
        self.send_chat_message()

    def send_sticker(self, emoji: str, title: str):
        if not self.is_running:
            messagebox.showwarning("แจ้งเตือน", "กรุณาเปิดเซิร์ฟเวอร์ก่อนส่งสติ๊กเกอร์")
            return

        now = self.get_time_str()
        self.append_sticker_message(self.server_name, self.server_color, emoji, title, now)

        self.broadcast_packet({
            "type": "sticker",
            "sender": self.server_name,
            "color": self.server_color,
            "emoji": emoji,
            "title": title,
            "time": now,
        })

    def _create_popup(
        self, btn: tk.Button, title: str, w: int, h: int, dy: int
    ) -> tk.Toplevel:
        p = tk.Toplevel(self.root, bg="#FFFFFF")
        p.title(title)
        p.geometry(f"{w}x{h}")
        p.resizable(False, False)
        p.transient(self.root)
        bx, by = max(10, btn.winfo_rootx()), max(10, btn.winfo_rooty() - dy)
        p.geometry(f"+{bx}+{by}")
        return p

    def toggle_emoji_picker(self):
        if self.emoji_window and self.emoji_window.winfo_exists():
            self.emoji_window.destroy()
            self.emoji_window = None
            return

        if self.sticker_window and self.sticker_window.winfo_exists():
            self.sticker_window.destroy()
            self.sticker_window = None

        p = self._create_popup(self.btn_emoji, "เลือกอีโมจิ (Emoji)", 360, 280, 300)
        self.emoji_window = p

        tk.Label(
            p,
            text="แตะอีโมจิเพื่อพิมพ์ลงในข้อความ",
            font=("Segoe UI", 9, "bold"),
            bg="#FFFFFF",
            fg="#616161",
        ).pack(pady=8)

        grid = tk.Frame(p, bg="#FFFFFF")
        grid.pack(padx=10, pady=5)
        for i, emo in enumerate(POPULAR_EMOJIS):
            tk.Button(
                grid,
                text=emo,
                font=("Segoe UI Emoji", 14),
                bg="#FFFFFF",
                activebackground="#E3F2FD",
                relief="flat",
                width=2,
                cursor="hand2",
                command=lambda e=emo: (
                    self.entry_msg.insert(tk.INSERT, e),
                    self.entry_msg.focus_set(),
                ),
            ).grid(row=i // 10, column=i % 10, padx=2, pady=2)

    def toggle_sticker_picker(self):
        if self.sticker_window and self.sticker_window.winfo_exists():
            self.sticker_window.destroy()
            self.sticker_window = None
            return

        if self.emoji_window and self.emoji_window.winfo_exists():
            self.emoji_window.destroy()
            self.emoji_window = None

        p = self._create_popup(
            self.btn_sticker, "เลือกสติ๊กเกอร์ (Stickers)", 420, 340, 360
        )
        self.sticker_window = p

        tk.Label(
            p,
            text="แตะสติ๊กเกอร์เพื่อส่งทันที",
            font=("Segoe UI", 10, "bold"),
            bg="#FFFFFF",
            fg="#2E7D32",
        ).pack(pady=8)

        grid = tk.Frame(p, bg="#FFFFFF")
        grid.pack(padx=10, pady=5)
        for i, (emoji, title, bg, badge) in enumerate(STICKERS):
            tk.Button(
                grid,
                text=f"{emoji}\n{title}",
                font=("Segoe UI Emoji", 11, "bold"),
                bg=bg,
                fg=badge,
                activebackground="#CFD8DC",
                relief="solid",
                bd=1,
                width=11,
                height=3,
                cursor="hand2",
                command=lambda e=emoji, t=title: (p.destroy(), self.send_sticker(e, t)),
            ).grid(row=i // 3, column=i % 3, padx=5, pady=5)

    def get_time_str(self) -> str:
        return datetime.datetime.now().strftime("%H:%M")

    def on_closing(self):
        if self.is_running and not messagebox.askyesno("ยืนยันการปิด", "เซิร์ฟเวอร์กำลังทำงานอยู่ คุณต้องการปิดเซิร์ฟเวอร์และออกจากโปรแกรมใช่หรือไม่?"):
            return
        if self.emoji_window and self.emoji_window.winfo_exists():
            try: self.emoji_window.destroy()
            except Exception: pass
        if self.sticker_window and self.sticker_window.winfo_exists():
            try: self.sticker_window.destroy()
            except Exception: pass
        if self.is_running:
            self.stop_server()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    ChatServerGUI(root)
    root.mainloop()
