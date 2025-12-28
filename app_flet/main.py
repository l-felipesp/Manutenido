import sys
import os
import flet as ft

project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

def main(page: ft.Page):
    page.title = "Manutenido"
    page.theme_mode = ft.ThemeMode.DARK

    def route_change(route):
        page.views.clear()
        from home import HomeView
        from dashboard import DashboardView
        from vehicle_details import VehicleDetailsView
        from login import LoginView
        from workshop_search import WorkshopSearchView

        if page.route == "/":
            page.views.append(ft.View("/", [HomeView(page)], padding=0))
        elif page.route == "/login":
            page.views.append(ft.View("/login", [LoginView(page)], padding=0))
        elif page.route == "/dashboard":
            page.views.append(ft.View("/dashboard", [DashboardView(page)]))
        elif page.route == "/vehicle_details":
            page.views.append(ft.View("/vehicle_details", [VehicleDetailsView(page)]))
        elif page.route == "/workshop_search":
            page.views.append(ft.View("/workshop_search", [WorkshopSearchView(page)]))

        page.update()

    page.on_route_change = route_change
    page.go("/login")

if __name__ == "__main__":
    ft.run(
        target=main,
        view=ft.AppView.WEB_BROWSER,
        port=8550
    )
