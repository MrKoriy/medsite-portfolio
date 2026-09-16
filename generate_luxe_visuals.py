import os
import math
import subprocess
from PIL import Image, ImageDraw, ImageFont

ASSETS_DIR = "/root/coding/medsite/frontend/assets/world"
os.makedirs(ASSETS_DIR, exist_ok=True)

W, H = 1920, 1080

def get_fonts():
    try:
        f_num = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
        f_hero = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
        f_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
        f_badge = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 15)
        f_mono = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 14)
        return f_num, f_hero, f_sub, f_badge, f_mono
    except Exception:
        f = ImageFont.load_default()
        return f, f, f, f, f

f_num, f_hero, f_sub, f_badge, f_mono = get_fonts()

scenes = [
    {
        "id": "triage",
        "num": "01",
        "badge": "ВХОДНАЯ ГРУППА · ТРИАЖ",
        "title": "Приёмное отделение и маршрутизация",
        "lead": "Экспресс-оценка состояния пациента за 3 минуты. Персональный медицинский координатор организует приём без ожидания.",
        "metrics": [("3 мин", "время триажа"), ("100%", "цифровой учёт"), ("Пн–Сб", "08:30–20:30")],
        "accent": "#10b981",
        "accent_dim": "rgba(16, 185, 129, 0.15)",
        "tag": "EHR DIRECT // 7701",
        "type": "triage"
    },
    {
        "id": "diagnostics",
        "num": "02",
        "badge": "ВЫСОКОТОЧНЫЙ СКРИНИНГ",
        "title": "Лабораторный комплекс и МРТ",
        "lead": "Цифровой томограф Siemens Magnetom 1.5 Тесла с пониженным уровнем шума. Экспресс-панели крови с выдачей день в день.",
        "metrics": [("1.5 Тл", "мощность МРТ"), ("20 мин", "готовность C-РБ"), ("DICOM", "облачный архив")],
        "accent": "#06b6d4",
        "accent_dim": "rgba(6, 182, 212, 0.15)",
        "tag": "DIAGNOSTICS HUB // SCAN",
        "type": "mri"
    },
    {
        "id": "consulting",
        "num": "03",
        "badge": "МЕЖДУНАРОДНЫЕ СТАНДАРТЫ",
        "title": "Врачи доказательной практики",
        "lead": "Консультации от 30 до 60 минут. Никаких гомеопатических назначений, фуфломицинов и лишних анализов — только верифицированная медицина.",
        "metrics": [("30–60 мин", "время приёма"), ("15+ лет", "опыт врачей"), ("0%", "избыточных чеков")],
        "accent": "#3b82f6",
        "accent_dim": "rgba(59, 130, 246, 0.15)",
        "tag": "EVIDENCE-BASED // CLINICAL",
        "type": "doctor"
    },
    {
        "id": "day_hospital",
        "num": "04",
        "badge": "МАЛОИНВАЗИВНЫЙ СТАЦИОНАР",
        "title": "Дневной стационар и реабилитация",
        "lead": "Светлые индивидуальные палаты с постоянным кардиомониторингом. Восстановительная инфузионная терапия под непрерывным контролем врача.",
        "metrics": [("100%", "контроль гемодинамики"), ("1 палата", "1 пациент"), ("24/7", "мониторинг")],
        "accent": "#a855f7",
        "accent_dim": "rgba(168, 85, 247, 0.15)",
        "tag": "RECOVERY // INPATIENT",
        "type": "hospital"
    },
    {
        "id": "digital_care",
        "num": "05",
        "badge": "ЦИФРОВАЯ СВЯЗЬ И ЗАПИСЬ",
        "title": "Онлайн-запись и личный кабинет",
        "lead": "Электронная медицинская карта в вашем телефоне. Прямой чат с лечащим врачом после приёма и напоминания о контрольных осмотрах.",
        "metrics": [("24/7", "онлайн-запись"), ("0 звонков", "всё в приложении"), ("SSL", "защита данных")],
        "accent": "#10b981",
        "accent_dim": "rgba(16, 185, 129, 0.15)",
        "tag": "TELEMED // BOOKING",
        "type": "app"
    }
]

