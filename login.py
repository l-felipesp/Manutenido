# login.py
import flet as ft
import asyncio
from api_client import auth_login, auth_register


def LoginView(page: ft.Page):
    txt_email = ft.TextField(
        label="E-mail",
        width=300,
        keyboard_type=ft.KeyboardType.EMAIL
    )
    txt_password = ft.TextField(
        label="Senha",
        password=True,
        can_reveal_password=True,
        width=300
    )

    status = ft.Text("", color="red")

    # ---------- LOGIN ----------
    async def executar_login():
        try:
            res = await asyncio.to_thread(
                auth_login,
                txt_email.value.strip(),
                txt_password.value
            )
        except Exception as exc:
            print("DEBUG login exception:", exc)
            status.value = "Erro de conexão."
            page.update()
            return

        if isinstance(res, dict) and res.get("error"):
            status.value = "E-mail ou senha inválidos."
            page.update()
            return

        # sucesso
        page.session.set("user_id", res.get("localId"))
        page.session.set("id_token", res.get("idToken"))
        page.go("/dashboard")

    # ---------- CADASTRO ----------
    async def executar_cadastro():
        try:
            res = await asyncio.to_thread(
                auth_register,
                txt_email.value.strip(),
                txt_password.value
            )
        except Exception as exc:
            print("DEBUG cadastro exception:", exc)
            status.value = "Erro de conexão."
            page.update()
            return

        if isinstance(res, dict) and res.get("error"):
            status.value = "Erro ao criar conta."
            page.update()
            return

        # sucesso
        page.session.set("user_id", res.get("localId"))
        page.session.set("id_token", res.get("idToken"))
        page.go("/dashboard")

    # ---------- HANDLERS ----------
    def on_login_click(e):
        if not txt_email.value or not txt_password.value:
            status.value = "Preencha e-mail e senha."
            page.update()
            return

        status.value = "Entrando..."
        page.update()
        page.run_task(executar_login)

    def on_register_click(e):
        if not txt_email.value or not txt_password.value:
            status.value = "Preencha e-mail e senha."
            page.update()
            return

        status.value = "Criando conta..."
        page.update()
        page.run_task(executar_cadastro)

    # ---------- UI ----------
    return ft.Container(
        expand=True,
        alignment=ft.alignment.center,
        content=ft.Column(
            [
                ft.Text("Manutenido", size=32, weight="bold"),
                ft.Text("Acesse sua conta", color="#94a3b8"),
                txt_email,
                txt_password,
                status,
                ft.ElevatedButton(
                    "Entrar",
                    on_click=on_login_click,
                    width=300,
                    height=45
                ),
                ft.TextButton(
                    "Criar conta",
                    on_click=on_register_click
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15,
        ),
    )
