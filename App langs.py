import flet as ft
import mysql.connector
from flet_audio import Audio
from flet_audiorecorder import AudioRecorder
from gtts import gTTS
import io

try:
    import tensorflow as tf
    from tensorflow.keras.preprocessing import image as keras_image
    from tensorflow.keras.applications import mobilenet_v2
except ImportError:
    tf = None
from PIL import Image

# Manual translation dictionaries (English, Tamil, Hindi)
strings = {
    "en": {
        "login": "Login",
        "enter_phone": "Enter phone number",
        "enter_pin": "Enter PIN",
        "daily_task": "Today's Task:",
        "camera_upload": "Upload image",
        "task_completed": "Task completed!"
    },
    "ta": {
        "login": "உள்நுழைய",
        "enter_phone": "தொலைபேசி எண்",
        "enter_pin": "PIN கொடுக்கவும்",
        "daily_task": "இன்றைய பணி:",
        "camera_upload": "படத்தைப் பதிவேற்றவும்",
        "task_completed": "பணி முடிந்தது!"
    },
    "hi": {
        "login": "लॉगिन",
        "enter_phone": "फ़ोन नंबर",
        "enter_pin": "PIN दर्ज करें",
        "daily_task": "आज का कार्य:",
        "camera_upload": "छवि अपलोड करें",
        "task_completed": "कार्य पूर्ण!"
    }
}


