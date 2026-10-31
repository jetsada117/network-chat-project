"""
Script to generate the complete updated User Manual presentation (.pptx)
for the Python TCP Socket Multi-Client Chat Application.
Includes high-resolution real screenshots, structured layouts, diagrams,
and comprehensive technical and user guides.
"""

import os
import shutil
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCREENSHOT_DIR = os.path.join(BASE_DIR, "screenshots")
OUTPUT_PPTX_ENG = os.path.join(BASE_DIR, "Chat_Application_Manual.pptx")
OUTPUT_PPTX_THAI = os.path.join(BASE_DIR, "คู่มือการใช้งาน_ระบบแชท_TCP_Socket.pptx")

# Color Palette
C_DARK_BG   = RGBColor(15, 23, 42)     # Slate 900
C_DARK_CARD = RGBColor(30, 41, 59)     # Slate 800
C_PRIMARY   = RGBColor(25, 118, 210)   # Blue 700
C_SECONDARY = RGBColor(2, 132, 199)    # Sky 600
C_ACCENT    = RGBColor(16, 185, 129)   # Emerald 500
C_AMBER     = RGBColor(245, 158, 11)   # Amber 500
C_RED       = RGBColor(220, 38, 38)    # Red 600
C_LIGHT_BG  = RGBColor(248, 250, 252)  # Slate 50
C_CARD_BG   = RGBColor(255, 255, 255)  # White
C_BORDER    = RGBColor(226, 232, 240)  # Slate 200
C_BORDER_HI = RGBColor(148, 163, 184)  # Slate 400
C_TEXT_DARK = RGBColor(15, 23, 42)     # Slate 900
C_TEXT_MUTED= RGBColor(100, 116, 139)  # Slate 500
C_TEXT_LIGHT= RGBColor(241, 245, 249)  # Slate 100

FONT_HEADING = "Segoe UI"
FONT_BODY    = "Segoe UI"


def create_base_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    return prs


def add_header(slide, badge_text, title_text, subtitle_text=""):
    """Adds a standard elegant header banner to a light-themed content slide."""
    # Top Accent Line
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.08))
    line.fill.solid()
    line.fill.fore_color.rgb = C_PRIMARY
    line.line.fill.background()

    # Category Badge
    badge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.35), Inches(2.2), Inches(0.32))
    badge.fill.solid()
    badge.fill.fore_color.rgb = RGBColor(224, 242, 254)  # Sky 100
    badge.line.color.rgb = C_SECONDARY
    badge.line.width = Pt(1)
    tf_b = badge.text_frame
    tf_b.margin_top = Inches(0.02)
    tf_b.margin_bottom = Inches(0.02)
    p_b = tf_b.paragraphs[0]
    p_b.text = badge_text.upper()
    p_b.alignment = PP_ALIGN.CENTER
    p_b.font.name = FONT_HEADING
    p_b.font.size = Pt(10)
    p_b.font.bold = True
    p_b.font.color.rgb = C_PRIMARY

    # Title & Subtitle text box
    tb = slide.shapes.add_textbox(Inches(0.8), Inches(0.72), Inches(11.7), Inches(0.85))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

    p_t = tf.paragraphs[0]
    p_t.text = title_text
    p_t.font.name = FONT_HEADING
    p_t.font.size = Pt(22)
    p_t.font.bold = True
    p_t.font.color.rgb = C_TEXT_DARK

    if subtitle_text:
        p_s = tf.add_paragraph()
        p_s.text = subtitle_text
        p_s.font.name = FONT_BODY
        p_s.font.size = Pt(12)
        p_s.font.color.rgb = C_TEXT_MUTED
        p_s.space_before = Pt(3)


def add_image_card(slide, img_name, left, top, width, height, caption=""):
    """Adds a framed screenshot with clean shadow/border styling."""
    img_path = os.path.join(SCREENSHOT_DIR, img_name)
    if not os.path.exists(img_path):
        print(f"Warning: image {img_name} not found!")
        return

    # Background card frame
    frame = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        left - Inches(0.08),
        top - Inches(0.08),
        width + Inches(0.16),
        height + (Inches(0.45) if caption else Inches(0.16))
    )
    frame.fill.solid()
    frame.fill.fore_color.rgb = C_CARD_BG
    frame.line.color.rgb = C_BORDER_HI
    frame.line.width = Pt(1)

    # Insert Picture
    slide.shapes.add_picture(img_path, left, top, width=width, height=height)

    # Caption if provided
    if caption:
        tb = slide.shapes.add_textbox(left, top + height + Inches(0.04), width, Inches(0.35))
        tf = tb.text_frame
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        p = tf.paragraphs[0]
        p.text = caption
        p.alignment = PP_ALIGN.CENTER
        p.font.name = FONT_BODY
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = C_TEXT_MUTED


# ==========================================================
# SLIDE BUILDERS
# ==========================================================

