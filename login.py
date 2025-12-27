import flet as ft
import asyncio
from firebase_config import sign_in_with_email_and_password, register_with_email_and_password


def LoginView(page: ft.Page):
    txt_email = ft.TextField(label="E-mail", width=300)
    txt_password = ft.TextField(label="Senha", password=True, can_reveal_password=True, width=300)
    status = ft.Text("", color="red")

    # ✅ ASYNC SEM PARÂMETROS
    async def executar_login():
        try:
            res = await asyncio.to_thread(
                sign_in_with_email_and_password,
                txt_email.value,
                txt_password.value
            )
        except Exception:
            status.value = "E-mail ou senha inválidos"
            page.update()
            return

        page.session.set("user_id", res.get("localId"))
        page.session.set("id_token", res.get("idToken"))
        page.go("/dashboard")

    async def executar_cadastro():
        try:
            res = await asyncio.to_thread(
                register_with_email_and_password,
                txt_email.value,
                txt_password.value
            )
        except Exception:
            status.value = "Erro ao criar conta"
            page.update()
            return

        page.session.set("user_id", res.get("localId"))
        page.session.set("id_token", res.get("idToken"))
        page.go("/dashboard")

    def on_login_click(e):
        status.value = "Entrando..."
        page.update()
        page.run_task(executar_login)  # ✅ CORRETO

    def on_register_click(e):
        status.value = "Criando conta..."
        page.update()
        page.run_task(executar_cadastro)  # ✅ CORRETO

    return ft.Container(
        expand=True,
        alignment=ft.alignment.center,
        content=ft.Column(
            [
                ft.Text("Login", size=30, weight="bold"),
                txt_email,
                txt_password,
                status,
                ft.ElevatedButton("Entrar", on_click=on_login_click),
                ft.TextButton("Criar conta", on_click=on_register_click),
            ],
            horizontal_alignment="center",
            spacing=15,
        ),
    )