def main(page: ft.Page):
    page.title = "Gaming Food Platform"
    page.vertical_alignment = ft.MainAxisAlignment.START

    # Setup locale support for Tamil and Hindi
    page.locale_configuration = ft.LocaleConfiguration(
        supported_locales=[ft.Locale("en"), ft.Locale("ta"), ft.Locale("hi")],
        current_locale=ft.Locale("en"),
    )

    # Connect to MySQL (requires mysql-connector-python)
    conn = mysql.connector.connect(
        user='your_db_user', password='your_db_password',
        host='localhost', database='farmers_db'
    )
    cursor = conn.cursor()
    # Create tables if not exist
    cursor.execute(""" CREATE TABLE IF NOT EXISTS farmers (  phone VARCHAR(15) PRIMARY KEY,     pin VARCHAR(10),        literacy_level INT,    score INT DEFAULT 0)   """)
    cursor.execute("""   CREATE TABLE IF NOT EXISTS tasks (id INT AUTO_INCREMENT PRIMARY KEY,      phone VARCHAR(15),        task_name VARCHAR(100),     image_path VARCHAR(255),       recognized VARCHAR(100),       FOREIGN KEY (phone) REFERENCES farmers(phone)   )  """)
    conn.commit()

    user_phone = ""
    user_lang = "en"
    tech_points = 0

    # Setup audio recorder for speech input (not fully implemented here)
    recorder = AudioRecorder()
    page.overlay.append(recorder)

    # Function to play text via TTS
    def speak(text):
        lang_code = {"en": "en", "ta": "ta", "hi": "hi"}[user_lang]
        tts = gTTS(text=text, lang=lang_code)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        audio = Audio(src=fp.read(), autoplay=True)
        page.overlay.append(audio)

    # Load image recognition model (MobileNet) if possible
    if tf:
        try:
            model = mobilenet_v2.MobileNetV2(weights="imagenet")
        except:
            model = None

        def recognize_image(file_path):
            img = Image.open(file_path).resize((224, 224))
            arr = keras_image.img_to_array(img)
            arr = mobilenet_v2.preprocess_input(arr)
            preds = model.predict(arr[np.newaxis, ...])
            decoded = mobilenet_v2.decode_predictions(preds, top=1)[0]
            return decoded[0][1]  # predicted class name
    else:
        def recognize_image(file_path):
            return None

    # Handle Login button click
    def login(e):
        nonlocal user_phone, tech_points
        phone = phone_field.value.strip()
        pin = pin_field.value.strip()
        if phone and pin:
            cursor.execute("SELECT pin FROM farmers WHERE phone=%s", (phone,))
            result = cursor.fetchone()
            if result:
                # Existing user: check PIN
                if result[0] == pin:
                    user_phone = phone
                    tech_points = 0
                    show_tests()
                else:
                    page.snack_bar = ft.SnackBar(ft.Text("Incorrect PIN"))
                    page.snack_bar.open = True
                    page.update()
            else:
                # New user: insert into DB
                cursor.execute("INSERT INTO farmers (phone, pin) VALUES (%s, %s)", (phone, pin))
                conn.commit()
                user_phone = phone
                tech_points = 0
                show_tests()

    # Show technical-literacy test(s)
    def show_tests():
        page.clean()
        page.add(ft.Text("Technical Literacy Test", size=20))
        # Example test: Tap the button
        test_label = ft.Text("Tap the green button below", size=16)
        tap_button = ft.ElevatedButton("Tap me", bgcolor=ft.colors.GREEN,
                                       on_click=lambda e: complete_test(1))
        page.add(test_label, tap_button)
        page.update()

    def complete_test(points):
        nonlocal tech_points
        tech_points += points
        determine_literacy()

    def determine_literacy():
        page.clean()
        # Simple thresholds for low/med/high literacy
        if tech_points < 2:
            level = 1  # low
        elif tech_points < 4:
            level = 2  # medium
        else:
            level = 3  # high
        # Update DB
        cursor.execute("UPDATE farmers SET literacy_level=%s WHERE phone=%s", (level, user_phone))
        conn.commit()
        if level == 1:
            show_low_ui()
        elif level == 2:
            show_medium_ui()
        else:
            show_high_ui()

    # Low-literacy UI: big buttons, icons, voice
    def show_low_ui():
        page.clean()
        page.add(ft.Text("Welcome (Low Literacy)", size=24))
        # Large button for task, voice on click
        task_btn = ft.ElevatedButton(
            strings[user_lang]["daily_task"], width=250, height=100,
            on_click=lambda e: speak("This is your daily task.")
        )
        upload_btn = ft.ElevatedButton(
            strings[user_lang]["camera_upload"], width=250, height=100,
            on_click=lambda e: file_picker.pick_files(allow_multiple=False)
        )
        page.add(task_btn, upload_btn, file_picker)
        page.update()

    # Medium-literacy UI: some text + icons
    def show_medium_ui():
        page.clean()
        page.add(ft.Text("Welcome (Medium Literacy)", size=24))
        page.add(ft.Text(strings[user_lang]["daily_task"] + " Check soil moisture."))
        mic_btn = ft.IconButton(
            ft.icons.MIC, tooltip="Hear task",
            on_click=lambda e: speak("Check soil moisture and upload a photo.")
        )
        page.add(mic_btn, file_picker)
        page.update()

    # High-literacy UI: full text, calendar
    def show_high_ui():
        page.clean()
        page.add(ft.Text("Welcome (High Literacy)", size=24))
        page.add(ft.Text(strings[user_lang]["daily_task"] + " Identify the weed species."))
        mic_btn = ft.IconButton(
            ft.icons.MIC, tooltip="Hear task",
            on_click=lambda e: speak("Identify the weed in the photo and upload its image.")
        )
        page.add(mic_btn, file_picker)
        # Calendar for extra info
        cal = ft.Calendar()
        page.add(cal)
        page.update()

    # Handle file uploads from the file picker
    def on_file_result(e: ft.FilePickerResultEvent):
        for file in e.files:
            path = file.path
            identified = recognize_image(path) if tf and model else None
            cursor.execute(
                "INSERT INTO tasks (phone, task_name, image_path, recognized) VALUES (%s, %s, %s, %s)",
                (user_phone, "DailyTask", path, identified)
            )
            conn.commit()
            msg = strings[user_lang]["task_completed"]
            if identified:
                msg += f" Recognized: {identified}"
            page.snack_bar = ft.SnackBar(ft.Text(msg))
            page.snack_bar.open = True
            page.update()

    file_picker = ft.FilePicker(on_result=on_file_result)

    # Change language handler
    def change_language(e):
        nonlocal user_lang
        user_lang = e.control.value
        page.locale_configuration.current_locale = ft.Locale(user_lang)
        page.update()

    # Build initial login page
    page.add(
        ft.Dropdown(
            label="Language / மொழி", width=200,
            options=[
                ft.dropdown.Option("English", "en"),
                ft.dropdown.Option("Tamil / தமிழ்", "ta"),
                ft.dropdown.Option("Hindi / हिंदी", "hi"),
            ],
            value="en",
            on_change=change_language
        ),
        ft.TextField(label=strings[user_lang]["enter_phone"], width=300),
        ft.TextField(label=strings[user_lang]["enter_pin"], width=300, password=True),
        ft.ElevatedButton(strings[user_lang]["login"], on_click=login)
    )


ft.app(target=main)