def build_slide_01_cover(prs):
    """Slide 1: Cover Page"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    # Dark background
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg.fill.solid()
    bg.fill.fore_color.rgb = C_DARK_BG
    bg.line.fill.background()

    # Top Accent bar
    top_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(0.12))
    top_bar.fill.solid()
    top_bar.fill.fore_color.rgb = C_SECONDARY
    top_bar.line.fill.background()

    # Left decorative bar
    dec = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.5), Inches(0.12), Inches(3.2))
    dec.fill.solid()
    dec.fill.fore_color.rgb = C_PRIMARY
    dec.line.fill.background()

    # Title & Subtitle
    tb = slide.shapes.add_textbox(Inches(1.2), Inches(1.4), Inches(11.0), Inches(3.5))
    tf = tb.text_frame
    tf.word_wrap = True

    p0 = tf.paragraphs[0]
    p0.text = "คู่มือและโครงสร้างการใช้งานระบบห้องแชทกลุ่มผ่านเครือข่าย"
    p0.font.name = FONT_HEADING
    p0.font.size = Pt(32)
    p0.font.bold = True
    p0.font.color.rgb = RGBColor(255, 255, 255)

    p1 = tf.add_paragraph()
    p1.text = "Multi-Client Group Chat System with TCP Socket, Multithreading & Tkinter GUI"
    p1.font.name = FONT_HEADING
    p1.font.size = Pt(18)
    p1.font.color.rgb = RGBColor(56, 189, 248) # Sky 400
    p1.space_before = Pt(10)

    p2 = tf.add_paragraph()
    p2.text = "คู่มือการติดตั้ง ใช้งาน และอธิบายการทำงานของระบบฝั่งเซิร์ฟเวอร์ (Server) และลูกข่าย (Client) ฉบับสมบูรณ์"
    p2.font.name = FONT_BODY
    p2.font.size = Pt(13)
    p2.font.color.rgb = RGBColor(148, 163, 184)
    p2.space_before = Pt(8)

    # Info Footer Card
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.2), Inches(5.0), Inches(10.9), Inches(1.6))
    card.fill.solid()
    card.fill.fore_color.rgb = C_DARK_CARD
    card.line.color.rgb = RGBColor(51, 65, 85)
    card.line.width = Pt(1)

    tf_c = card.text_frame
    tf_c.margin_left = Inches(0.4)
    tf_c.margin_top = Inches(0.25)

    pc1 = tf_c.paragraphs[0]
    r1 = pc1.add_run()
    r1.text = "📚 วิชา: "
    r1.font.bold = True
    r1.font.color.rgb = RGBColor(56, 189, 248)
    r2 = pc1.add_run()
    r2.text = "Computer Networks (เครือข่ายคอมพิวเตอร์) ภาคเรียนที่ 1/2569\n"
    r2.font.color.rgb = C_TEXT_LIGHT

    pc2 = tf_c.add_paragraph()
    r3 = pc2.add_run()
    r3.text = "🏛️ สถาบัน: "
    r3.font.bold = True
    r3.font.color.rgb = RGBColor(52, 211, 153)
    r4 = pc2.add_run()
    r4.text = "มหาวิทยาลัยมหาสารคาม (Mahasarakham University)\n"
    r4.font.color.rgb = C_TEXT_LIGHT

    pc3 = tf_c.add_paragraph()
    r5 = pc3.add_run()
    r5.text = "⚙️ จุดเด่นทางเทคนิค: "
    r5.font.bold = True
    r5.font.color.rgb = RGBColor(251, 191, 36)
    r6 = pc3.add_run()
    r6.text = "Python Standard Library 100% (ไม่ต้องติดตั้งแพ็กเกจเพิ่ม), TCP Socket, Multithreading, JSON, Tkinter"
    r6.font.color.rgb = C_TEXT_LIGHT


def build_slide_02_agenda(prs):
    """Slide 2: Table of Contents / Agenda"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_header(slide, "สารบัญ", "โครงสร้างเนื้อหาคู่มือการใช้งาน (Table of Contents)", "ภาพรวมการนำเสนอและหัวข้อคู่มือระบบห้องแชทกลุ่ม")

    sections = [
        ("01", "ภาพรวมและสถาปัตยกรรมระบบ", "System Architecture & Protocol", "สถาปัตยกรรม Client-Server, โครงสร้างโปรโตคอล JSON, การจัดการเธรด (Multithreading)", C_PRIMARY),
        ("02", "คู่มือการใช้งานฝั่งเซิร์ฟเวอร์", "Server Control Panel Manual", "การเปิดใช้งานเซิร์ฟเวอร์, แบนเนอร์ LAN IP, บันทึกเหตุการณ์ (Logs), การแชทในชื่อ Server และการเตะผู้ใช้", C_SECONDARY),
        ("03", "คู่มือการใช้งานฝั่งผู้ใช้", "Client Application Manual", "การเข้าสู่ห้องแชท, ระบบสีประจำตัว (Hash Avatar), การดู IP สมาชิก, การส่งข้อความ, สติ๊กเกอร์ และอีโมจิ", C_ACCENT),
        ("04", "การจัดการข้อผิดพลาดและ FAQ", "Troubleshooting & Best Practices", "การแก้ปัญหาการเชื่อมต่อ, การตรวจสอบชื่อซ้ำ, การตัดการเชื่อมต่อ และแนวทางพัฒนาต่อ", C_AMBER),
    ]

    left_base = Inches(0.8)
    col_w = Inches(2.7)
    gap = Inches(0.3)
    top = Inches(2.0)
    card_h = Inches(4.7)

    for i, (num, title_th, title_en, desc, col) in enumerate(sections):
        x = left_base + i * (col_w + gap)

        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, top, col_w, card_h)
        card.fill.solid()
        card.fill.fore_color.rgb = C_CARD_BG
        card.line.color.rgb = C_BORDER
        card.line.width = Pt(1.5)

        # Color Accent Top
        bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, top, col_w, Inches(0.12))
        bar.fill.solid()
        bar.fill.fore_color.rgb = col
        bar.line.fill.background()

        # Text Frame
        tb = slide.shapes.add_textbox(x + Inches(0.2), top + Inches(0.3), col_w - Inches(0.4), card_h - Inches(0.5))
        tf = tb.text_frame
        tf.word_wrap = True

        p_num = tf.paragraphs[0]
        p_num.text = num
        p_num.font.name = FONT_HEADING
        p_num.font.size = Pt(36)
        p_num.font.bold = True
        p_num.font.color.rgb = col

        p_th = tf.add_paragraph()
        p_th.text = title_th
        p_th.font.name = FONT_HEADING
        p_th.font.size = Pt(15)
        p_th.font.bold = True
        p_th.font.color.rgb = C_TEXT_DARK
        p_th.space_before = Pt(8)

        p_en = tf.add_paragraph()
        p_en.text = title_en
        p_en.font.name = FONT_BODY
        p_en.font.size = Pt(10)
        p_en.font.bold = True
        p_en.font.color.rgb = col
        p_en.space_before = Pt(2)

        p_desc = tf.add_paragraph()
        p_desc.text = desc
        p_desc.font.name = FONT_BODY
        p_desc.font.size = Pt(11)
        p_desc.font.color.rgb = C_TEXT_MUTED
        p_desc.space_before = Pt(12)


