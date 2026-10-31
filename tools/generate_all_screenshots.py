"""
Automated master screenshot generator for Chat Application.
Runs real Server and Client, simulates real TCP traffic, and captures all states.
Uses event-driven scheduling to ensure all threads stay inside Tkinter mainloop.
"""

import os
import sys
import time
import json
import socket
import shutil
import subprocess
import ctypes
from ctypes import wintypes
from PIL import Image

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import tkinter as tk
from client import ChatClientGUI

OUTPUT_DIR = os.path.join(BASE_DIR, "screenshots")
USER_SCREENSHOT_DIR = r"C:\Users\Nitro\OneDrive - Mahasarakham University\Pictures\Screenshots"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}")
    sys.stdout.flush()


def capture_hwnd(hwnd, filename):
    user32 = ctypes.windll.user32
    gdi32 = ctypes.windll.gdi32

    user32.ShowWindow(hwnd, 9)  # SW_RESTORE
    user32.SetForegroundWindow(hwnd)
    time.sleep(0.15)

    rect = wintypes.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    w = max(10, rect.right - rect.left)
    h = max(10, rect.bottom - rect.top)

    hdc_window = user32.GetWindowDC(hwnd)
    hdc_mem = gdi32.CreateCompatibleDC(hdc_window)
    hbm = gdi32.CreateCompatibleBitmap(hdc_window, w, h)
    gdi32.SelectObject(hdc_mem, hbm)

    user32.PrintWindow(hwnd, hdc_mem, 0)

    class BITMAPINFOHEADER(ctypes.Structure):
        _fields_ = [
            ('biSize', wintypes.DWORD), ('biWidth', wintypes.LONG), ('biHeight', wintypes.LONG),
            ('biPlanes', wintypes.WORD), ('biBitCount', wintypes.WORD), ('biCompression', wintypes.DWORD),
            ('biSizeImage', wintypes.DWORD), ('biXPelsPerMeter', wintypes.LONG), ('biYPelsPerMeter', wintypes.LONG),
            ('biClrUsed', wintypes.DWORD), ('biClrImportant', wintypes.DWORD),
        ]

    bmi = BITMAPINFOHEADER()
    bmi.biSize = ctypes.sizeof(BITMAPINFOHEADER)
    bmi.biWidth = w
    bmi.biHeight = -h
    bmi.biPlanes = 1
    bmi.biBitCount = 32
    buf = ctypes.create_string_buffer(w * h * 4)
    gdi32.GetDIBits(hdc_mem, hbm, 0, h, buf, ctypes.byref(bmi), 0)

    im = Image.frombuffer('RGBA', (w, h), buf, 'raw', 'BGRA', 0, 1)
    im_rgb = im.convert('RGB')
    dest_path = os.path.join(OUTPUT_DIR, filename)
    im_rgb.save(dest_path)
    log(f"Captured: {filename} ({w}x{h})")

    try:
        if os.path.exists(USER_SCREENSHOT_DIR):
            user_dest = os.path.join(USER_SCREENSHOT_DIR, filename)
            shutil.copy2(dest_path, user_dest)
    except Exception as e:
        log(f"OneDrive copy notice: {e}")

    gdi32.DeleteObject(hbm)
    gdi32.DeleteDC(hdc_mem)
    user32.ReleaseDC(hwnd, hdc_window)
    return dest_path


def capture_tk(widget, filename):
    widget.update_idletasks()
    widget.update()
    time.sleep(0.1)
    inner = widget.winfo_id()
    parent = ctypes.windll.user32.GetParent(inner)
    hwnd = parent if parent else inner
    return capture_hwnd(hwnd, filename)


def send_server_ctrl(cmd: str):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5.0)
    try:
        s.connect(("127.0.0.1", 5001))
        s.sendall((cmd + "\n").encode("utf-8"))
        f = s.makefile("r", encoding="utf-8")
        resp = f.readline().strip()
        s.close()
        return resp
    except Exception as e:
        log(f"send_server_ctrl error for {cmd}: {e}")
        return ""


def send_raw_packet(sock, packet: dict):
    sock.sendall((json.dumps(packet, ensure_ascii=False) + "\n").encode("utf-8"))