def render_luxe_scene(data, out_path):
    # Deep graphite canvas
    img = Image.new("RGBA", (W, H), "#080c0e")
    d = ImageDraw.Draw(img)

    # Subtle technical background grid
    grid_color = "#0e151a"
    for x in range(0, W, 80):
        d.line([(x, 0), (x, H)], fill=grid_color, width=1)
    for y in range(0, H, 80):
        d.line([(0, y), (W, y)], fill=grid_color, width=1)

    # Ambient radial glow around center right
    accent_hex = data["accent"]
    
    # Large frosted glass card in 3D right side
    card_x1, card_y1 = 880, 180
    card_x2, card_y2 = 1760, 900
    
    # Card outer border & soft shadow
    d.rounded_rectangle([card_x1 - 2, card_y1 - 2, card_x2 + 2, card_y2 + 2], radius=16, outline=accent_hex, width=1)
    d.rounded_rectangle([card_x1, card_y1, card_x2, card_y2], radius=16, fill="#0f161c", outline="#1c2730", width=1)

    # Header of the card
    d.rounded_rectangle([card_x1, card_y1, card_x2, card_y1 + 70], radius=16, fill="#131c24")
    d.rectangle([card_x1, card_y1 + 50, card_x2, card_y1 + 70], fill="#131c24")
    d.line([(card_x1, card_y1 + 70), (card_x2, card_y1 + 70)], fill="#1f2c38", width=1)

    # Badge on card header
    d.text((card_x1 + 32, card_y1 + 26), data["badge"], font=f_badge, fill=accent_hex)
    d.text((card_x2 - 240, card_y1 + 26), data["tag"], font=f_mono, fill="#64748b")

    # Big holographic watermark number
    d.text((card_x2 - 190, card_y1 + 90), data["num"], font=f_num, fill="#131e26")

    # Title & Lead inside card
    d.text((card_x1 + 32, card_y1 + 105), data["title"], font=f_hero, fill="#f8fafc")
    
    # Word wrap lead
    words = data["lead"].split()
    lines, cur = [], []
    for w in words:
        cur.append(w)
        if len(" ".join(cur)) > 48:
            lines.append(" ".join(cur))
            cur = []
    if cur:
        lines.append(" ".join(cur))

    text_y = card_y1 + 175
    for l in lines:
        d.text((card_x1 + 32, text_y), l, font=f_sub, fill="#94a3b8")
        text_y += 32

    # Visual high-tech telemetry / waveform / scan visualization
    vis_x1, vis_y1 = card_x1 + 32, card_y1 + 340
    vis_x2, vis_y2 = card_x2 - 32, card_y1 + 540
    d.rounded_rectangle([vis_x1, vis_y1, vis_x2, vis_y2], radius=12, fill="#0b1014", outline="#1c2832", width=1)

    # Waveform or graph
    if data["type"] == "triage" or data["type"] == "hospital":
        # Realistic ECG / Vital monitor wave
        d.text((vis_x1 + 20, vis_y1 + 16), "PULSE RATE // VITAL TELEMETRY", font=f_mono, fill="#64748b")
        d.text((vis_x2 - 120, vis_y1 + 16), "72 BPM · OK", font=f_mono, fill=accent_hex)
        pts = []
        cy = vis_y1 + 110
        step = 6
        x_curr = vis_x1 + 20
        idx = 0
        while x_curr < vis_x2 - 20:
            if idx % 18 == 8:
                pts.append((x_curr, cy - 8))
            elif idx % 18 == 9:
                pts.append((x_curr + 4, cy - 45))
            elif idx % 18 == 10:
                pts.append((x_curr + 8, cy + 25))
            elif idx % 18 == 11:
                pts.append((x_curr + 12, cy - 10))
            else:
                pts.append((x_curr, cy + math.sin(idx * 0.5) * 4))
            x_curr += step
            idx += 1
        d.line(pts, fill=accent_hex, width=2)

    elif data["type"] == "mri":
        # MRI Ring / Cross-section representation
        d.text((vis_x1 + 20, vis_y1 + 16), "RESONANCE SCANNER 1.5T // CALIBRATED", font=f_mono, fill="#64748b")
        d.text((vis_x2 - 140, vis_y1 + 16), "NOISE -40dB · ACTIVE", font=f_mono, fill=accent_hex)
        cx_mri = (vis_x1 + vis_x2) // 2
        cy_mri = vis_y1 + 110
        for r in range(20, 80, 15):
            d.ellipse([cx_mri - r, cy_mri - r // 2, cx_mri + r, cy_mri + r // 2], outline="#1e2d38", width=2)
        d.ellipse([cx_mri - 50, cy_mri - 25, cx_mri + 50, cy_mri + 25], outline=accent_hex, width=2)

    elif data["type"] == "doctor":
        # Clinical evidence checklist
        d.text((vis_x1 + 20, vis_y1 + 16), "PROTOCOL COMPLIANCE // COCHRANE & NICE", font=f_mono, fill="#64748b")
        d.text((vis_x2 - 120, vis_y1 + 16), "VERIFIED", font=f_mono, fill=accent_hex)
        d.text((vis_x1 + 30, vis_y1 + 60), "✔ Первичный осмотр: 45 минут с детальным анамнезом", font=f_sub, fill="#cbd5e1")
        d.text((vis_x1 + 30, vis_y1 + 100), "✔ Исключение неэффективных коммерческих схем", font=f_sub, fill="#cbd5e1")
        d.text((vis_x1 + 30, vis_y1 + 140), "✔ Прозрачный план лечения с понятными целями", font=f_sub, fill="#cbd5e1")

    elif data["type"] == "app":
        # Digital pass & booking slot
        d.text((vis_x1 + 20, vis_y1 + 16), "SECURE PATIENT ACCESS // TLS 1.3", font=f_mono, fill="#64748b")
        d.text((vis_x2 - 120, vis_y1 + 16), "ONLINE", font=f_mono, fill=accent_hex)
        d.text((vis_x1 + 30, vis_y1 + 65), "ЭЛЕКТРОННАЯ ЗАПИСЬ НА ПРИЁМ", font=f_hero, fill="#f8fafc")
        d.text((vis_x1 + 30, vis_y1 + 115), "Свободные окна к врачам сегодня: 14:00, 16:30, 18:00", font=f_sub, fill="#38bdf8")
        d.text((vis_x1 + 30, vis_y1 + 150), "SMS и push-уведомление без звонков из колл-центра", font=f_mono, fill="#94a3b8")

    # Metrics row along bottom of card
    mx = card_x1 + 32
    col_w = (card_x2 - card_x1 - 64) // 3
    d.line([(card_x1 + 32, card_y1 + 580), (card_x2 - 32, card_y1 + 580)], fill="#1f2c38", width=1)
    
    for val, lbl in data["metrics"]:
        d.text((mx, card_y1 + 605), val, font=f_hero, fill=accent_hex)
        d.text((mx, card_y1 + 655), lbl, font=f_sub, fill="#64748b")
        mx += col_w

    img.convert("RGB").save(out_path, quality=95)
    print(f"Rendered luxe still: {out_path}")

for item in scenes:
    still_file = os.path.join(ASSETS_DIR, f"{item['id']}.webp")
    render_luxe_scene(item, still_file)

# Generate smooth cinematic 1080p scrub video clips
for item in scenes:
    still_file = os.path.join(ASSETS_DIR, f"{item['id']}.webp")
    video_file = os.path.join(ASSETS_DIR, f"{item['id']}.mp4")

    # Gentle high-tech slow camera glide
    zoom_expr = "min(zoom+0.0003,1.06)"
    x_expr = "iw/2-(iw/zoom/2)+30*(on/192)"
    y_expr = "ih/2-(ih/zoom/2)+15*(on/192)"

    cmd = [
        "ffmpeg", "-y", "-loop", "1", "-i", still_file,
        "-vf", f"zoompan=z='{zoom_expr}':x='{x_expr}':y='{y_expr}':d=192:s=1920x1080:fps=24,unsharp=5:5:0.8:5:5:0.0",
        "-t", "8", "-an", "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-pix_fmt", "yuv420p", "-g", "8", "-keyint_min", "8", "-sc_threshold", "0",
        "-movflags", "+faststart", video_file
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(f"Generated luxe video: {video_file}")

print("All luxe assets created!")
