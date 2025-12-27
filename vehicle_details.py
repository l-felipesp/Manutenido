# vehicle_details.py
import flet as ft
import asyncio
from api_client import list_events
from event_form import open_event_modal


def VehicleDetailsView(page: ft.Page):
    COLOR_EMERALD = "#10b981"
    COLOR_SLATE_900 = "#0f172a"
    COLOR_CARD_BG = "#1e293b"

    vehicle_data = page.session.get("selected_vehicle_data")
    vehicle_id = page.session.get("selected_vehicle_id")

    if not vehicle_data or not vehicle_id:
        return ft.Text("Erro: Nenhum veículo selecionado", color="red")

    header = ft.Container(
        padding=20,
        bgcolor=COLOR_CARD_BG,
        border_radius=15,
        content=ft.Row(
            [
                ft.Icon(ft.Icons.DIRECTIONS_CAR, size=40, color=COLOR_EMERALD),
                ft.Column(
                    [
                        ft.Text(vehicle_data.get("modelo", ""), size=24, weight="bold", color="white"),
                        ft.Text(vehicle_data.get("placa", ""), size=16, color="#94a3b8"),
                    ]
                ),
            ]
        ),
    )

    history_list = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO)
    loading = ft.Text("Carregando histórico...", color="#94a3b8")

    async def carregar_historico():
        history_list.controls.clear()
        history_list.controls.append(loading)
        page.update()

        try:
            eventos = await asyncio.to_thread(list_events, vehicle_id)

            history_list.controls.clear()

            if not eventos:
                history_list.controls.append(
                    ft.Text("Nenhum histórico ainda.", color="#94a3b8")
                )
            else:
                for data in eventos:
                    icon = ft.Icons.BUILD_CIRCLE
                    color = COLOR_EMERALD

                    if data.get("tipo") in ("Ocorrência", "Problema"):
                        icon = ft.Icons.WARNING_AMBER
                        color = "orange"
                    elif data.get("tipo") == "Abastecimento":
                        icon = ft.Icons.LOCAL_GAS_STATION
                        color = "blue"

                    history_list.controls.append(
                        ft.Container(
                            bgcolor=COLOR_CARD_BG,
                            padding=15,
                            border_radius=10,
                            margin=ft.margin.only(bottom=10),
                            content=ft.Row(
                                [
                                    ft.Icon(icon, color=color, size=30),
                                    ft.Column(
                                        [
                                            ft.Text(data.get("tipo", "Evento"), weight="bold", size=16, color="white"),
                                            ft.Text(data.get("descricao", ""), size=14, color="#94a3b8"),
                                            ft.Text(
                                                f"{data.get('km')} km" if data.get("km") else "",
                                                size=12,
                                                color="#64748b",
                                            ),
                                        ],
                                        expand=True,
                                    ),
                                ]
                            ),
                        )
                    )

        except Exception as exc:
            print("DEBUG histórico erro:", exc)
            history_list.controls.clear()
            history_list.controls.append(ft.Text("Erro ao carregar histórico.", color="red"))

        page.update()

    def abrir_modal_evento(e):
        open_event_modal(page, vehicle_id, on_success_callback=lambda: page.run_task(carregar_historico))

    page.run_task(carregar_historico)

    return ft.Container(
        expand=True,
        padding=20,
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
                        ft.Text("Detalhes do Veículo", size=20, weight="bold", color="white"),
                    ]
                ),
                ft.Container(height=20),
                header,
                ft.Container(height=20),
                ft.Text("Histórico de Eventos", size=18, weight="bold", color="white"),
                ft.Container(content=history_list, expand=True),
                ft.FloatingActionButton(
                    icon=ft.Icons.ADD,
                    bgcolor=COLOR_EMERALD,
                    on_click=abrir_modal_evento,
                ),
            ]
        ),
    )
