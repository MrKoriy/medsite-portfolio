import os
import math
import subprocess
from PIL import Image, ImageDraw, ImageFont

ASSETS_DIR = "/root/coding/medsite/frontend/assets/world"
os.makedirs(ASSETS_DIR, exist_ok=True)

W, H = 1920, 1080

def get_fonts():
    try:
        f_hero = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 44)
        f_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
        f_badge = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
        f_mono = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 15)
        return f_hero, f_sub, f_badge, f_mono
    except Exception:
        f = ImageFont.load_default()
        return f, f, f, f

f_hero, f_sub, f_badge, f_mono = get_fonts()

scenes_data = [
    {
        "id": "triage",
        "num": "01",
        "badge": "ВХОДНАЯ ГРУППА И ТРИАЖ",
        "title": "Приёмное отделение",
        "desc": "Бережная маршрутизация за 3 минуты. Врач приёмного отделения оценивает симптомы и направляет к профильному специалисту без очередей.",
        "accent": "#11382d",
        "accent_light": "#e3ede9",
        "items": ["Электронная регистрация", "Экспресс-триаж", "Индивидуальный координатор"],
        "icon": "cross"
    },
    {
        "id": "diagnostics",
        "num": "02",
        "badge": "ВЫСОКОТОЧНОЕ ОБОРУДОВАНИЕ",
        "title": "Лаборатория и МРТ",
        "desc": "Цифровой томограф 1.5 Тесла с пониженным уровнем шума. Автоматизированные гематологические анализаторы с выдачей результатов день в день.",
        "accent": "#0e4a42",
        "accent_light": "#d8ebe7",
        "items": ["МРТ Siemens Magnetom", "Срочные C-реактивные тесты", "Цифровой архив снимков"],
        "icon": "mri"
    },
    {
        "id": "consulting",
        "num": "03",
        "badge": "ДОКАЗАТЕЛЬНАЯ ПРАКТИКА",
        "title": "Консультативное крыло",
        "desc": "Приёмы длительностью от 30 до 60 минут. Никаких гомеопатических препаратов и назначений 'на всякий случай' — только международные гайдлайны.",
        "accent": "#1a4731",
        "accent_light": "#e4eee7",
        "items": ["Терапия и Кардиология", "Неврология и Эндокринология", "Второе экспертное мнение"],
        "icon": "stethoscope"
    },
    {
        "id": "day_hospital",
        "num": "04",
        "badge": "МАЛОИНВАЗИВНЫЙ СТАЦИОНАР",
        "title": "Дневной стационар",
        "desc": "Светлые индивидуальные палаты с постоянным кардиомониторингом. Восстановительная инфузионная терапия под непрерывным контролем врача.",
        "accent": "#1e3d36",
        "accent_light": "#dceae5",
        "items": ["Персональный мониторинг", "Эргономичные кресла-кровати", "Контроль гемодинамики"],
        "icon": "bed"
    },
    {
        "id": "digital_care",
        "num": "05",
        "badge": "ЦИФРОВАЯ ЭКОСИСТЕМА",
        "title": "Онлайн-запись и связь",
        "desc": "Электронная медицинская карта в вашем телефоне. Чат с лечащим врачом после приёма и напоминания о контрольных осмотрах.",
        "accent": "#11382d",
        "accent_light": "#e2ece7",
        "items": ["Запись без звонков", "Безопасное хранение данных", "Поддержка 24/7"],
        "icon": "app"
    }
]

