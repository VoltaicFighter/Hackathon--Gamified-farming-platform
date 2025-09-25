import flet as ft


def main(page: ft.Page):
    page.title = "Farmer Tech Literacy Test"
    page.window_width = 400
    page.window_height = 700
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    ##################
    # CLICK TEST
    ##################
    click_count = ft.Text(value="Click Count: 0", size=20)

    def click_handler(e):
        count = int(click_count.value.split(": ")[1]) + 1
        click_count.value = f"Click Count: {count}"
        page.update()

    click_btn = ft.ElevatedButton("Click Me!", width=200, on_click=click_handler)

    def go_to_audio(e):
        page.go("/audio")

    click_test_view = ft.Column(
        controls=[
            ft.Text("Clicking Test", size=25, weight=ft.FontWeight.BOLD),
            ft.Text("Tap the button as accurately as you can."),
            click_btn,
            click_count,
            ft.ElevatedButton("Next Test", on_click=go_to_audio)
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    ##################
    # AUDIO INSTRUCTION TEST (No Audio widget)
    ##################
    def go_to_navigate(e):
        page.go("/navigate")

    audio_test_view = ft.Column(
        controls=[
            ft.Text("Audio Instruction Test", size=25, weight=ft.FontWeight.BOLD),
            ft.Text("Listen to the instruction and follow it."),
            ft.Text("Audio playback is not supported in Flet. Please play the instruction.mp3 file manually."),
            ft.ElevatedButton("Next Test", on_click=go_to_navigate)
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    ##################
    # NAVIGATION TEST
    ##################
    def go_to_swipe(e):
        page.go("/swipe")

    navigation_test_view = ft.Column(
        controls=[
            ft.Text("Navigation Test", size=25, weight=ft.FontWeight.BOLD),
            ft.Text("Tap the button below to go to the next test."),
            ft.ElevatedButton("Go to Next Test", on_click=go_to_swipe)
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    ##################
    # SWIPE TEST
    ##################
    swipe_status = ft.Text("Swipe left or right", size=20)

    def on_swipe(e: ft.DragUpdateEvent):
        if e.delta_x < -10:
            swipe_status.value = "Swiped Left!"
        elif e.delta_x > 10:
            swipe_status.value = "Swiped Right!"
        page.update()

    swipe_container = ft.GestureDetector(
        content=ft.Container(
            content=swipe_status,
            width=300,
            height=200,
            bgcolor="#FFECB3",  # Amber 100 hex value
            border_radius=10,
            alignment="center",  # <-- this is the fix!
        ),
        on_horizontal_drag_update=on_swipe
    )

    swipe_test_view = ft.Column(
        controls=[
            ft.Text("Swipe Test", size=25, weight=ft.FontWeight.BOLD),
            swipe_container,
            ft.Text("Try swiping the box left or right.")
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    ##################
    # ROUTING
    ##################
    def route_change(e):
        page.views.clear()
        if page.route == "/":
            page.views.append(ft.View("/", [click_test_view]))
        elif page.route == "/audio":
            page.views.append(ft.View("/audio", [audio_test_view]))
        elif page.route == "/navigate":
            page.views.append(ft.View("/navigate", [navigation_test_view]))
        elif page.route == "/swipe":
            page.views.append(ft.View("/swipe", [swipe_test_view]))
        page.update()

    page.on_route_change = route_change
    page.go(page.route or "/")


ft.run(main)