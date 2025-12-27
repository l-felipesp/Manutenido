# dashboard.py
import flet as ft
import asyncio
from api_client import list_vehicles
from vehicle_form import open_vehicle_modal


def DashboardView(page: ft.Page):
    COLOR_EMERALD = "#10b981"
    COLOR_SLATE_900 = "#0f172a"
    COLOR_SLATE_400 = "#94a3b8"
    COLOR_CARD_BG = "#1e293b"
    COLOR_CARD_ALT = "#334155"

    lista_veiculos = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)

    def navegar_detalhes(e, vehicle_id, vehicle_data):
        page.session.set("selected_vehicle_id", vehicle_id)
        page.session.set("selected_vehicle_data", vehicle_data)
        page.go("/vehicle_details")

    # -------------------------------
    # Carregar veículos (API)
    # -------------------------------
    async def carregar_dados():
        lista_veiculos.controls.clear()
        lista_veiculos.controls.append(
            ft.Text("Carregando veículos...", color=COLOR_SLATE_400)
        )
        page.update()

        try:
            user_id = page.session.get("user_id")
            if not user_id:
                raise Exception("Usuário não autenticado")

            vehicles = await asyncio.to_thread(list_vehicles, user_id)

            if isinstance(vehicles, dict) and vehicles.get("error"):
                raise Exception(vehicles["error"])

        except Exception as exc:
            print("DEBUG dashboard erro:", exc)
            lista_veiculos.controls.clear()
            lista_veiculos.controls.append(
                ft.Text("Erro ao carregar veículos.", color="red")
            )
            page.update()
            return

        lista_veiculos.controls.clear()

        if not vehicles:
            lista_veiculos.controls.append(
                ft.Text(
                    "Nenhum veículo cadastrado. Clique em + para adicionar.",
                    color=COLOR_SLATE_400,
                )
            )
            page.update()
            return

        for v in vehicles:
            vehicle_id = v.get("id")
            tipo = v.get("tipo", "")
            icone = ft.Icons.DIRECTIONS_CAR

            if tipo == "Moto":
                icone = ft.Icons.TWO_WHEELER
            elif tipo == "Caminhão":
                icone = ft.Icons.LOCAL_SHIPPING
            elif tipo == "Bicicleta":
                icone = ft.Icons.PEDAL_BIKE

            card = ft.Container(
                bgcolor=COLOR_CARD_BG,
                border_radius=10,
                margin=ft.margin.only(bottom=10),
                content=ft.ListTile(
                    leading=ft.Icon(icone, color=COLOR_EMERALD),
                    title=ft.Text(
                        v.get("modelo", "---"),
                        weight="bold",
                        color="white",
                    ),
                    subtitle=ft.Text(
                        f"Placa: {v.get('placa', '---')}",
                        color=COLOR_SLATE_400,
                    ),
                    trailing=ft.Icon(
                        ft.Icons.CHEVRON_RIGHT,
                        color="white",
                    ),
                    on_click=lambda e, vid=vehicle_id, data=v: navegar_detalhes(
                        e, vid, data
                    ),
                ),
            )

            lista_veiculos.controls.append(card)

        page.update()

    # -------------------------------
    # Ações
    # -------------------------------
    def abrir_cadastro(e):
        open_vehicle_modal(
            page,
            on_success_callback=lambda: page.run_task(carregar_dados),
        )

    def fazer_logout(e):
        page.session.clear()
        page.go("/login")

    # dispara carregamento inicial
    page.run_task(carregar_dados)

    # -------------------------------
    # UI
    # -------------------------------
    return ft.Container(
        padding=20,
        expand=True,
        gradient=ft.LinearGradient(
            begin=ft.alignment.top_left,
            end=ft.alignment.bottom_right,
            colors=[COLOR_SLATE_900, "#1e293b", COLOR_SLATE_900],
        ),
        content=ft.Column(
            [
                # Cabeçalho
                ft.Row(
                    [
                        ft.Text(
                            "Meus Veículos",
                            size=28,
                            weight="bold",
                            color="white",
                        ),
                        ft.IconButton(
                            ft.Icons.LOGOUT,
                            on_click=fazer_logout,
                            icon_color="red",
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),

                ft.Divider(color="transparent"),

                # 🔧 Área da oficina (BUSCA POR PLACA)
                ft.Container(
                    bgcolor=COLOR_CARD_ALT,
                    padding=15,
                    border_radius=12,
                    margin=ft.margin.only(bottom=15),
                    on_click=lambda _: page.go("/workshop_search"),
                    content=ft.Row(
                        [
                            ft.Row(
                                [
                                    ft.Icon(
                                        ft.Icons.BUILD,
                                        color=COLOR_EMERALD,
                                    ),
                                    ft.Text(
                                        "Sou uma oficina / Buscar veículo por placa",
                                        color="white",
                                        weight="bold",
                                    ),
                                ]
                            ),
                            ft.Icon(
                                ft.Icons.ARROW_FORWARD,
                                color="white",
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                ),

                # Lista de veículos
                ft.Container(content=lista_veiculos, expand=True),

                # Botão +
                ft.FloatingActionButton(
                    icon=ft.Icons.ADD,
                    bgcolor=COLOR_EMERALD,
                    on_click=abrir_cadastro,
                ),
            ]
        ),
    )