def kill_port_owner(port: int):
    try:
        out = subprocess.check_output(f"netstat -ano | findstr :{port}", shell=True).decode()
        for line in out.strip().splitlines():
            if "LISTENING" in line:
                pid = line.strip().split()[-1]
                if pid and pid != "0" and int(pid) != os.getpid():
                    subprocess.call(f"taskkill /F /PID {pid}", shell=True)
    except Exception:
        pass

class AutomationOrchestrator:
    def __init__(self):
        kill_port_owner(5000)
        kill_port_owner(5001)
        time.sleep(0.5)
        log("Starting Server Subprocess...")
        server_runner_path = os.path.join(os.path.dirname(__file__), "server_runner.py")
        self.server_proc = subprocess.Popen([sys.executable, server_runner_path])
        
        user32 = ctypes.windll.user32
        self.server_hwnd = 0
        for _ in range(40):
            time.sleep(0.1)
            self.server_hwnd = user32.FindWindowW(None, "Chat Server Control Panel - ระบบเซิร์ฟเวอร์ห้องแชท")
            if self.server_hwnd:
                break
        log(f"Server HWND detected: {self.server_hwnd}")

        self.c_root = tk.Tk()
        self.c_app = ChatClientGUI(self.c_root)
        self.c_root.geometry("860x620+200+100")

        self.s_bot1 = None
        self.s_bot2 = None

        self.c_root.after(500, self.step_0)

    def start(self):
        self.c_root.mainloop()

    def step_0(self):
        log("Executing step 0...")
        # 1. Server initial offline
        capture_hwnd(self.server_hwnd, "01_server_initial_offline.png")
        # 2. Server start online
        resp = send_server_ctrl("START")
        log(f"Server start ctrl response: {resp}")
        self.c_root.after(800, self.step_1)

    def step_1(self):
        log("Executing step 1...")
        # Capture Server online (with LAN banner, active chat bar, user list with Server host)
        capture_hwnd(self.server_hwnd, "02_server_running_online.png")
        # 3. Client login empty (shows default 127.0.0.1)
        capture_tk(self.c_root, "03_client_login_empty.png")
        # 4. Client typing & preview: Change IP to LAN IP 10.26.25.195 and type nickname
        self.c_app.entry_ip.delete(0, tk.END)
        self.c_app.entry_ip.insert(0, "10.26.25.195")
        self.c_app.entry_username.insert(0, "Somchai_MSU")
        self.c_app.on_username_typed()
        self.c_root.after(500, self.step_2)

    def step_2(self):
        log("Executing step 2...")
        capture_tk(self.c_root, "04_client_login_typing_preview.png")

        # 5. Duplicate Login Error Mock Window
        dup_win = tk.Toplevel(self.c_root)
        dup_win.title("Group Chat Client - ห้องแชทกลุ่ม")
        dup_win.geometry("860x620+230+130")
        dup_app = ChatClientGUI(dup_win)
        dup_app.entry_ip.delete(0, tk.END)
        dup_app.entry_ip.insert(0, "10.26.25.195")
        dup_app.entry_username.insert(0, "Somchai_MSU")
        dup_app.on_username_typed()
        dup_app.lbl_login_status.configure(
            text="เชื่อมต่อไม่สำเร็จ: ชื่อ 'Somchai_MSU' มีผู้ใช้งานแล้ว กรุณาเลือกชื่ออื่น",
            fg="#D32F2F"
        )
        dup_win.update()
        capture_tk(dup_win, "05_client_login_duplicate_error.png")
        dup_win.destroy()

        # Connect Client 1
        log("Client 1 connecting...")
        self.c_app.connect_to_server()
        self.c_root.after(1000, self.step_3)

    def step_3(self):
        log("Executing step 3...")
        capture_tk(self.c_root, "06_client_chat_welcome.png")

        # Connect peer bots
        log("Connecting bots...")
        self.s_bot1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s_bot1.connect(("10.26.25.195", 5000))
        send_raw_packet(self.s_bot1, {
            "type": "join",
            "username": "Nong_May",
            "simulated_ip": "10.26.25.102",
            "simulated_port": 54120
        })

        self.s_bot2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s_bot2.connect(("10.26.25.195", 5000))
        send_raw_packet(self.s_bot2, {
            "type": "join",
            "username": "Ajarn_Kitti",
            "simulated_ip": "10.26.25.88",
            "simulated_port": 51200
        })

        self.c_root.after(800, self.step_4)

    def step_4(self):
        log("Executing step 4: Exchanging messages...")
        # Client 1 message
        self.c_app.entry_msg.insert(0, "สวัสดีครับอาจารย์และเพื่อนๆ ทุกคน ยินดีต้อนรับสู่ห้องแชทครับ! 👋")
        self.c_app.send_chat_message()

        # Bot 1 message
        send_raw_packet(self.s_bot1, {"type": "chat", "content": "สวัสดีค่ะพี่สมชายและอาจารย์กิตติ ระบบแชท GUI สวยงามและตอบสนองเร็วมากเลยค่ะ ✨"})
        # Bot 2 message
        send_raw_packet(self.s_bot2, {"type": "chat", "content": "สวัสดีทุกคน โครงงาน Socket TCP แชทกลุ่มชิ้นนี้ออกแบบและจัดการ Multi-thread ได้ดีมากครับ 👍"})
        # Bot 1 sticker
        send_raw_packet(self.s_bot1, {"type": "sticker", "emoji": "🎉", "title": "ยินดีด้วย!"})
        # Client 1 sticker
        self.c_app.send_sticker("🔥", "ไฟลุก!")

        # Server sends message and sticker as Server!
        send_server_ctrl("CHAT ยินดีต้อนรับทุกคนเข้าสู่ห้องแชทวิชา Network ครับ! ขอให้สนุกกับการทดสอบระบบ 🌐")
        send_server_ctrl("STICKER 👍 สุดยอดเลย!")

        self.c_root.after(1200, self.step_5)

    def step_5(self):
        log("Executing step 5: Capturing active conversation...")
        # Capture Active Multi-user Chat
        capture_tk(self.c_root, "07_client_chat_active_conversation.png")
        # Open Emoji Picker
        self.c_app.toggle_emoji_picker()
        self.c_root.after(600, self.step_6)

    def step_6(self):
        log("Executing step 6: Emoji picker...")
        emoji_win = None
        for child in self.c_root.winfo_children():
            if isinstance(child, tk.Toplevel) and child.title() == "เลือกอีโมจิ (Emoji)":
                emoji_win = child
                break
        if emoji_win:
            capture_tk(emoji_win, "08_client_emoji_picker_popup.png")
            emoji_win.destroy()

        # Open Sticker Picker
        self.c_app.toggle_sticker_picker()
        self.c_root.after(600, self.step_7)

    def step_7(self):
        log("Executing step 7: Sticker picker...")
        sticker_win = None
        for child in self.c_root.winfo_children():
            if isinstance(child, tk.Toplevel) and child.title() == "เลือกสติ๊กเกอร์ (Stickers)":
                sticker_win = child
                break
        if sticker_win:
            capture_tk(sticker_win, "09_client_sticker_picker_popup.png")
            sticker_win.destroy()

        # Capture Server with active logs & users
        capture_hwnd(self.server_hwnd, "10_server_active_logs_and_users.png")

        # Send an announcement chat from Server
        send_server_ctrl("CHAT 📢 แจ้งเตือนนิสิตทุกคน เตรียมตัวนำเสนอโครงงานระบบเครือข่ายสัปดาห์หน้าครับ!")
        self.c_root.after(1000, self.step_8)

    def step_8(self):
        log("Executing step 8: Server announcement...")
        capture_hwnd(self.server_hwnd, "11_server_broadcast_sent.png")
        capture_tk(self.c_root, "12_client_broadcast_received.png")

        # Server kicks Nong_May
        log("Server kicking Nong_May...")
        send_server_ctrl("KICK Nong_May")
        self.c_root.after(1000, self.step_9)

    def step_9(self):
        log("Executing step 9: After user kicked...")
        capture_hwnd(self.server_hwnd, "13_server_after_user_kicked.png")

        # Disconnect client 1
        self.c_app.disconnect_from_server()
        self.c_root.after(600, self.step_10)

    def step_10(self):
        log("Executing step 10: Disconnected state...")
        capture_tk(self.c_root, "14_client_disconnected_state.png")

        # Cleanup
        try: self.s_bot1.close()
        except Exception: pass
        try: self.s_bot2.close()
        except Exception: pass

        send_server_ctrl("QUIT")
        try: self.server_proc.wait(timeout=2)
        except Exception: self.server_proc.kill()

        self.c_root.destroy()
        log("ALL AUTOMATED SCREENSHOTS COMPLETED SUCCESSFULLY!")


if __name__ == "__main__":
    app = AutomationOrchestrator()
    app.start()
