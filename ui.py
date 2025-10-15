from datetime import date, time, datetime, timedelta
from nicegui import __version__, ui
from nicegui.elements.grid import Grid

from calc import Calc

class UI:
    def __init__(self, calc: Calc) -> None:
        self.calc = calc
        self.language = "en-US"

    def date_picker(self, attrname):
        with ui.input('Date') as date_input:
            with ui.menu().props('no-parent-event') as menu:
                with ui.date().bind_value(date_input):
                    with ui.row().classes('justify-end'):
                        ui.button('Close', on_click=menu.close).props('flat')
            with date_input.add_slot('append'):
                ui.icon('edit_calendar').on('click', menu.open).classes('cursor-pointer')
            date_input.on_value_change(lambda x: setattr(self.calc, attrname, datetime.strptime(x.value, "%Y-%m-%d").date()))

    def time_picker(self, attrname):
        with ui.input('Time') as time_input:
            with ui.menu().props('no-parent-event') as menu:
                with ui.time().bind_value(time_input):
                    with ui.row().classes('justify-end'):
                        ui.button('Close', on_click=menu.close).props('flat')
            with time_input.add_slot('append'):
                ui.icon('access_time').on('click', menu.open).classes('cursor-pointer')
            time_input.on_value_change(lambda x: setattr(self.calc, attrname, datetime.strptime(x.value, "%H:%M").time()))


    @ui.refreshable_method
    def deduction_grid(self):
        with ui.grid(columns=4):
            self.calc.meal_deductions.clear()
            if self.calc.from_date == None or self.calc.to_date == None:
                ui.label("Bitte Reisebeginn und Ende auswählen")
                return
            delta = self.calc.to_date - self.calc.from_date
            for i in range(delta.days + 1):
                self.calc.meal_deductions.append([False, False, False])
                current_day = self.calc.from_date + timedelta(days=i)
                ui.label(f'Day {current_day}')

                def set(row, column, val):
                    self.calc.meal_deductions[row][column] = val
                    self.result.refresh()

                ui.checkbox(on_change=lambda x, i=i: set(i, 0, x.value))
                ui.checkbox(on_change=lambda x, i=i: set(i, 1, x.value))
                ui.checkbox(on_change=lambda x, i=i: set(i, 2, x.value))
            self.result.refresh()

    def left_row(self):
        with ui.card():
            ui.label('Begin der Reise')
            with ui.column():
                self.date_picker("from_date")
                self.time_picker("from_time")
            ui.label('Ende der Reise')
            with ui.column():
                self.date_picker("to_date")
                self.time_picker("to_time")
            ui.label('Reiseland')
            def on_change(vcea):
                self.calc.destination = vcea.value
            ui.select(self.calc.countries, on_change=on_change)

            ui.button('Aktualisieren', on_click=lambda: self.deduction_grid.refresh())

    def right_row(self):
        with ui.column():
            with ui.card():
                ui.label("Verpflegungsabzüge")
                self.deduction_grid()
            with ui.card():
                self.result()

    @ui.refreshable_method
    def result(self):
        try:
            ui.label(f"{self.calc.calculate()}€")
        except AssertionError as e:
            ui.label(f"Error: {e}")

    def run(self):
        ui.add_body_html(f'''
            <script src="/_nicegui/{__version__}/static/lang/de.umd.prod.js"></script>
            <script src="/_nicegui/{__version__}/static/lang/fr.umd.prod.js"></script>
            <script src="/_nicegui/{__version__}/static/lang/es.umd.prod.js"></script>
            <script src="/_nicegui/{__version__}/static/lang/zh-CN.umd.prod.js"></script>
        ''')        
        with ui.header(elevated=True).style('background-color: #3874c8').classes('items-center justify-between'):
            ui.label('Reisekosten 2025')


            def switch_language(language_code: str) -> None:
                self.language = language_code
                ui.run_javascript(f'''
                    Quasar.lang.set(Quasar.lang["{language_code.replace('-', '')}"])
                ''')


            ui.select(options={
                'de': 'Deutsch',
                'en': 'English',
                'fr': 'Français',
                'es': 'Español',
                'zh-CN': '中文',
            }, value='en', on_change=lambda e: switch_language(e.value))

        ui.date()
        with ui.row():
            self.left_row()
            self.right_row()
        
        ui.run()
