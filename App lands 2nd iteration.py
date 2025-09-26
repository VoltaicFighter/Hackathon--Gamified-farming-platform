# gaming_food_platform.py
import flet as ft
import mysql.connector
import pyttsx3
import os
import flet_audio
import json
from flet_audio import Audio

# ---------- 1. CONFIGURATION ----------
LANGUAGES = {'en': 'English', 'ta': 'தமிழ்', 'hi': 'हिंदी'}
DB_CONFIG = {
    "host": "localhost",
    "user": "db_user",
    "password": "root",
    "database": "farming_db",
}
AUDIO_PATH = "audio_files"  # base directory for TTS audio
os.makedirs(AUDIO_PATH, exist_ok=True)

# ---------- 2. LOCALIZATION -----------
# Example translation dict; expand as needed.
STRINGS = {
    'en': {
        'login': "Login",
        'register': "Register",
        'phone': "Phone Number",
        'pin': "PIN",
        'submit': "Submit",
        'welcome': "Welcome!",
        'choose_lang': "Choose Language",
        'literacy_test': "Technical Literacy Test",
        'swipe_test': "Swipe Left to Continue",
        'tap_test': "Tap the Button",
        'nav_test': "Navigate to Next",
        'cam_test': "Take a Photo",
        'tasks': "Daily Tasks",
        # ... other keys
    },
    'ta': {
        'login': "உள்நுழைக",
        'register': "பதிவு செய்யவும்",
        'phone': "தொலைபேசி எண்",
        'pin': "பின்",
        'submit': "சமர்ப்பிக்க",
        'welcome': "வரவேற்கின்றேன்!",
        'choose_lang': "மொழியைத் தேர்ந்தெடுக்கவும்",
        'literacy_test': "தொழில்நுட்ப அறிவு பரிசோதனை",
        'swipe_test': "மறுதிசை இழுக்கவும்",
        'tap_test': "பட்டனை அழுத்தவும்",
        'nav_test': "அடுத்ததாக செல்லவும்",
        'cam_test': "புகைப்படம் எடுக்கவும்",
        'tasks': "தினசரி பணிகள்",
    },
    'hi': {
        'login': "लॉगिन करें",
        'register': "पंजीकरण करें",
        'phone': "फ़ोन नंबर",
        'pin': "पिन",
        'submit': "जमा करें",
        'welcome': "स्वागत है!",
        'choose_lang': "भाषा चुनें",
        'literacy_test': "तकनीकी साक्षरता परीक्षण",
        'swipe_test': "आगे बढ़ने के लिए स्वाइप करें",
        'tap_test': "बटन पर टैप करें",
        'nav_test': "आगे नेविगेट करें",
        'cam_test': "फोटो लें",
        'tasks': "दैनिक कार्य",
    }
}
app_language = 'en'  # default; will be set at runtime

def t(key):
    return STRINGS[app_language].get(key, key)

# ---------- 3. TEXT-TO-SPEECH ----------
engine = pyttsx3.init()
def tts(text, lang_code):
    """Generate or fetch TTS audio file for given text/language."""
    safe_key = f"{lang_code}_{abs(hash(text))}.wav"
    fp = os.path.join(AUDIO_PATH, safe_key)
    if not os.path.exists(fp):
        engine.setProperty('voice', lang_code)
        engine.save_to_file(text, fp)
        engine.runAndWait()
    return fp

# ---------- 4. DATABASE ----------
def db_connect():
    return mysql.connector.connect(**DB_CONFIG)

def db_get_farmer(phone):
    with db_connect() as db:
        c = db.cursor(dictionary=True)
        c.execute("SELECT * FROM farmers WHERE phone=%s", (phone,))
        return c.fetchone()

def db_register_farmer(phone, pin_hash, lang, lit_level):
    with db_connect() as db:
        c = db.cursor()
        c.execute("INSERT INTO farmers (phone, pin_hash, language, literacy_lvl) VALUES (%s, %s, %s, %s)",
                  (phone, pin_hash, lang, lit_level))
        db.commit()

# ---------- 5. PIN HASHING ----------
import bcrypt
def hash_pin(pin):
    return bcrypt.hashpw(pin.encode(), bcrypt.gensalt()).decode()

def check_pin(pin, pin_hash):
    return bcrypt.checkpw(pin.encode(), pin_hash.encode())