def build_slide_03_architecture(prs):
    """Slide 3: System Architecture"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_header(slide, "สถาปัตยกรรมระบบ", "สถาปัตยกรรมเครือข่ายและการทำงานของระบบ (Architecture Overview)", "โครงสร้างการเชื่อมต่อระหว่างเซิร์ฟเวอร์และไคลเอนต์ผ่าน TCP Socket")

    nodes = [
        ("🖥️ Client Application", "client.py (Tkinter GUI)", [
            "• GUI Main Thread: ควบคุมการแสดงผลและรับ Event จากผู้ใช้",
            "• Async Receiver Thread: เธรดเบื้องหลังรอรับข้อมูลจาก Server แบบ Real-time",
            "• Deterministic Hash: สุ่มสีประจำตัวผู้ใช้อัตโนมัติด้วย MD5",
            "• Dynamic Rich Content: เรนเดอร์การ์ดสติ๊กเกอร์, อีโมจิ และแสดง IP สมาชิก",
        ], Inches(0.8), Inches(1.9), Inches(3.6), Inches(4.8), C_PRIMARY),

        ("🌐 Network Layer", "TCP/IP Protocol (Port 5000)", [
            "• Reliable Connection: ใช้โปรโตคอล TCP แบบ Stream ป้องกันข้อมูลสูญหาย",
            "• Framing: แยกแพ็กเก็ตข้อความด้วย Newline Delimiter (\\n)",
            "• Payload: เข้ารหัสข้อมูลด้วย JSON Format (UTF-8) รองรับภาษาไทย 100%",
            "• Support: รองรับทั้ง Localhost (127.0.0.1) และเครือข่ายวง LAN/Wi-Fi",
        ], Inches(4.8), Inches(1.9), Inches(3.7), Inches(4.8), C_SECONDARY),

        ("🎛️ Server Control Panel", "server.py (Multi-threaded GUI)", [
            "• Listener Thread: วนรับการเชื่อมต่อ client.accept() แบบ Non-blocking",
            "• Per-Client Worker Thread: จัดการการรับส่งข้อมูลของผู้ใช้แต่ละคน",
            "• Thread-Safe Mutex Lock: ป้องกัน Race Condition เมื่อสมาชิกเข้า-ออก",
            "• Live Administration: แสดงผล Log (Read-only), รายชื่อพร้อมสีและ IP, เตะผู้ใช้, และแชทในชื่อ Server",
        ], Inches(8.9), Inches(1.9), Inches(3.6), Inches(4.8), C_ACCENT),
    ]

    for title, sub, bullets, x, y, w, h, col in nodes:
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)
        card.fill.solid()
        card.fill.fore_color.rgb = C_CARD_BG
        card.line.color.rgb = C_BORDER
        card.line.width = Pt(1.5)

        bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, Inches(0.12))
        bar.fill.solid()
        bar.fill.fore_color.rgb = col
        bar.line.fill.background()

        tb = slide.shapes.add_textbox(x + Inches(0.2), y + Inches(0.25), w - Inches(0.4), h - Inches(0.4))
        tf = tb.text_frame
        tf.word_wrap = True

        p1 = tf.paragraphs[0]
        p1.text = title
        p1.font.name = FONT_HEADING
        p1.font.size = Pt(15)
        p1.font.bold = True
        p1.font.color.rgb = C_TEXT_DARK

        p2 = tf.add_paragraph()
        p2.text = sub
        p2.font.name = FONT_BODY
        p2.font.size = Pt(10)
        p2.font.bold = True
        p2.font.color.rgb = col
        p2.space_before = Pt(2)

        for b in bullets:
            pb = tf.add_paragraph()
            pb.text = b
            pb.font.name = FONT_BODY
            pb.font.size = Pt(11)
            pb.font.color.rgb = C_TEXT_MUTED
            pb.space_before = Pt(8)


def build_slide_04_protocol(prs):
    """Slide 4: Communication Protocol Table"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_header(slide, "โปรโตคอลสื่อสาร", "รูปแบบโปรโตคอลการแลกเปลี่ยนข้อมูล (JSON Network Protocol)", "โครงสร้างของแพ็กเก็ต JSON ที่ใช้สื่อสารระหว่าง Client และ Server")

    packets = [
        ("join", "Client ➔ Server", "ขอเข้าร่วมห้องแชท", '{"type": "join", "username": "Somchai_MSU"}', "ตรวจสอบชื่อว่างและชื่อซ้ำ"),
        ("join_ack", "Server ➔ Client", "ตอบรับ/ปฏิเสธการเข้า", '{"type": "join_ack", "success": true, "color": "#1E88E5", "message": "ยินดีต้อนรับ"}', "ส่งผลการตรวจสอบและสีประจำตัว"),
        ("chat", "Client ⇄ Server", "ส่งและกระจายข้อความ", '{"type": "chat", "sender": "Server", "content": "ยินดีต้อนรับทุกคน", "time": "14:58"}', "ส่งต่อ (Broadcast) ให้ทุกคนในห้อง"),
        ("sticker", "Client ⇄ Server", "ส่งสติ๊กเกอร์การ์ด", '{"type": "sticker", "emoji": "🎉", "title": "ยินดีด้วย!", "sender": "..."}', "แสดงผลเป็นการ์ดกราฟิกพิเศษ"),
        ("user_list", "Server ➔ Client", "อัปเดตสมาชิกและ IP", '{"type": "user_list", "users": [{"username": "...", "color": "...", "ip": "...", "port": ...}], "count": 3}', "ส่งรายการผู้ใช้, สี และ IP ให้ทุกคน"),
        ("kicked", "Server ➔ Client", "แจ้งเตือนการถูกเตะ", '{"type": "kicked", "reason": "คุณถูกเตะออกจากห้องโดยผู้ดูแลระบบ"}', "ตัดการเชื่อมต่อ Socket ทันที"),
        ("leave", "Client ➔ Server", "ออกจากห้องแชท", '{"type": "leave"}', "แจ้ง Server เพื่อปิด Socket อย่างปลอดภัย"),
    ]

    rows = len(packets) + 1
    cols = 5
    table_shape = slide.shapes.add_table(rows, cols, Inches(0.8), Inches(1.85), Inches(11.733), Inches(4.8))
    table = table_shape.table

    col_widths = [Inches(1.5), Inches(1.8), Inches(2.2), Inches(3.8), Inches(2.433)]
    for i, w in enumerate(col_widths):
        table.columns[i].width = w

    headers = ["ประเภทแพ็กเก็ต", "ทิศทางการส่ง", "คำอธิบายการทำงาน", "ตัวอย่างโครงสร้าง JSON Payload", "หมายเหตุการทำงาน"]
    for i, h_text in enumerate(headers):
        cell = table.cell(0, i)
        cell.fill.solid()
        cell.fill.fore_color.rgb = C_PRIMARY
        p = cell.text_frame.paragraphs[0]
        p.text = h_text
        p.font.name = FONT_HEADING
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = RGBColor(255, 255, 255)
        p.alignment = PP_ALIGN.CENTER

    for row_idx, data in enumerate(packets, start=1):
        for col_idx, val in enumerate(data):
            cell = table.cell(row_idx, col_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(255, 255, 255) if row_idx % 2 == 1 else RGBColor(241, 245, 249)
            p = cell.text_frame.paragraphs[0]
            p.text = val
            p.font.name = "Consolas" if col_idx == 3 else FONT_BODY
            p.font.size = Pt(9.5 if col_idx == 3 else 10)
            if col_idx == 0:
                p.font.bold = True
                p.font.color.rgb = C_PRIMARY
            elif col_idx == 1:
                p.font.bold = True
                p.font.color.rgb = C_SECONDARY
            else:
                p.font.color.rgb = C_TEXT_DARK


def build_slide_05_server_start(prs):
    """Slide 5: Server Startup Guide"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_header(slide, "คู่มือ SERVER", "การเปิดใช้งานเซิร์ฟเวอร์ (Server Startup Guide)", "ขั้นตอนการกำหนดค่าและเริ่มต้นระบบห้องแชทฝั่งผู้ดูแลระบบ")

    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.85), Inches(4.5), Inches(4.9))
    card.fill.solid()
    card.fill.fore_color.rgb = C_CARD_BG
    card.line.color.rgb = C_BORDER
    card.line.width = Pt(1.5)

    tb = slide.shapes.add_textbox(Inches(1.0), Inches(2.05), Inches(4.1), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True

    steps = [
        ("1. การรันโปรแกรมเซิร์ฟเวอร์", "เปิด Terminal/Command Prompt แล้วพิมพ์คำสั่ง:\npython server.py\nระบบจะเปิดหน้าต่าง Server Control Panel ขึ้นมา"),
        ("2. กำหนด IP Address และ Port", "• IP เซิร์ฟเวอร์: ค่าเริ่มต้น 0.0.0.0 (รับการเชื่อมต่อจากทุก Interface ทั้งในเครื่องและในวง LAN)\n• Port: ค่าเริ่มต้น 5000 (สามารถปรับเปลี่ยนได้ตามต้องการ)"),
        ("3. เริ่มการทำงานเซิร์ฟเวอร์", "คลิกปุ่ม '▶ เริ่มเซิร์ฟเวอร์ (Start)'\n• แบนเนอร์สีฟ้าแสดง IP ในวง LAN จะปรากฏขึ้นทันที เพื่อให้นำไปบอกเพื่อนในวงเดียวกัน\n• สถานะเปลี่ยนเป็น '● เซิร์ฟเวอร์: กำลังทำงาน (Online)'\n• แถบพิมพ์ข้อความด้านล่างจะปลดล็อกพร้อมใช้งานทันที"),
    ]

    for i, (title, content) in enumerate(steps):
        p_t = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p_t.text = title
        p_t.font.name = FONT_HEADING
        p_t.font.size = Pt(13)
        p_t.font.bold = True
        p_t.font.color.rgb = C_PRIMARY
        if i > 0:
            p_t.space_before = Pt(12)

        p_c = tf.add_paragraph()
        p_c.text = content
        p_c.font.name = FONT_BODY
        p_c.font.size = Pt(10.5)
        p_c.font.color.rgb = C_TEXT_MUTED
        p_c.space_before = Pt(3)

    add_image_card(slide, "01_server_initial_offline.png", Inches(5.6), Inches(1.85), Inches(3.3), Inches(2.3), "รูปที่ 1: สถานะเซิร์ฟเวอร์ก่อนเปิดใช้งาน (Offline)")
    add_image_card(slide, "02_server_running_online.png", Inches(9.2), Inches(1.85), Inches(3.3), Inches(2.3), "รูปที่ 2: เซิร์ฟเวอร์เริ่มทำงานและแสดงแบนเนอร์ LAN IP (Online)")

    tip = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(5.6), Inches(4.6), Inches(6.9), Inches(2.15))
    tip.fill.solid()
    tip.fill.fore_color.rgb = RGBColor(236, 253, 245) # Emerald 50
    tip.line.color.rgb = C_ACCENT
    tip.line.width = Pt(1)

    tb_t = tip.text_frame
    tb_t.margin_left = Inches(0.25)
    tb_t.margin_top = Inches(0.2)
    p_tip_h = tb_t.paragraphs[0]
    p_tip_h.text = "💡 จุดเด่นด้านความสะดวกในระบบเครือข่าย (Auto LAN IP Detection)"
    p_tip_h.font.name = FONT_HEADING
    p_tip_h.font.size = Pt(12)
    p_tip_h.font.bold = True
    p_tip_h.font.color.rgb = C_ACCENT

    p_tip_b = tb_t.add_paragraph()
    p_tip_b.text = "• โปรแกรมมีระบบค้นหา IP เครื่องเซิร์ฟเวอร์ในวง LAN อัตโนมัติและแสดงขึ้นมาในกรอบสีฟ้าชัดเจน ผู้ใช้ไม่ต้องเปิด Command Prompt พิมพ์ ipconfig เอง\n• แถบพิมพ์ข้อความด้านล่างจะตรึงแน่นที่ขอบจอเสมอ ไม่ถูกดันตกขอบเมื่อแบนเนอร์ IP เปิดขึ้นมา"
    p_tip_b.font.name = FONT_BODY
    p_tip_b.font.size = Pt(10)
    p_tip_b.font.color.rgb = C_TEXT_DARK
    p_tip_b.space_before = Pt(4)


def build_slide_06_server_logs(prs):
    """Slide 6: Server Real-time Logs"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_header(slide, "คู่มือ SERVER", "ระบบบันทึกเหตุการณ์และสถานะสมาชิก (Event Logs & Members)", "การติดตามความเคลื่อนไหวในห้องแชทแบบเรียลไทม์ผ่าน Server Control Panel")

    add_image_card(slide, "10_server_active_logs_and_users.png", Inches(0.8), Inches(1.85), Inches(6.8), Inches(4.8), "รูปที่ 3: แผงควบคุมเซิร์ฟเวอร์ขณะมีผู้ใช้งาน 4 คน เชื่อมต่อ สนทนา และส่งสติ๊กเกอร์")

    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.9), Inches(1.85), Inches(4.6), Inches(4.8))
    card.fill.solid()
    card.fill.fore_color.rgb = C_CARD_BG
    card.line.color.rgb = C_BORDER
    card.line.width = Pt(1.5)

    tb = slide.shapes.add_textbox(Inches(8.1), Inches(2.05), Inches(4.2), Inches(4.4))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "📋 จุดเด่นของระบบบันทึกเหตุการณ์และสมาชิก"
    p.font.name = FONT_HEADING
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = C_PRIMARY

    tags = [
        ("🟢 [JOIN]", "แสดงเมื่อมีผู้ใช้ใหม่เข้าร่วมห้อง พร้อมระบุ IP:Port ผู้เชื่อมต่อ"),
        ("💬 [CHAT]", "แสดงข้อความสนทนาพร้อมชื่อและสีประจำตัวของผู้ส่ง"),
        ("🏷️ [STICKER]", "เรนเดอร์การ์ดสติ๊กเกอร์ขนาดใหญ่ให้แอดมินเห็นแบบเดียวกับผู้ใช้"),
        ("🛡️ ระบบ Read-Only", "ล็อกกล่องข้อความไม่ให้แอดมินเผลอคลิกลบหรือพิมพ์แทรกข้อความบนจอได้"),
        ("👥 จุดสีประจำตัวสมาชิก", "แสดงจุดสี ● ตรงกับสีของผู้ใช้แต่ละคนในกล่องรายชื่อออนไลน์"),
        ("🌐 แสดง IP ของทุกคน", "แสดง IP:Port ต่อท้ายชื่อสมาชิกแต่ละคนอย่างชัดเจน (เช่น 10.26.25.195, 10.26.25.102)"),
    ]

    for tag, desc in tags:
        pt = tf.add_paragraph()
        r1 = pt.add_run()
        r1.text = f"{tag}: "
        r1.font.bold = True
        r1.font.size = Pt(10.5)
        r1.font.color.rgb = C_TEXT_DARK
        r2 = pt.add_run()
        r2.text = desc
        r2.font.size = Pt(10)
        r2.font.color.rgb = C_TEXT_MUTED
        pt.space_before = Pt(6)


