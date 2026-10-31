"""โปรแกรมลูกข่ายห้องแชทกลุ่ม (Group Chat Client)
พัฒนาด้วย Python TCP Socket, Multithreading และ Tkinter GUI
"""

import hashlib
import json
import socket
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext
from typing import Optional

USER_COLORS = [
    "#E53935",
    "#1E88E5",
    "#43A047",
    "#FB8C00",
    "#8E24AA",
    "#00ACC1",
    "#D81B60",
    "#3949AB",
    "#00897B",
    "#F4511E",
    "#5E35B1",
    "#7CB342",
    "#6D4C41",
    "#0288D1",
    "#C0CA33",
    "#8D6E63",
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

POPULAR_EMOJIS = [
    "😀",
    "😃",
    "😄",
    "😁",
    "😆",
    "😅",
    "😂",
    "🤣",
    "😊",
    "😇",
    "🙂",
    "😉",
    "😍",
    "🥰",
    "😘",
    "😋",
    "😜",
    "😎",
    "🥳",
    "🥺",
    "😭",
    "😱",
    "😡",
    "💩",
    "👍",
    "👎",
    "👏",
    "🙌",
    "🙏",
    "🤝",
    "❤️",
    "🧡",
    "💛",
    "💚",
    "💙",
    "💜",
    "💔",
    "💖",
    "✨",
    "🔥",
    "💯",
    "🚀",
    "💡",
    "☕",
    "🍕",
    "🍔",
    "🐱",
    "🐶",
    "💻",
    "🎮",
]


def get_user_color(username: str) -> str:
    """คำนวณสีประจำตัวจากชื่อผู้ใช้แบบคงที่ (Deterministic Hashing)"""
    if not username:
        return "#1E88E5"
    h = int(hashlib.md5(username.strip().lower().encode("utf-8")).hexdigest(), 16)
    return USER_COLORS[h % len(USER_COLORS)]


class ChatClientGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Group Chat Client - ห้องแชทกลุ่ม")
        self.root.geometry("860x620")
        self.root.minsize(700, 500)

        self.client_socket: Optional[socket.socket] = None
        self.file_reader = None
        self.is_connected = False
        self.my_username = ""
        self.my_color = "#1E88E5"
        self.font_family = "Segoe UI"

        self.container = tk.Frame(self.root, bg="#F0F2F5")
        self.container.pack(fill="both", expand=True)

        self.setup_login_view()
        self.setup_chat_view()
        self.show_login_view()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    # ---------------- 1. หน้าต่างเข้าสู่ระบบ (Login View) ----------------

    def setup_login_view(self):
        self.login_frame = tk.Frame(self.container, bg="#F0F2F5")
        card = tk.Frame(
            self.login_frame, bg="#FFFFFF", padx=35, pady=30, bd=1, relief="solid"
        )
        card.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            card,
            text="💬 เข้าร่วมห้องแชท",
            font=(self.font_family, 18, "bold"),
            bg="#FFFFFF",
            fg="#1976D2",
        ).pack(pady=(0, 2))
        tk.Label(
            card,
            text="ระบบแชทกลุ่มผ่านเครือข่าย TCP Socket",
            font=(self.font_family, 9),
            bg="#FFFFFF",
            fg="#757575",
        ).pack(pady=(0, 20))

        def add_field(label_text, default_val=""):
            row = tk.Frame(card, bg="#FFFFFF")
            row.pack(fill="x", pady=5)
            tk.Label(
                row,
                text=label_text,
                font=(self.font_family, 10, "bold"),
                bg="#FFFFFF",
                width=12,
                anchor="w",
            ).pack(side="left")
            entry = tk.Entry(row, font=(self.font_family, 10), width=20)
            if default_val:
                entry.insert(0, default_val)
            entry.pack(side="left")
            return entry

        self.entry_ip = add_field("IP เซิร์ฟเวอร์:", "127.0.0.1")
        self.entry_port = add_field("Port:", "5000")
        self.entry_username = add_field("ชื่อผู้ใช้งาน:")
        self.entry_username.bind("<KeyRelease>", self.on_username_typed)
        self.entry_username.bind("<Return>", lambda _: self.connect_to_server())

        self.lbl_color_preview = tk.Label(
            card,
            text="● สีประจำตัวของคุณจะปรากฏที่นี่",
            font=(self.font_family, 9, "bold"),
            bg="#FFFFFF",
            fg="#757575",
        )
        self.lbl_color_preview.pack(pady=10)

        self.lbl_login_status = tk.Label(
            card, text="", font=(self.font_family, 9), bg="#FFFFFF", fg="#D32F2F"
        )
        self.lbl_login_status.pack(pady=(0, 10))

        self.btn_connect = tk.Button(
            card,
            text="🚀 เข้าสู่ห้องแชท (Connect)",
            font=(self.font_family, 11, "bold"),
            bg="#1976D2",
            fg="white",
            activebackground="#0D47A1",
            activeforeground="white",
            relief="flat",
            padx=20,
            pady=8,
            cursor="hand2",
            command=self.connect_to_server,
        )
        self.btn_connect.pack(fill="x")

    def on_username_typed(self, _event=None):
        name = self.entry_username.get().strip()
        if not name:
            self.lbl_color_preview.configure(
                text="● กรุณาพิมพ์ชื่อเพื่อดูสีประจำตัว", fg="#757575"
            )
            return
        self.lbl_color_preview.configure(
            text=f"● สีประจำตัวของคุณ: {name}", fg=get_user_color(name)
        )

    def show_login_view(self):
        self.chat_frame.pack_forget()
        self.login_frame.pack(fill="both", expand=True)
        self.entry_username.focus_set()

    # ---------------- 2. หน้าต่างห้องแชทหลัก (Chat View) ----------------

    def setup_chat_view(self):
        self.chat_frame = tk.Frame(self.container, bg="#F0F2F5")

        # Top Bar
        top_bar = tk.Frame(
            self.chat_frame, bg="#FFFFFF", padx=15, pady=10, bd=1, relief="solid"
        )
        top_bar.pack(fill="x", padx=15, pady=(15, 8))

        self.lbl_chat_info = tk.Label(
            top_bar,
            text="🟢 กำลังเชื่อมต่อ...",
            font=(self.font_family, 10, "bold"),
            bg="#FFFFFF",
            fg="#2E7D32",
        )
        self.lbl_chat_info.pack(side="left")

        self.lbl_my_name_badge = tk.Label(
            top_bar, text="", font=(self.font_family, 10, "bold"), bg="#FFFFFF"
        )
        self.lbl_my_name_badge.pack(side="left", padx=10)

        tk.Button(
            top_bar,
            text="🚪 ออกจากห้องแชท",
            font=(self.font_family, 9, "bold"),
            bg="#D32F2F",
            fg="white",
            activebackground="#B71C1C",
            activeforeground="white",
            relief="flat",
            padx=12,
            pady=4,
            cursor="hand2",
            command=self.disconnect_from_server,
        ).pack(side="right")

        # Body Frame
        body = tk.Frame(self.chat_frame, bg="#F0F2F5")
        body.pack(fill="both", expand=True, padx=15, pady=5)

        # ฝั่งซ้าย: กล่องข้อความแชท
        left_body = tk.Frame(body, bg="#FFFFFF", bd=1, relief="solid")
        left_body.pack(side="left", fill="both", expand=True, padx=(0, 8))

        self.chat_text = scrolledtext.ScrolledText(
            left_body,
            wrap="word",
            font=(self.font_family, 10),
            bg="#FFFFFF",
            fg="#212121",
            padx=12,
            pady=10,
            bd=0,
            state="disabled",
        )
        self.chat_text.pack(fill="both", expand=True)
        self.chat_text.tag_config(
            "tag_time", foreground="#888888", font=(self.font_family, 8)
        )
        self.chat_text.tag_config(
            "tag_msg", foreground="#212121", font=(self.font_family, 10)
        )
        self.chat_text.tag_config(
            "tag_system", foreground="#616161", font=(self.font_family, 9, "italic")
        )

        # ฝั่งขวา: รายชื่อผู้ใช้ออนไลน์
        right_body = tk.Frame(body, bg="#FFFFFF", bd=1, relief="solid", width=250)
        right_body.pack(side="right", fill="y", padx=(8, 0))
        right_body.pack_propagate(False)

        user_header = tk.Frame(right_body, bg="#FFFFFF", padx=10, pady=8)
        user_header.pack(fill="x")
        self.lbl_online_count = tk.Label(
            user_header,
            text="👥 สมาชิก (0)",
            font=(self.font_family, 10, "bold"),
            bg="#FFFFFF",
        )
        self.lbl_online_count.pack(side="left")

        self.users_display = tk.Text(
            right_body,
            font=(self.font_family, 10),
            bg="#FAFAFA",
            fg="#212121",
            padx=10,
            pady=8,
            bd=0,
            state="disabled",
            cursor="arrow",
            wrap="none",
        )
        self.users_display.pack(fill="both", expand=True)
        self.users_display.tag_config(
            "me_text", font=(self.font_family, 10, "bold"), foreground="#1976D2"
        )
        self.users_display.tag_config(
            "other_text", font=(self.font_family, 10, "bold"), foreground="#212121"
        )
        self.users_display.tag_config(
            "host_text", font=(self.font_family, 10, "bold"), foreground="#1976D2"
        )
        self.users_display.tag_config(
            "ip_text", font=(self.font_family, 9), foreground="#616161"
        )

        # Bottom Bar: แถบส่งข้อความ
        bottom_bar = tk.Frame(
            self.chat_frame, bg="#FFFFFF", padx=12, pady=10, bd=1, relief="solid"
        )
        bottom_bar.pack(fill="x", padx=15, pady=(8, 15))

        self.btn_emoji = tk.Button(
            bottom_bar,
            text="😀 อีโมจิ",
            font=(self.font_family, 9, "bold"),
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
            bottom_bar,
            text="🏷️ สติ๊กเกอร์",
            font=(self.font_family, 9, "bold"),
            bg="#E8F5E9",
            fg="#2E7D32",
            activebackground="#C8E6C9",
            relief="flat",
            padx=10,
            pady=5,
            cursor="hand2",
            command=self.toggle_sticker_picker,
        )
        self.btn_sticker.pack(side="left", padx=(0, 10))

        self.entry_msg = tk.Entry(
            bottom_bar, font=(self.font_family, 11), bg="#F8F9FA", bd=1, relief="solid"
        )
        self.entry_msg.pack(side="left", fill="x", expand=True, padx=(0, 8), ipady=4)
        self.entry_msg.bind("<Return>", lambda _: self.send_chat_message())

        tk.Button(
            bottom_bar,
            text="ส่ง (Send) ✈️",
            font=(self.font_family, 10, "bold"),
            bg="#1976D2",
            fg="white",
            activebackground="#0D47A1",
            activeforeground="white",
            relief="flat",
            padx=15,
            pady=5,
            cursor="hand2",
            command=self.send_chat_message,
        ).pack(side="right")

    def show_chat_view(self):
        self.login_frame.pack_forget()
        self.chat_frame.pack(fill="both", expand=True)
        self.entry_msg.focus_set()

    # ---------------- 3. การเชื่อมต่อและ Network Logic ----------------

    def connect_to_server(self):
        ip = self.entry_ip.get().strip()
        port_str = self.entry_port.get().strip()
        username = self.entry_username.get().strip()

        if not ip or not port_str or not username:
            self.lbl_login_status.configure(text="กรุณากรอกข้อมูลให้ครบถ้วนทุกช่อง")
            return

        if not port_str.isdigit():
            self.lbl_login_status.configure(text="Port ต้องเป็นตัวเลขเท่านั้น")
            return

        self.lbl_login_status.configure(
            text="กำลังเชื่อมต่อไปยังเซิร์ฟเวอร์...", fg="#1976D2"
        )
        self.btn_connect.configure(state="disabled")
        threading.Thread(
            target=self._async_connect, args=(ip, int(port_str), username), daemon=True
        ).start()

    def _async_connect(self, ip: str, port: int, username: str):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(6.0)
            sock.connect((ip, port))
            sock.settimeout(None)

            sock.sendall(
                (
                    json.dumps(
                        {"type": "join", "username": username}, ensure_ascii=False
                    )
                    + "\n"
                ).encode("utf-8")
            )

            f = sock.makefile("r", encoding="utf-8")
            resp_line = f.readline()
            if not resp_line:
                raise ConnectionResetError("เซิร์ฟเวอร์ตัดการเชื่อมต่อก่อนตอบกลับ")

            resp_data = json.loads(resp_line.strip())
            if not resp_data.get("success"):
                sock.close()
                self.root.after(
                    0,
                    self._on_connect_failed,
                    resp_data.get("message", "ไม่สามารถเข้าร่วมห้องแชทได้"),
                )
                return

            self.client_socket = sock
            self.file_reader = f
            self.is_connected = True
            self.my_username = username
            self.my_color = resp_data.get("color", get_user_color(username))

            self.root.after(0, self._on_connect_success, ip, port)
            threading.Thread(target=self.receive_loop, daemon=True).start()

        except Exception as err:
            self.root.after(0, self._on_connect_failed, str(err))

    def _on_connect_failed(self, error_message: str):
        self.btn_connect.configure(state="normal")
        self.lbl_login_status.configure(
            text=f"เชื่อมต่อไม่สำเร็จ: {error_message}", fg="#D32F2F"
        )

    def _on_connect_success(self, ip: str, port: int):
        self.btn_connect.configure(state="normal")
        self.lbl_login_status.configure(text="")
        self.lbl_chat_info.configure(text=f"🟢 เชื่อมต่อกับ {ip}:{port}")
        self.lbl_my_name_badge.configure(
            text=f"คุณ: {self.my_username}", fg=self.my_color
        )

        self.chat_text.configure(state="normal")
        self.chat_text.delete("1.0", "end")
        self.chat_text.configure(state="disabled")

        self.append_system_message(
            f"🎉 คุณได้เข้าร่วมห้องแชทในชื่อ '{self.my_username}'"
        )
        self.show_chat_view()

    def disconnect_from_server(self):
        if not self.is_connected:
            self.show_login_view()
            return

        self.is_connected = False
        try:
            if self.client_socket:
                self.client_socket.sendall(
                    (json.dumps({"type": "leave"}, ensure_ascii=False) + "\n").encode(
                        "utf-8"
                    )
                )
                self.client_socket.close()
        except Exception:
            pass

        self.client_socket = None
        self.file_reader = None
        self.show_login_view()
        self.lbl_login_status.configure(text="ออกจากห้องแชทแล้ว", fg="#757575")

    def receive_loop(self):
        while self.is_connected and self.file_reader:
            try:
                line = self.file_reader.readline()
                if not line:
                    break
                self.root.after(
                    0, self.handle_incoming_packet, json.loads(line.strip())
                )
            except Exception:
                break

        if self.is_connected:
            self.root.after(0, self.handle_server_lost)

    def handle_server_lost(self):
        if self.is_connected:
            self.is_connected = False
            messagebox.showwarning(
                "หลุดจากการเชื่อมต่อ", "ขาดการเชื่อมต่อจากเซิร์ฟเวอร์"
            )
            self.disconnect_from_server()

    def handle_incoming_packet(self, packet: dict):
        p_type = packet.get("type")
        sender = packet.get("sender", "นิรนาม")
        color = packet.get("color", get_user_color(sender))

        if p_type == "chat":
            self.append_chat_message(
                sender, color, packet.get("content", ""), packet.get("time", "")
            )
        elif p_type == "sticker":
            self.append_sticker_message(
                sender,
                color,
                packet.get("emoji", ""),
                packet.get("title", ""),
                packet.get("time", ""),
            )
        elif p_type == "system":
            self.append_system_message(packet.get("content", ""))
        elif p_type == "user_list":
            self.update_user_list_display(packet.get("users", []))
        elif p_type == "kicked":
            messagebox.showerror(
                "ถูกตัดการเชื่อมต่อ", packet.get("reason", "ถูกเตะออกจากห้อง")
            )
            self.disconnect_from_server()

    # ---------------- 4. การแสดงผลข้อความในห้องแชท (UI Rendering) ----------------

    def _write_chat(self, fn):
        self.chat_text.configure(state="normal")
        fn()
        self.chat_text.configure(state="disabled")
        self.chat_text.see("end")

    def _insert_header(self, sender: str, color: str, time_str: str, suffix=": "):
        self.chat_text.insert("end", f"[{time_str}] ", "tag_time")
        is_me = sender == self.my_username
        tag_name = f"u_{sender}_{abs(hash(color))}"
        self.chat_text.tag_config(
            tag_name, foreground=color, font=(self.font_family, 10, "bold")
        )
        self.chat_text.insert(
            "end", f"{sender} (คุณ){suffix}" if is_me else f"{sender}{suffix}", tag_name
        )

    def append_chat_message(self, sender: str, color: str, content: str, time_str: str):
        def _insert():
            self._insert_header(sender, color, time_str)
            self.chat_text.insert("end", f"{content}\n", "tag_msg")

        self._write_chat(_insert)

    def append_sticker_message(
        self, sender: str, color: str, emoji: str, title: str, time_str: str
    ):
        def _insert():
            self._insert_header(sender, color, time_str, suffix=" ส่งสติ๊กเกอร์:\n")
            card = tk.Frame(
                self.chat_text, bg="#F5F6F8", bd=1, relief="solid", padx=16, pady=8
            )
            tk.Label(card, text=emoji, font=("Segoe UI Emoji", 30), bg="#F5F6F8").pack()
            tk.Label(
                card,
                text=f" {title} ",
                font=(self.font_family, 9, "bold"),
                bg="#E0E0E0",
                fg="#333333",
                padx=8,
                pady=2,
            ).pack(pady=(2, 0))
            self.chat_text.insert("end", "  ")
            self.chat_text.window_create("end", window=card)
            self.chat_text.insert("end", "\n\n")

        self._write_chat(_insert)

    def append_system_message(self, content: str):
        self._write_chat(
            lambda: self.chat_text.insert("end", f"── {content} ──\n", "tag_system")
        )

    def update_user_list_display(self, users: list):
        self.users_display.configure(state="normal")
        self.users_display.delete("1.0", "end")
        self.lbl_online_count.configure(text=f"👥 สมาชิก ({len(users)})")

        for u in users:
            name = u.get("username", "")
            color = u.get("color", get_user_color(name))
            tag_name = f"dot_{name}_{abs(hash(color))}"
            self.users_display.tag_config(
                tag_name, foreground=color, font=(self.font_family, 11, "bold")
            )
            self.users_display.insert("end", " ● ", tag_name)

            is_me = name == self.my_username
            is_host = u.get("is_host", False) or name == "Server"
            addr_str = u.get("addr_str", "")
            if not addr_str and u.get("ip"):
                addr_str = f"{u['ip']}:{u.get('port', '')}"

            if is_me:
                self.users_display.insert("end", f"{name} (คุณ)", "me_text")
            elif is_host:
                self.users_display.insert("end", f"{name}", "host_text")
            else:
                self.users_display.insert("end", f"{name}", "other_text")

            # แสดง IP / สถานะโฮสต์ เหมือนกับฝั่ง Server
            if is_host:
                self.users_display.insert("end", " (โฮสต์)\n", "ip_text")
            elif addr_str:
                self.users_display.insert("end", f" ({addr_str})\n", "ip_text")
            else:
                self.users_display.insert("end", "\n")

        self.users_display.configure(state="disabled")

    # ---------------- 5. การส่งข้อความและสติ๊กเกอร์ ----------------

    def send_chat_message(self):
        if not self.is_connected:
            return
        msg = self.entry_msg.get().strip()
        if not msg:
            return
        self.entry_msg.delete(0, "end")
        self.send_packet_to_server({"type": "chat", "content": msg})

    def send_sticker(self, emoji: str, title: str):
        if self.is_connected:
            self.send_packet_to_server(
                {"type": "sticker", "emoji": emoji, "title": title}
            )

    def send_packet_to_server(self, packet: dict):
        if not self.client_socket:
            return
        try:
            raw = (json.dumps(packet, ensure_ascii=False) + "\n").encode("utf-8")
            self.client_socket.sendall(raw)
        except Exception as err:
            messagebox.showerror("เกิดข้อผิดพลาด", f"ไม่สามารถส่งข้อความได้:\n{err}")

    # ---------------- 6. Emoji Picker และ Sticker Picker ----------------

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
        p = self._create_popup(self.btn_emoji, "เลือกอีโมจิ (Emoji)", 360, 280, 300)
        tk.Label(
            p,
            text="แตะอีโมจิเพื่อพิมพ์ลงในข้อความ",
            font=(self.font_family, 9, "bold"),
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
        p = self._create_popup(
            self.btn_sticker, "เลือกสติ๊กเกอร์ (Stickers)", 420, 340, 360
        )
        tk.Label(
            p,
            text="แตะสติ๊กเกอร์เพื่อส่งทันที",
            font=(self.font_family, 10, "bold"),
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

    def on_closing(self):
        if self.is_connected:
            self.disconnect_from_server()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    ChatClientGUI(root)
    root.mainloop()