# ---------- 6. AUDIO CONTROL ----------
audio_controls = {}
def play_audio(page, text, lang_code):
    # Generate or fetch audio and play
    path = tts(text, lang_code)
    if lang_code not in audio_controls:
        audio_controls[lang_code] = Audio(src=path, volume=1)
        page.overlay.append(audio_controls[lang_code])
    audio_controls[lang_code].src = path
    audio_controls[lang_code].update()
    audio_controls[lang_code].play()

# ---------- 7. UI/UX ADAPTATION ----------
def get_ui_params(lit_level):
    if lit_level == 0:  # Low
        return {'button_size': 50, 'icon_size': 42, 'use_voice': True,
                'layout':'linear', 'help':True}
    elif lit_level == 1:  # Medium
        return {'button_size': 42, 'icon_size': 32, 'use_voice': False,
                'layout':'grid', 'help':False}
    else:  # High
        return {'button_size': 32, 'icon_size': 22, 'use_voice': False,
                'layout':'advanced', 'help':False}

# ---------- 8. IMAGE RECOGNITION (Backend API Placeholder) ----------
import requests
def recognize_image(img_bytes):
    # Replace with your REST API endpoint for the ML model
    url = 'http://localhost:8000/crop-recognize'
    files = {'file': ('image.jpg', img_bytes)}
    r = requests.post(url, files=files)
    return r.json()  # {'crop_type': 'rice', 'status': 'healthy', ...}

