# workshop_search.py
import flet as ft
import asyncio
from api_client import find_vehicle_by_plate


def WorkshopSearchView(page: ft.Page):
    COLOR_EMERALD = "#10b981"
    COLOR_SLATE_900 = "#0f172a"

    txt_placa = ft.TextField(
        label="Digite a Placa do Cliente",
        hint_text="Ex: ABC-1234",
        text_align=ft.TextAlign.CENTER,
        border_color=COLOR_EMERALD,
        color="white",
        text_size=20,
        width=250,
        capitalization=ft.TextCapitalization.CHARACTERS,
    )

    error_text = ft.Text("", color="red")

    async def buscar_veiculo():
        error_text.value = ""
        page.update()

        if not txt_placa.value:
            error_text.value = "Digite uma placa."
            page.update()
            return

        try:
            placa = txt_placa.value.strip().upper()
            result = await asyncio.to_thread(find_vehicle_by_plate, placa)

            if isinstance(result, dict) and result.get("error"):
                raise Exception(result["error"])

            if result and result.get("id"):
                page.session.set("selected_vehicle_id", result.get("id"))
                page.session.set("selected_vehicle_data", result)
                page.go("/vehicle_details")
            else:
                error_text.value = "Veículo não encontrado. Verifique a placa."

        except Exception as exc:
            print("DEBUG workshop_search erro:", exc)
            error_text.value = "Erro ao buscar veículo."

        page.update()

    return ft.Container(
        expand=True,
        gradient=ft.LinearGradient(
            begin=ft.alignment.top_left,
            end=ft.alignment.bottom_right,
            colors=[COLOR_SLATE_900, "#1e293b", COLOR_SLATE_900],
        ),
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.IconButton(
                            ft.Icons.ARROW_BACK,
                            on_click=lambda _: page.go("/dashboard"),
                            icon_color="white",
                        ),
                        ft.Text("Área da Oficina", size=20, weight="bold", color="white"),
                    ]
                ),
                ft.Container(height=50),
                ft.Icon(ft.Icons.SEARCH, size=80, color=COLOR_EMERALD),
                ft.Text("Buscar Veículo", size=28, weight="bold", color="white"),
                ft.Text(
                    "Digite a placa para registrar uma manutenção",
                    color="#94a3b8",
                ),
                ft.Container(height=30),
                txt_placa,
                error_text,
                ft.Container(height=20),
                ft.ElevatedButton(
                    "BUSCAR VEÍCULO",
                    on_click=lambda e: page.run_task(buscar_veiculo),
                    bgcolor=COLOR_EMERALD,
                    color="white",
                    height=50,
                    width=200,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )
