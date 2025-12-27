# event_form.py
import flet as ft
import asyncio
from api_client import add_event


def open_event_modal(page: ft.Page, vehicle_id: str, on_success_callback=None):
    txt_desc = ft.TextField(label="Descrição")
    txt_km = ft.TextField(
        label="Quilometragem", keyboard_type=ft.KeyboardType.NUMBER
    )

    dd_tipo = ft.Dropdown(
        label="Tipo",
        value="Manutenção",
        options=[
            ft.dropdown.Option("Manutenção"),
            ft.dropdown.Option("Abastecimento"),
            ft.dropdown.Option("Ocorrência"),
        ],
    )

    error = ft.Text("", color="red")
    btn_save = ft.ElevatedButton("Salvar", bgcolor="#10b981", color="white")
    btn_cancel = ft.TextButton("Cancelar")

    def fechar(e=None):
        try:
            page.overlay.remove(overlay)
        except Exception:
            pass
        page.update()

    async def salvar_evento():
        error.value = ""
        page.update()

        if not txt_desc.value:
            error.value = "Descrição obrigatória"
            page.update()
            return

        btn_save.disabled = True
        btn_save.text = "Salvando..."
        page.update()

        try:
            payload = {
                "vehicle_id": vehicle_id,
                "user_id": page.session.get("user_id"),
                "tipo": dd_tipo.value,
                "descricao": txt_desc.value.strip(),
                "km": int(txt_km.value) if txt_km.value else None,
            }

            result = await asyncio.to_thread(add_event, payload)

            if isinstance(result, dict) and result.get("error"):
                raise Exception(result["error"])

            if on_success_callback:
                on_success_callback()

            fechar()

        except Exception as exc:
            print("DEBUG add_event erro:", exc)
            error.value = "Erro ao salvar evento."

        finally:
            btn_save.disabled = False
            btn_save.text = "Salvar"
            page.update()

    btn_cancel.on_click = fechar
    btn_save.on_click = lambda e: page.run_task(salvar_evento)

    card = ft.Container(
        width=400,
        padding=20,
        bgcolor="#1e293b",
        border_radius=12,
        content=ft.Column(
            [
                ft.Text("Novo Evento", size=20, weight="bold", color="white"),
                dd_tipo,
                txt_desc,
                txt_km,
                ft.Row(
                    [
                        ft.Container(expand=True),
                        btn_cancel,
                        btn_save,
                    ]
                ),
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