def render_scene_still(data, out_path):
    img = Image.new("RGBA", (W, H), "#fafaf8")
    d = ImageDraw.Draw(img)

    # Subtle grid lines (Swiss clinical architecture)
    for x in range(0, W, 120):
        d.line([(x, 0), (x, H)], fill="#f0f1ee", width=1)
    for y in range(0, H, 120):
        d.line([(0, y), (W, y)], fill="#f0f1ee", width=1)

    # Architectural room base (isometric perspective floor plate)
    # Right side 3D diorama platform
    cx, cy = 1260, 560
    base_w, base_h = 920, 540
    
    # Shadow underneath
    d.polygon([
        (cx, cy + 240),
        (cx + 460, cy + 30),
        (cx, cy - 180),
        (cx - 460, cy + 30)
    ], fill="#eaeae6")

    # Platform slab top
    d.polygon([
        (cx, cy + 210),
        (cx + 450, cy + 10),
        (cx, cy - 190),
        (cx - 450, cy + 10)
    ], fill="#ffffff", outline="#d7ded9", width=2)

    # Walls / partitions (Swiss clean glass & minimalist white panels)
    # Back-left wall
    d.polygon([
        (cx - 450, cy + 10),
        (cx, cy - 190),
        (cx, cy - 430),
        (cx - 450, cy - 230)
    ], fill="#f4f6f4", outline="#cbd5ce", width=2)

    # Back-right wall
    d.polygon([
        (cx, cy - 190),
        (cx + 450, cy + 10),
        (cx + 450, cy - 230),
        (cx, cy - 430)
    ], fill="#eef2ef", outline="#cbd5ce", width=2)

    # Accent decorative strip along top of wall
    d.polygon([
        (cx - 450, cy - 230),
        (cx, cy - 430),
        (cx, cy - 418),
        (cx - 450, cy - 218)
    ], fill=data["accent"])
    
    d.polygon([
        (cx, cy - 430),
        (cx + 450, cy - 230),
        (cx + 450, cy - 218),
        (cx, cy - 418)
    ], fill=data["accent"])

    # Scene specific clinical props in isometric
    prop_accent = data["accent"]
    
    if data["icon"] == "cross":
        # Triage reception desk & digital board
        # Reception counter
        d.polygon([(cx - 150, cy + 60), (cx + 100, cy - 50), (cx + 100, cy + 40), (cx - 150, cy + 150)], fill="#ffffff", outline="#cbd5ce", width=2)
        d.polygon([(cx - 150, cy + 60), (cx + 100, cy - 50), (cx + 60, cy - 70), (cx - 190, cy + 40)], fill="#e3ede9", outline="#cbd5ce", width=2)
        # Medical cross emblem on counter
        d.rectangle([cx - 40, cy + 85, cx - 20, cy + 125], fill=prop_accent)
        d.rectangle([cx - 50, cy + 95, cx - 10, cy + 115], fill=prop_accent)
        # Standing display monitor
        d.polygon([(cx + 160, cy - 120), (cx + 260, cy - 75), (cx + 260, cy + 30), (cx + 160, cy - 15)], fill="#121517")
        d.text((cx + 175, cy - 80), "TRIAGE\nSTATUS\nNORMAL", font=f_mono, fill="#2dd4bf")

    elif data["icon"] == "mri":
        # MRI scanner circular bore in 3D
        d.ellipse([cx - 120, cy - 180, cx + 180, cy + 100], fill="#ffffff", outline="#cbd5ce", width=8)
        d.ellipse([cx - 80, cy - 140, cx + 140, cy + 60], fill="#11382d", outline="#2dd4bf", width=4)
        # Patient couch gliding into scanner
        d.polygon([(cx - 280, cy + 120), (cx - 20, cy - 10), (cx + 40, cy + 15), (cx - 220, cy + 145)], fill="#eef3f0", outline="#b2c4ba", width=2)
        # Control console
        d.polygon([(cx + 220, cy - 20), (cx + 310, cy + 20), (cx + 310, cy + 90), (cx + 220, cy + 50)], fill="#ffffff", outline="#cbd5ce", width=2)

    elif data["icon"] == "stethoscope":
        # Doctor consultation desk with monitors
        d.polygon([(cx - 160, cy + 20), (cx + 120, cy - 100), (cx + 160, cy - 80), (cx - 120, cy + 40)], fill="#ffffff", outline="#cbd5ce", width=2)
        d.polygon([(cx - 160, cy + 20), (cx + 120, cy - 100), (cx + 120, cy - 30), (cx - 160, cy + 90)], fill="#f4f6f4", outline="#cbd5ce", width=2)
        # Dual monitors
        d.polygon([(cx - 60, cy - 100), (cx + 20, cy - 135), (cx + 20, cy - 65), (cx - 60, cy - 30)], fill="#121517")
        d.polygon([(cx + 30, cy - 140), (cx + 110, cy - 175), (cx + 110, cy - 105), (cx + 30, cy - 70)], fill="#121517")
        d.text((cx - 45, cy - 80), "EHR 2026", font=f_mono, fill="#a7f3d0")
        # Consultation chairs
        d.ellipse([cx - 190, cy + 80, cx - 130, cy + 130], fill="#3e6b5c")
        d.ellipse([cx + 50, cy + 10, cx + 110, cy + 60], fill="#11382d")

    elif data["icon"] == "bed":
        # Day hospital modern recovery bed
        d.polygon([(cx - 160, cy + 20), (cx + 80, cy - 80), (cx + 140, cy - 50), (cx - 100, cy + 50)], fill="#ffffff", outline="#b2c4ba", width=3)
        d.polygon([(cx - 160, cy + 20), (cx - 100, cy + 50), (cx - 100, cy + 110), (cx - 160, cy + 80)], fill="#3e6b5c")
        # Head pillow
        d.polygon([(cx + 30, cy - 70), (cx + 80, cy - 90), (cx + 120, cy - 70), (cx + 70, cy - 50)], fill="#d8ebe7")
        # Infusion monitor pole
        d.line([(cx + 180, cy - 160), (cx + 180, cy + 40)], fill="#94a3b8", width=4)
        d.ellipse([cx + 160, cy - 180, cx + 200, cy - 140], fill="#11382d")

    elif data["icon"] == "app":
        # Digital smart kiosk and mobile sync hub
        d.polygon([(cx - 80, cy - 160), (cx + 40, cy - 210), (cx + 40, cy + 80), (cx - 80, cy + 130)], fill="#11382d", outline="#2dd4bf", width=2)
        d.text((cx - 65, cy - 120), "MEDSPHERE\nDIGITAL\nID: 7701\n\nONLINE", font=f_mono, fill="#ffffff")
        # Floating badge / card
        d.polygon([(cx + 100, cy - 50), (cx + 260, cy - 120), (cx + 260, cy - 40), (cx + 100, cy + 30)], fill="#ffffff", outline="#11382d", width=2)
        d.text((cx + 120, cy - 75), "CONFIRMED", font=f_mono, fill="#11382d")

    # Save still
    img.convert("RGB").save(out_path, quality=95)
    print(f"Rendered still: {out_path}")