# ---------- 9. MAIN APP ----------
def main(page: ft.Page):
    page.title = "Gaming Food Platform for Sustainable Agriculture"
    # -------- LANGUAGE SELECTION -----------
    def choose_language(e=None):
        def set_lang(ev):
            global app_language
            app_language = ev.control.data
            page.clean()
            login_screen()
        page.clean()
        page.add(ft.Text("🌱 " + t("choose_lang"), size=30))
        for code, name in LANGUAGES.items():
            page.add(ft.ElevatedButton(name, data=code, on_click=set_lang, width=200))

    # --------- LOGIN / REGISTER ------------
    def login_screen(msg=""):
        page.clean()
        phone_field = ft.TextField(label=t("phone"), width=250)
        pin_field = ft.TextField(label=t("pin"), password=True, can_reveal_password=True, width=250)
        msg_text = ft.Text(msg, color="red") if msg else None
        def on_login(e):
            farmer = db_get_farmer(phone_field.value)
            if farmer and check_pin(pin_field.value, farmer['pin_hash']):
                # Store local session, route to literacy/adaptive UI
                literacy_level = farmer['literacy_lvl']
                page.client_storage.set("user_phone", farmer['phone'])
                page.client_storage.set("literacy_lvl", literacy_level)
                daily_tasks_screen(literacy_level)
            else:
                login_screen(msg="Wrong credentials. Try again.")

        page.add(ft.Text("🌾 " + t("login"), size=24))
        if msg_text: page.add(msg_text)
        page.add(phone_field, pin_field)
        page.add(ft.ElevatedButton(t("submit"), on_click=on_login, width=200))
        page.add(ft.TextButton(t("register"), on_click=lambda e: registration_screen()))

    def registration_screen():
        page.clean()
        phone_field = ft.TextField(label=t("phone"), width=250)
        pin_field = ft.TextField(label=t("pin"), password=True, can_reveal_password=True, width=250)
        lang_field = ft.Dropdown(label=t("choose_lang"), options=[ft.dropdown.Option(v, key=k) for k,v in LANGUAGES.items()])
        def on_register(e):
            pin_hash = hash_pin(pin_field.value)
            db_register_farmer(phone_field.value, pin_hash, lang_field.value, 0)  # Assume low literacy; will update after test
            login_screen("Registered! Please login.")
        page.add(ft.Text("🌱 " + t("register"), size=24))
        page.add(phone_field, pin_field, lang_field)
        page.add(ft.ElevatedButton(t("submit"), on_click=on_register, width=200))
        page.add(ft.TextButton(t("login"), on_click=lambda e: login_screen()))

    # --------- TECHNICAL LITERACY TEST -------------
    def literacy_test_screen():
        page.clean()
        lit_scores = [0,0,0,0]  # [swipe, tap, nav, cam]
        current_test = [0]  # index; boxed to be mutable

        def test_swipe():
            page.clean()
            page.add(ft.Text(t("swipe_test"), size=18))
            b = ft.ElevatedButton("⬅️", width=100, height=50)
            def on_swipe(ev):  # You may use on_change for certain gestures, as per Flet's gesture support
                lit_scores[0] = 1
                test_tap()
            b.on_click = on_swipe
            page.add(b)
            if get_ui_params(0)["use_voice"]:
                play_audio(page, t("swipe_test"), app_language)
        def test_tap():
            page.clean()
            page.add(ft.Text(t("tap_test"), size=18))
            b = ft.ElevatedButton("🖱️", width=100, height=50)
            def on_tap(ev):
                lit_scores[1] = 1
                test_nav()
            b.on_click = on_tap
            page.add(b)
            if get_ui_params(0)["use_voice"]:
                play_audio(page, t("tap_test"), app_language)
        def test_nav():
            page.clean()
            page.add(ft.Text(t("nav_test"), size=18))
            b = ft.ElevatedButton("➡️", width=100, height=50)
            def on_nav(ev):
                lit_scores[2] = 1
                test_cam()
            b.on_click = on_nav
            page.add(b)
            if get_ui_params(0)["use_voice"]:
                play_audio(page, t("nav_test"), app_language)
        def test_cam():
            page.clean()
            page.add(ft.Text(t("cam_test"), size=18))
            b = ft.IconButton(icon=ft.icons.CAMERA_ALT, icon_size=50)
            def on_cam(ev):
                lit_scores[3] = 1
                show_result()
            b.on_click = on_cam
            page.add(b)
            if get_ui_params(0)["use_voice"]:
                play_audio(page, t("cam_test"), app_language)
        def show_result():
            score = sum(lit_scores)
            if score < 2:
                lvl = 0  # Low
            elif score < 4:
                lvl = 1  # Med
            else:
                lvl = 2  # High
            # Update farmer DB
            phone = page.client_storage.get("user_phone")
            with db_connect() as db:
                c = db.cursor()
                c.execute("UPDATE farmers SET literacy_lvl=%s WHERE phone=%s", (lvl, phone))
                db.commit()
            daily_tasks_screen(lvl)
        test_swipe()

    # --------- DAILY TASKS + GAMIFICATION -----------
    def daily_tasks_screen(lit_level):
        page.clean()
        ui = get_ui_params(lit_level)
        page.add(ft.Text("🌱 " + t("tasks"), size=24))
        # Sample tasks (should pull from DB or dynamic schedule)
        tasks = [
            {"id": 1, "desc": "Water the paddy field", "points": 10},
            {"id": 2, "desc": "Take a photo of blooming tomatoes", "points": 15}
        ]
        done = []
        # Points, badges; pull actual scores from DB in production

        for task in tasks:
            task_text = task['desc']
            btn = ft.ElevatedButton(task_text,
                                    width=ui["button_size"]*5, height=ui["button_size"]*1.4,
                                    on_click=lambda e, t=task: task_detail_screen(t, lit_level),
                                    tooltip=f"{task['points']} points")
            if ui["use_voice"]:
                btn.on_hover = lambda e, txt=task_text: play_audio(page, txt, app_language)
            page.add(btn)

        # Leaderboard and rewards
        page.add(ft.Text("🏆 Leaderboard: (Coming soon)", size=18))

    # --------- TASK DETAIL + IMAGE RECOGNITION -------
    def task_detail_screen(task, lit_level):
        page.clean()
        ui = get_ui_params(lit_level)
        page.add(ft.Text("🔎 Task: "+task["desc"], size=22))
        def on_upload(e):
            uploaded_image = e.files[0]
            with open(uploaded_image.path, "rb") as f:
                img_bytes = f.read()
            result = recognize_image(img_bytes)  # Backend ML call
            res_text = f"Crop: {result.get('crop_type', 'Unknown')}, Status: {result.get('status', 'Unknown')}"
            page.snack_bar = ft.SnackBar(content=ft.Text(res_text))
            page.snack_bar.open = True
            page.update()
            # Gamification update
            # TODO: Save completion, update rewards/points/DB
            page.add(ft.Text(f"You earned {task['points']} points!", size=18))
        page.add(ft.FilePicker(on_result=on_upload, file_type=ft.FilePickerFileType.IMAGE))
        page.add(ft.TextButton("⬅️ Back", on_click=lambda e: daily_tasks_screen(lit_level)))

    # --------- USER FLOW ----------
    choose_language()

ft.run(main)