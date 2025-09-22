import flet as ft

# Available languages
LANGUAGES = ["English", "Español", "Français", "Deutsch", "العربية"]

def main(page: ft.Page):
    page.title = "Language & Login App"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # Save selected language
    selected_language = ft.Text(value="", visible=False)

    def show_login(e):
        selected = dropdown.value
        if selected:
            selected_language.value = selected
            # Clear previous controls
            page.controls.clear()
            page.controls.append(ft.Text(f"Language selected: {selected}", size=20))

            # Create login form
            username = ft.TextField(label="Username", width=300)
            password = ft.TextField(label="Password", password=True, can_reveal_password=True, width=300)
            login_button = ft.ElevatedButton("Login", on_click=lambda e: handle_login(username.value, password.value))

            # Add form to page
            page.controls.extend([username, password, login_button])
            page.update()

    def handle_login(username, password):
        print(f"Username: {username}")
        print(f"Password: {password}")
        # In real apps, you'd validate credentials here

        page.controls.clear()
        page.controls.append(ft.Text(f"Welcome, {username}!", size=25))
        page.update()

    # Language selection dropdown
    dropdown = ft.Dropdown(
        label="Select your language",
        options=[ft.dropdown.Option(lang) for lang in LANGUAGES],
        width=300,
    )
    continue_button = ft.ElevatedButton("Continue", on_click=show_login)

    # Initial UI
    page.add(
        ft.Text("Welcome! Please select your language:", size=20),
        dropdown,
        continue_button,
        selected_language
    )

ft.app(target=main)