# Render all 5 stills
for item in scenes_data:
    still_path = os.path.join(ASSETS_DIR, f"{item['id']}.webp")
    render_scene_still(item, still_path)

# Generate smooth 8s MP4 camera glide clips using ffmpeg with GOP=8 (-g 8)
for i, item in enumerate(scenes_data):
    still_file = os.path.join(ASSETS_DIR, f"{item['id']}.webp")
    video_file = os.path.join(ASSETS_DIR, f"{item['id']}.mp4")
    
    # Camera motion formula: subtle smooth zoom and pan
    # zoom from 1.0 to 1.08 over 8 seconds @ 24fps
    # slow pan towards the focal center of the 3D diorama
    zoom_expr = "min(zoom+0.0004,1.08)"
    x_expr = "iw/2-(iw/zoom/2)+40*(on/192)"
    y_expr = "ih/2-(ih/zoom/2)+20*(on/192)"
    
    cmd = [
        "ffmpeg", "-y", "-loop", "1", "-i", still_file,
        "-vf", f"zoompan=z='{zoom_expr}':x='{x_expr}':y='{y_expr}':d=192:s=1920x1080:fps=24,unsharp=5:5:0.8:5:5:0.0",
        "-t", "8", "-an", "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-pix_fmt", "yuv420p", "-g", "8", "-keyint_min", "8", "-sc_threshold", "0",
        "-movflags", "+faststart", video_file
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(f"Generated scrub clip: {video_file}")

print("All assets generated successfully!")