def build_slide_07_server_admin_actions(prs):
    """Slide 7: Server Admin Actions (Kick & Chat)"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_header(slide, "คู่มือ SERVER", "การแชทและการควบคุมผู้ใช้งาน (Chat & User Management)", "การส่งข้อความ/สติ๊กเกอร์ในนาม Server และการเตะผู้ใช้ที่ไม่พึงประสงค์")

    # Left: Chat as Server
    card_l = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.85), Inches(5.6), Inches(4.9))
    card_l.fill.solid()
    card_l.fill.fore_color.rgb = C_CARD_BG
    card_l.line.color.rgb = C_BORDER
    card_l.line.width = Pt(1.5)

    tb_l = slide.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.2), Inches(1.5))
    tf_l = tb_l.text_frame
    tf_l.word_wrap = True
    p_l = tf_l.paragraphs[0]
    p_l.text = "💬 เซิร์ฟเวอร์ร่วมแชทและส่งสติ๊กเกอร์ (Chat as Server)"
    p_l.font.name = FONT_HEADING
    p_l.font.size = Pt(13)
    p_l.font.bold = True
    p_l.font.color.rgb = C_PRIMARY

    p_lc = tf_l.add_paragraph()
    p_lc.text = "1. พิมพ์ข้อความในช่องแชทด้านล่าง หรือกดเลือกอีโมจิ/สติ๊กเกอร์การ์ด\n2. กดปุ่ม 'ส่ง (Send) ✈️' หรือกด Enter\n3. ข้อความจะถูกส่งตรงไปยังทุกคนในห้องในนาม 'Server' พร้อมสีประจำตัว"
    p_lc.font.name = FONT_BODY
    p_lc.font.size = Pt(10.5)
    p_lc.font.color.rgb = C_TEXT_MUTED
    p_lc.space_before = Pt(4)

    add_image_card(slide, "11_server_broadcast_sent.png", Inches(1.0), Inches(3.6), Inches(5.2), Inches(2.9), "รูปที่ 4: เซิร์ฟเวอร์ส่งสติ๊กเกอร์และข้อความประกาศในนาม Server")

    # Right: Kick User
    card_r = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.9), Inches(1.85), Inches(5.6), Inches(4.9))
    card_r.fill.solid()
    card_r.fill.fore_color.rgb = C_CARD_BG
    card_r.line.color.rgb = C_BORDER
    card_r.line.width = Pt(1.5)

    tb_r = slide.shapes.add_textbox(Inches(7.1), Inches(2.0), Inches(5.2), Inches(1.5))
    tf_r = tb_r.text_frame
    tf_r.word_wrap = True
    p_r = tf_r.paragraphs[0]
    p_r.text = "⚠️ การเตะผู้ใช้ออกจากห้อง (Kick User)"
    p_r.font.name = FONT_HEADING
    p_r.font.size = Pt(13)
    p_r.font.bold = True
    p_r.font.color.rgb = C_RED

    p_rc = tf_r.add_paragraph()
    p_rc.text = "1. คลิกเลือกแถวผู้ใช้ในกล่องรายชื่อ '👥 ออนไลน์' (จะมีไฮไลต์สีฟ้าอ่อน)\n2. กดปุ่ม '⚠️ เตะผู้ใช้ที่เลือก (Kick)'\n3. กดยืนยันในกล่องข้อความเตือน -> ผู้ใช้จะถูกตัด Socket ทันทีและขึ้นแจ้งเตือน"
    p_rc.font.name = FONT_BODY
    p_rc.font.size = Pt(10.5)
    p_rc.font.color.rgb = C_TEXT_MUTED
    p_rc.space_before = Pt(4)

    add_image_card(slide, "13_server_after_user_kicked.png", Inches(7.1), Inches(3.6), Inches(5.2), Inches(2.9), "รูปที่ 5: ผลการเตะผู้ใช้ Nong_May บันทึก [ADMIN] และอัปเดตสมาชิกเหลือ 3 คน")


def build_slide_08_client_login(prs):
    """Slide 8: Client Login Screen & Color Hash Identity"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_header(slide, "คู่มือ CLIENT", "การเข้าสู่ระบบและสีประจำตัว (Login & User Identity)", "ขั้นตอนการระบุข้อมูลเพื่อเข้าสู่ห้องแชทและระบบคำนวณสีประจำตัวอัตโนมัติ")

    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.85), Inches(4.6), Inches(4.9))
    card.fill.solid()
    card.fill.fore_color.rgb = C_CARD_BG
    card.line.color.rgb = C_BORDER
    card.line.width = Pt(1.5)

    tb = slide.shapes.add_textbox(Inches(1.0), Inches(2.05), Inches(4.2), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True

    steps = [
        ("1. ระบุ IP และ Port ของเซิร์ฟเวอร์", "• IP เซิร์ฟเวอร์: เปลี่ยนจากค่าเริ่มต้น 127.0.0.1 เป็น IP วงแลนของเครื่องเซิร์ฟเวอร์ เช่น 10.26.25.195 ตามที่แบนเนอร์แจ้ง\n• Port: กรอกพอร์ต 5000 ให้ตรงกัน"),
        ("2. ตั้งชื่อผู้ใช้งาน (Username)", "กรอกชื่อที่ต้องการใช้ในห้องแชท (ต้องไม่เป็นค่าว่าง)"),
        ("✨ ไฮไลต์: ระบบคำนวณสีประจำตัว (Hash Avatar)", "โปรแกรมใช้ Deterministic Hashing โดยคำนวณค่า MD5 จากชื่อผู้ใช้เพื่อเลือกสีประจำตัวจาก 16 โทนสีมาตรฐาน ทำให้สีประจำตัวของผู้ใช้จะคงเดิมเสมอแม้เข้าใหม่ และมีพรีวิวสีสดใสปรากฏขึ้นทันทีขณะพิมพ์"),
        ("3. กดเข้าสู่ห้องแชท", "คลิกปุ่ม '🚀 เข้าสู่ห้องแชท (Connect)' หรือกดปุ่ม Enter"),
    ]

    for i, (title, content) in enumerate(steps):
        p_t = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p_t.text = title
        p_t.font.name = FONT_HEADING
        p_t.font.size = Pt(12)
        p_t.font.bold = True
        p_t.font.color.rgb = C_PRIMARY if "✨" not in title else C_AMBER
        if i > 0:
            p_t.space_before = Pt(10)

        p_c = tf.add_paragraph()
        p_c.text = content
        p_c.font.name = FONT_BODY
        p_c.font.size = Pt(10)
        p_c.font.color.rgb = C_TEXT_MUTED
        p_c.space_before = Pt(2)

    add_image_card(slide, "03_client_login_empty.png", Inches(5.8), Inches(1.85), Inches(3.4), Inches(2.3), "รูปที่ 6: หน้าต่างเข้าสู่ระบบเริ่มต้น (ค่าเริ่มต้น 127.0.0.1)")
    add_image_card(slide, "04_client_login_typing_preview.png", Inches(9.4), Inches(1.85), Inches(3.4), Inches(2.3), "รูปที่ 7: กรอก IP วงแลน 10.26.25.195 และพรีวิวสี")
    add_image_card(slide, "05_client_login_duplicate_error.png", Inches(7.5), Inches(4.45), Inches(3.6), Inches(2.2), "รูปที่ 8: การแจ้งเตือนกรณีชื่อผู้ใช้ซ้ำกันในระบบ")


def build_slide_09_client_chat_ui(prs):
    """Slide 9: Client Chat Room Layout"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_header(slide, "คู่มือ CLIENT", "ส่วนประกอบหน้าต่างห้องแชทหลัก (Chat Room Layout)", "โครงสร้างองค์ประกอบและพื้นที่การใช้งานของหน้าจอสนทนา")

    add_image_card(slide, "07_client_chat_active_conversation.png", Inches(0.8), Inches(1.85), Inches(6.8), Inches(4.8), "รูปที่ 9: หน้าต่างห้องแชทขณะสมาชิกพูดคุย ส่งสติ๊กเกอร์ และแสดง IP ของทุกคน")

    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.9), Inches(1.85), Inches(4.6), Inches(4.8))
    card.fill.solid()
    card.fill.fore_color.rgb = C_CARD_BG
    card.line.color.rgb = C_BORDER
    card.line.width = Pt(1.5)

    tb = slide.shapes.add_textbox(Inches(8.1), Inches(2.05), Inches(4.2), Inches(4.4))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "🎯 ส่วนประกอบสำคัญบนหน้าจอแชท"
    p.font.name = FONT_HEADING
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = C_PRIMARY

    parts = [
        ("1. แถบหัวเรื่องด้านบน (Top Bar)", "แสดงสถานะการเชื่อมต่อ (IP:Port), ป้ายชื่อของคุณพร้อมสีประจำตัว และปุ่ม '🚪 ออกจากห้องแชท'"),
        ("2. พื้นที่สนทนาหลัก (Chat Stream)", "ใช้ ScrolledText แสดงเวลา [HH:MM], ชื่อผู้ส่งตามสีประจำตัว, ข้อความ, และการ์ดสติ๊กเกอร์"),
        ("3. แถบรายชื่อสมาชิกพร้อม IP (Members Sidebar)", "แสดงจำนวนผู้ใช้ออนไลน์, จุดสีประจำตัว ●, สถานะ (คุณ)/(โฮสต์), และแสดง IP:Port ของแต่ละคน"),
        ("4. แถบส่งข้อความด้านล่าง (Input Bar)", "ประกอบด้วยปุ่มเปิดเมนูอีโมจิ, เมนูปุ่มสติ๊กเกอร์, ช่องพิมพ์ข้อความ, และปุ่ม 'ส่ง (Send) ✈️'"),
    ]

    for title, desc in parts:
        pt = tf.add_paragraph()
        pt.text = title
        pt.font.name = FONT_HEADING
        pt.font.size = Pt(11)
        pt.font.bold = True
        pt.font.color.rgb = C_TEXT_DARK
        pt.space_before = Pt(8)

        pd = tf.add_paragraph()
        pd.text = desc
        pd.font.name = FONT_BODY
        pd.font.size = Pt(10)
        pd.font.color.rgb = C_TEXT_MUTED
        pd.space_before = Pt(2)


def build_slide_10_client_stickers(prs):
    """Slide 10: Stickers Feature"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_header(slide, "ลูกเล่นพิเศษ", "ระบบสติ๊กเกอร์แบบการ์ดกราฟิก (Interactive Stickers)", "การส่งสติ๊กเกอร์แทนความรู้สึกด้วยการ์ดกราฟิกสีสันสดใส")

    add_image_card(slide, "09_client_sticker_picker_popup.png", Inches(0.8), Inches(1.85), Inches(4.5), Inches(4.8), "รูปที่ 10: หน้าต่างป๊อปอัปเลือกสติ๊กเกอร์ 12 อารมณ์")

    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(5.6), Inches(1.85), Inches(6.9), Inches(4.8))
    card.fill.solid()
    card.fill.fore_color.rgb = C_CARD_BG
    card.line.color.rgb = C_BORDER
    card.line.width = Pt(1.5)

    tb = slide.shapes.add_textbox(Inches(5.9), Inches(2.05), Inches(6.3), Inches(4.4))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "🏷️ ความสามารถของระบบสติ๊กเกอร์"
    p.font.name = FONT_HEADING
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = C_PRIMARY

    bullets = [
        ("เปิดใช้งานสะดวกในคลิกเดียว", "เพียงคลิกปุ่ม '🏷️ สติ๊กเกอร์' ที่แถบด้านล่าง หน้าต่าง Pop-up จะเปิดขึ้นมาให้เลือกทันที ทั้งฝั่ง Client และ Server"),
        ("12 สติ๊กเกอร์ด่วนยอดนิยม", "คัดสรรสติ๊กเกอร์ที่ใช้บ่อย เช่น 👍 สุดยอดเลย!, ❤️ รักเลย, 🎉 ยินดีด้วย!, 😂 ขำกลิ้ง, 🔥 ไฟลุก!, 🍕 หิวข้าวมาก, ☕ พักดื่มกาแฟ, 💻 กำลังปั่นงาน"),
        ("แตะแล้วส่งทันที (Instant Send)", "เมื่อผู้ใช้คลิกเลือกสติ๊กเกอร์ที่ต้องการ หน้าต่างเลือกจะปิดตัวเองและส่งข้อมูลสติ๊กเกอร์เข้าสู่ห้องแชททันทีโดยไม่ต้องกดปุ่มส่งซ้ำ"),
        ("เรนเดอร์เป็นการ์ดพิเศษ (Rich Card Rendering)", "สติ๊กเกอร์ในห้องแชทจะถูกสร้างขึ้นเป็น Frame การ์ดขนาดใหญ่พร้อมกรอบและป้ายกำกับข้อความ ช่วยเพิ่มสีสันและมิติในการสื่อสาร"),
    ]

    for title, desc in bullets:
        pt = tf.add_paragraph()
        pt.text = f"• {title}"
        pt.font.name = FONT_HEADING
        pt.font.size = Pt(11)
        pt.font.bold = True
        pt.font.color.rgb = C_TEXT_DARK
        pt.space_before = Pt(8)

        pd = tf.add_paragraph()
        pd.text = desc
        pd.font.name = FONT_BODY
        pd.font.size = Pt(10)
        pd.font.color.rgb = C_TEXT_MUTED
        pd.space_before = Pt(2)


