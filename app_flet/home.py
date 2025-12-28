import flet as ft

def HomeView(page: ft.Page):
    # Cores exatas da sua interface original
    color_emerald = "#10b981"
    color_slate_900 = "#0f172a"
    color_slate_800 = "#1e293b"
    color_slate_400 = "#94a3b8"

    logo_icon = ft.Container(
        content=ft.Icon(ft.Icons.DIRECTIONS_CAR_ROUNDED, size=50, color="white"),
        bgcolor=color_emerald,
        padding=15,
        border_radius=20,
    )

    title = ft.Text(
        "Histórico completo do seu veículo",
        size=40,
        weight=ft.FontWeight.BOLD,
        color="white",
        text_align=ft.TextAlign.CENTER,
    )

    description = ft.Text(
        "Registre manutenções, eventos e mantenha seu veículo sempre em dia. Compartilhe o acesso com oficinas de confiança.",
        size=16,
        color=color_slate_400,
        text_align=ft.TextAlign.CENTER,
    )

    btn_start = ft.ElevatedButton(
        content=ft.Row(
            [ft.Text("Começar agora", size=18), ft.Icon(ft.Icons.ARROW_FORWARD)],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        bgcolor=color_emerald,
        color="white",
        height=60,
        width=250,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=15)),
        on_click=lambda _: page.go("/login")
    )

    def feature_card(icon, label):
        return ft.Container(
            content=ft.Column([
                ft.Icon(icon, color=color_emerald, size=30),
                ft.Text(label, size=12, weight="bold", color="white")
            ], horizontal_alignment="center"),
            bgcolor="#ffffff10", # Branco com 10% de opacidade
            padding=15,
            border_radius=15,
            expand=True
        )

    features = ft.Row([
        feature_card(ft.Icons.DIRECTIONS_CAR, "10 Veículos"),
        feature_card(ft.Icons.BUILD_CIRCLE, "Histórico"),
        feature_card(ft.Icons.SHIELD, "Segurança"),
    ], spacing=10)

    return ft.Container(
        expand=True,
        gradient=ft.LinearGradient(
            begin=ft.alignment.top_left,
            end=ft.alignment.bottom_right,
            colors=[color_slate_900, color_slate_800, color_slate_900],
        ),
        content=ft.Column([
            ft.Container(height=50),
            logo_icon,
            ft.Container(height=20),
            title,
            ft.Container(padding=20, content=description),
            ft.Container(height=30),
            btn_start,
            ft.Container(height=40),
            ft.Container(padding=20, content=features),
        ], horizontal_alignment="center", scroll=ft.ScrollMode.AUTO)
    )
