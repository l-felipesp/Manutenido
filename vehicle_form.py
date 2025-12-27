import flet as ft
import asyncio
from api_client import add_vehicle


def open_vehicle_modal(page: ft.Page, on_success_callback=None):
    txt_modelo = ft.TextField(label="Modelo")
    txt_placa = ft.TextField(label="Placa")
    dd_tipo = ft.Dropdown(
        label="Tipo",
        options=[
            ft.dropdown.Option("Carro"),
            ft.dropdown.Option("Moto"),
            ft.dropdown.Option("Caminhão"),
            ft.dropdown.Option("Bicicleta"),
        ],
        value="Carro",
    )

    error_text = ft.Text("", color="red")
    btn_save = ft.ElevatedButton("Salvar", bgcolor="#10b981", color="white")
    btn_cancel = ft.TextButton("Cancelar")

    def fechar(e=None):
        try:
            page.overlay.remove(overlay)
        except Exception:
            pass
        page.update()

    async def salvar_async():
        btn_save.disabled = True
        btn_save.text = "Salvando..."
        error_text.value = ""
        page.update()

        try:
            user_id = page.session.get("user_id")
            payload = {
                "modelo": txt_modelo.value.strip(),
                "placa": txt_placa.value.strip().upper(),
                "tipo": dd_tipo.value,
                "user_id": user_id,
            }

            await asyncio.to_thread(add_vehicle, payload)

        except Exception as exc:
            error_text.value = "Erro ao salvar veículo."
            print("ERRO salvar veículo:", exc)
            btn_save.disabled = False
            btn_save.text = "Salvar"
            page.update()
            return

        # sucesso
        if on_success_callback:
            on_success_callback()

        fechar()

    def on_save_click(e):
        if not txt_modelo.value or not txt_placa.value:
            txt_modelo.error_text = "Obrigatório" if not txt_modelo.value else None
            txt_placa.error_text = "Obrigatório" if not txt_placa.value else None
            page.update()
            return

        page.run_task(salvar_async)  # ✅ padrão correto

    btn_cancel.on_click = fechar
    btn_save.on_click = on_save_click

    card = ft.Container(
        width=400,
        padding=20,
        bgcolor="#1e293b",
        border_radius=12,
        content=ft.Column(
            [
                ft.Text("Cadastrar veículo", size=20, weight="bold", color="white"),
                txt_modelo,
                txt_placa,
                dd_tipo,
                error_text,
                ft.Row([ft.Container(expand=True), btn_cancel, btn_save]),
            ],
            tight=True,
        ),
    )

    overlay = ft.Container(
        expand=True,
        bgcolor="#00000088",
        alignment=ft.alignment.center,
        content=card,
    )

    page.overlay.append(overlay)
    page.update()