def build_slide_11_client_emojis_broadcast(prs):
    """Slide 11: Emojis & Server Announcements"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_header(slide, "ลูกเล่นพิเศษ", "คลังอีโมจิและการรับข้อความจากเซิร์ฟเวอร์ (Emojis & Server Chat)", "การใช้งานอีโมจิกว่า 50 แบบ และรูปแบบการแสดงผลข้อความจาก Server")

    add_image_card(slide, "08_client_emoji_picker_popup.png", Inches(0.8), Inches(1.85), Inches(4.6), Inches(4.8), "รูปที่ 11: ป๊อปอัปกริดอีโมจิ 50+ รายการ")
    add_image_card(slide, "12_client_broadcast_received.png", Inches(5.8), Inches(1.85), Inches(6.7), Inches(3.2), "รูปที่ 12: การแสดงผลข้อความและสติ๊กเกอร์จาก Server ในห้องแชท")

    tip = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(5.8), Inches(5.35), Inches(6.7), Inches(1.3))
    tip.fill.solid()
    tip.fill.fore_color.rgb = RGBColor(254, 242, 242) # Red 50
    tip.line.color.rgb = C_PRIMARY
    tip.line.width = Pt(1)

    tb_t = tip.text_frame
    tb_t.margin_left = Inches(0.2)
    tb_t.margin_top = Inches(0.12)
    p_t = tb_t.paragraphs[0]
    p_t.text = "💬 เซิร์ฟเวอร์ในฐานะผู้ร่วมแชท (Server Participation)"
    p_t.font.name = FONT_HEADING
    p_t.font.size = Pt(11)
    p_t.font.bold = True
    p_t.font.color.rgb = C_PRIMARY

    p_d = tb_t.add_paragraph()
    p_d.text = "เซิร์ฟเวอร์สามารถส่งข้อความแชท สติ๊กเกอร์ หรือส่งประกาศข้อความในชื่อ Server ได้อย่างกลมกลืน โดยทุกคนในห้องจะเห็นสัญลักษณ์และสีประจำตัวของ Server ในการสนทนาอย่างชัดเจน"
    p_d.font.name = FONT_BODY
    p_d.font.size = Pt(9.5)
    p_d.font.color.rgb = C_TEXT_DARK
    p_d.space_before = Pt(2)


def build_slide_12_disconnection(prs):
    """Slide 12: Leaving & Disconnection Handling"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_header(slide, "คู่มือ CLIENT", "การออกจากห้องแชทและการจัดการสถานะ (Disconnection)", "กระบวนการออกจากห้องแบบปกติ และการตรวจจับกรณีหลุดการเชื่อมต่อ")

    add_image_card(slide, "14_client_disconnected_state.png", Inches(0.8), Inches(1.85), Inches(5.6), Inches(4.8), "รูปที่ 13: หน้าจอหลังออกจากห้องแชทและคืนสถานะพร้อมเข้าใหม่")

    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.85), Inches(5.7), Inches(4.8))
    card.fill.solid()
    card.fill.fore_color.rgb = C_CARD_BG
    card.line.color.rgb = C_BORDER
    card.line.width = Pt(1.5)

    tb = slide.shapes.add_textbox(Inches(7.0), Inches(2.05), Inches(5.3), Inches(4.4))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "🚪 3 รูปแบบการสิ้นสุดการเชื่อมต่อในระบบ"
    p.font.name = FONT_HEADING
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = C_PRIMARY

    scenarios = [
        ("1. การออกจากห้องแบบปกติ (Graceful Leave)", "ผู้ใช้กดปุ่ม '🚪 ออกจากห้องแชท'\n• ไคลเอนต์ส่งแพ็กเก็ต {'type': 'leave'} ไปยังเซิร์ฟเวอร์\n• เซิร์ฟเวอร์ปิด Socket และส่ง system packet แจ้งทุกคนในห้อง\n• ไคลเอนต์สลับหน้าจอกลับมาที่หน้า Login อย่างปลอดภัย"),
        ("2. การถูกเตะออกจากห้อง (Admin Kicked)", "หากแอดมินสั่งเตะผู้ใช้ เซิร์ฟเวอร์จะส่งแพ็กเก็ต {'type': 'kicked'}\n• ไคลเอนต์จะแสดงกล่องแจ้งเตือน 'คุณถูกเตะออกจากห้องโดยผู้ดูแลระบบ'\n• ไคลเอนต์จะปิดการเชื่อมต่อและกลับมาที่หน้าต่างเริ่มต้น"),
        ("3. การขาดการเชื่อมต่อกะทันหัน (Server Lost / Network Drop)", "หากเซิร์ฟเวอร์ปิดตัวลง หรือสายแลน/เน็ตเวิร์กหลุด\n• เธรด receive_loop จะตรวจจับการปิด Socket และแจ้งเตือน 'ขาดการเชื่อมต่อจากเซิร์ฟเวอร์'\n• ป้องกันโปรแกรมค้าง (Hang) ด้วยการคืนทรัพยากรอย่างสมบูรณ์"),
    ]

    for title, desc in scenarios:
        pt = tf.add_paragraph()
        pt.text = title
        pt.font.name = FONT_HEADING
        pt.font.size = Pt(11)
        pt.font.bold = True
        pt.font.color.rgb = C_TEXT_DARK
        pt.space_before = Pt(8)

        pd = tf.add_paragraph()
        pd.text = desc
        pd.font.name = FONT_BODY
        pd.font.size = Pt(9.5)
        pd.font.color.rgb = C_TEXT_MUTED
        pd.space_before = Pt(2)


def build_slide_13_troubleshooting(prs):
    """Slide 13: Troubleshooting & FAQ"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_header(slide, "การแก้ไขปัญหา", "ปัญหาที่พบบ่อยและวิธีแก้ไข (Troubleshooting & FAQ)", "แนวทางการตรวจสอบและแก้ไขข้อผิดพลาดที่อาจเกิดขึ้นระหว่างใช้งาน")

    faqs = [
        ("❌ เชื่อมต่อเซิร์ฟเวอร์ไม่สำเร็จ (Connection Refused)", "สาเหตุ: เซิร์ฟเวอร์ยังไม่ได้เปิด หรือระบุ IP/Port ไม่ถูกต้อง\nวิธีแก้: ตรวจสอบว่าหน้าต่าง server.py อยู่ในสถานะ 'กำลังทำงาน' หรือไม่ และนำ IP ในแบนเนอร์สีฟ้าบนเซิร์ฟเวอร์มากรอกใน client.py"),
        ("⚠️ ชื่อผู้ใช้งานนี้มีผู้ใช้งานแล้ว (Duplicate Username)", "สาเหตุ: มีผู้ใช้ออนไลน์ในห้องใช้ชื่อเดียวกันนี้ หรือแอบอ้างใช้ชื่อ 'Server'\nวิธีแก้: เปลี่ยนชื่อผู้ใช้งานใหม่ให้ไม่ซ้ำกับผู้อื่นในระบบ"),
        ("🔒 ไม่สามารถเชื่อมต่อข้ามเครื่องในวง LAN/Wi-Fi ได้", "สาเหตุ: Windows Defender Firewall หรือ Antivirus บล็อกการเชื่อมต่อของพอร์ต 5000\nวิธีแก้: ไปที่ Windows Firewall และกดยอมรับ Allow Access หรือเพิ่ม Inbound Rule สำหรับพอร์ต 5000"),
        ("📦 ต้องติดตั้งไลบรารีอะไรเพิ่มเติมหรือไม่?", "คำตอบ: ไม่ต้องติดตั้งแพ็กเกจใดๆ เพิ่มเติม (No pip install needed)\nระบบใช้เฉพาะ Python Standard Library (socket, threading, tkinter, json, hashlib) สามารถนำไปรันบนเครื่องอื่นได้ทันที"),
    ]

    left = Inches(0.8)
    top = Inches(1.85)
    w = Inches(5.7)
    h = Inches(2.35)
    gap_x = Inches(0.33)
    gap_y = Inches(0.2)

    for i, (title, content) in enumerate(faqs):
        col = i % 2
        row = i // 2
        x = left + col * (w + gap_x)
        y = top + row * (h + gap_y)

        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)
        card.fill.solid()
        card.fill.fore_color.rgb = C_CARD_BG
        card.line.color.rgb = C_BORDER
        card.line.width = Pt(1.5)

        tb = slide.shapes.add_textbox(x + Inches(0.2), y + Inches(0.15), w - Inches(0.4), h - Inches(0.3))
        tf = tb.text_frame
        tf.word_wrap = True

        pt = tf.paragraphs[0]
        pt.text = title
        pt.font.name = FONT_HEADING
        pt.font.size = Pt(11.5)
        pt.font.bold = True
        pt.font.color.rgb = C_PRIMARY

        pc = tf.add_paragraph()
        pc.text = content
        pc.font.name = FONT_BODY
        pc.font.size = Pt(10)
        pc.font.color.rgb = C_TEXT_MUTED
        pc.space_before = Pt(5)


def build_slide_14_future_enhancements(prs):
    """Slide 14: Summary & Future Enhancements"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_header(slide, "สรุปและต่อยอด", "สรุปผลการพัฒนาและแนวทางต่อยอด (Summary & Future Work)", "จุดเด่นของโครงงานและโอกาสในการพัฒนาฟีเจอร์ขั้นสูงในอนาคต")

    card_l = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.85), Inches(5.7), Inches(4.9))
    card_l.fill.solid()
    card_l.fill.fore_color.rgb = C_CARD_BG
    card_l.line.color.rgb = C_BORDER
    card_l.line.width = Pt(1.5)

    bar_l = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.85), Inches(5.7), Inches(0.1))
    bar_l.fill.solid()
    bar_l.fill.fore_color.rgb = C_ACCENT
    bar_l.line.fill.background()

    tb_l = slide.shapes.add_textbox(Inches(1.0), Inches(2.1), Inches(5.3), Inches(4.5))
    tf_l = tb_l.text_frame
    tf_l.word_wrap = True
    p_lh = tf_l.paragraphs[0]
    p_lh.text = "🏆 สรุปผลความสำเร็จของโครงงาน"
    p_lh.font.name = FONT_HEADING
    p_lh.font.size = Pt(14)
    p_lh.font.bold = True
    p_lh.font.color.rgb = C_ACCENT

    points_l = [
        ("ความเสถียรของเครือข่าย", "การรับส่งข้อมูลผ่าน TCP Socket ทำงานได้อย่างถูกต้อง แม่นยำ ไม่สูญหาย และแยกแพ็กเก็ตด้วย Newline Framing ได้อย่างสมบูรณ์"),
        ("ระบบมัลติเธรด (Multithreading)", "แยกการรับส่งข้อมูลเครือข่ายออกจากเธรด GUI ทำให้หน้าจอไม่ค้างและตอบสนองได้รวดเร็วตลอดเวลา"),
        ("ประสบการณ์ผู้ใช้ (UX/UI)", "หน้าต่าง Tkinter ทันสมัย มีฟังก์ชันสติ๊กเกอร์ อีโมจิ สีประจำตัว จุดสีออนไลน์ และแสดง IP ชัดเจนทั้งสองฝั่ง"),
        ("สถาปัตยกรรมแบบ Standalone", "ใช้เฉพาะโมดูลมาตรฐานของ Python ไม่ต้องติดตั้ง External Dependency ทำให้พกพาไปรันได้ทุกเครื่อง"),
    ]

    for t, d in points_l:
        p = tf_l.add_paragraph()
        p.text = f"✔ {t}: {d}"
        p.font.name = FONT_BODY
        p.font.size = Pt(10.5)
        p.font.color.rgb = C_TEXT_DARK
        p.space_before = Pt(8)

    card_r = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.85), Inches(5.7), Inches(4.9))
    card_r.fill.solid()
    card_r.fill.fore_color.rgb = C_CARD_BG
    card_r.line.color.rgb = C_BORDER
    card_r.line.width = Pt(1.5)

    bar_r = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(6.8), Inches(1.85), Inches(5.7), Inches(0.1))
    bar_r.fill.solid()
    bar_r.fill.fore_color.rgb = C_PRIMARY
    bar_r.line.fill.background()

    tb_r = slide.shapes.add_textbox(Inches(7.0), Inches(2.1), Inches(5.3), Inches(4.5))
    tf_r = tb_r.text_frame
    tf_r.word_wrap = True
    p_rh = tf_r.paragraphs[0]
    p_rh.text = "🚀 แนวทางการพัฒนาต่อยอดในอนาคต (Roadmap)"
    p_rh.font.name = FONT_HEADING
    p_rh.font.size = Pt(14)
    p_rh.font.bold = True
    p_rh.font.color.rgb = C_PRIMARY

    points_r = [
        ("📁 ระบบรับส่งไฟล์ (File Transfer)", "เพิ่มโปรโตคอลรับส่งไฟล์เอกสารและรูปภาพระหว่างสมาชิกในห้อง"),
        ("🔒 การเข้ารหัสข้อมูล (SSL/TLS Encryption)", "ยกระดับความปลอดภัยด้วยการครอบ Secure Sockets Layer (TLS) ป้องกันการดักจับแพ็กเก็ต (Packet Sniffing)"),
        ("💬 ห้องแชทส่วนตัว (Private Message / DM)", "เพิ่มคำสั่งส่งข้อความกระซิบหรือเปิดห้องสนทนาย่อยแบบ 1 ต่อ 1"),
        ("💾 บันทึกประวัติลงฐานข้อมูล (Database)", "เชื่อมต่อฐานข้อมูล SQLite หรือ PostgreSQL เพื่อเก็บประวัติการสนทนาย้อนหลัง"),
    ]

    for t, d in points_r:
        p = tf_r.add_paragraph()
        p.text = f"⭐ {t}: {d}"
        p.font.name = FONT_BODY
        p.font.size = Pt(10.5)
        p.font.color.rgb = C_TEXT_DARK
        p.space_before = Pt(8)


def build_slide_15_qa_closing(prs):
    """Slide 15: Q&A and Thank You Slide"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg.fill.solid()
    bg.fill.fore_color.rgb = C_DARK_BG
    bg.line.fill.background()

    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(2.0), Inches(1.5), Inches(9.333), Inches(4.5))
    card.fill.solid()
    card.fill.fore_color.rgb = C_DARK_CARD
    card.line.color.rgb = RGBColor(51, 65, 85)
    card.line.width = Pt(1.5)

    tb = slide.shapes.add_textbox(Inches(2.5), Inches(2.0), Inches(8.333), Inches(3.5))
    tf = tb.text_frame
    tf.word_wrap = True

    p0 = tf.paragraphs[0]
    p0.text = "ขอบคุณสำหรับการรับชม"
    p0.font.name = FONT_HEADING
    p0.font.size = Pt(36)
    p0.font.bold = True
    p0.font.color.rgb = RGBColor(255, 255, 255)
    p0.alignment = PP_ALIGN.CENTER

    p1 = tf.add_paragraph()
    p1.text = "QUESTIONS & ANSWERS (Q&A)"
    p1.font.name = FONT_HEADING
    p1.font.size = Pt(18)
    p1.font.bold = True
    p1.font.color.rgb = RGBColor(56, 189, 248)
    p1.alignment = PP_ALIGN.CENTER
    p1.space_before = Pt(8)

    p2 = tf.add_paragraph()
    p2.text = "มีข้อสงสัยหรือคำถามเพิ่มเติมเกี่ยวกับโครงงานและระบบแชทเครือข่ายหรือไม่?"
    p2.font.name = FONT_BODY
    p2.font.size = Pt(13)
    p2.font.color.rgb = RGBColor(148, 163, 184)
    p2.alignment = PP_ALIGN.CENTER
    p2.space_before = Pt(12)

    p3 = tf.add_paragraph()
    p3.text = "── โครงงานวิชา Computer Networks (1/2569) | มหาวิทยาลัยมหาสารคาม ──"
    p3.font.name = FONT_BODY
    p3.font.size = Pt(11)
    p3.font.color.rgb = RGBColor(100, 116, 139)
    p3.alignment = PP_ALIGN.CENTER
    p3.space_before = Pt(25)


def generate_presentation():
    print("Generating updated PPTX presentation with python-pptx (10-Slide Curated Edition)...")
    prs = create_base_presentation()

    build_slide_01_cover(prs)
    build_slide_05_server_start(prs)
    build_slide_06_server_logs(prs)
    build_slide_07_server_admin_actions(prs)
    build_slide_08_client_login(prs)
    build_slide_09_client_chat_ui(prs)
    build_slide_10_client_stickers(prs)
    build_slide_11_client_emojis_broadcast(prs)
    build_slide_12_disconnection(prs)
    build_slide_15_qa_closing(prs)

    # Save to English path
    prs.save(OUTPUT_PPTX_ENG)
    print(f"Saved: {OUTPUT_PPTX_ENG}")

    # Copy to Thai path
    try:
        shutil.copy2(OUTPUT_PPTX_ENG, OUTPUT_PPTX_THAI)
        print(f"Saved copy: {OUTPUT_PPTX_THAI}")
    except Exception as e:
        print(f"Copy error: {e}")


if __name__ == "__main__":
    generate_presentation()
