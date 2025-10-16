from datetime import datetime, timedelta
import locale
from nicegui import __version__, ui

from calc import Calc

class UI:
    t_de_de = {
        '**Travel Information**': '**Information**',
        "Please select begin and end of travel": "Bitte Reisebeginn und Ende auswählen",
        'Begin of travel': 'Anfang der Reise',
        'End of travel': 'Ende der Reise',
        'Destination': 'Reiseland',
        'Refresh': 'Aktualisieren',
        'Meal deductions': "Abzüge der Verpflegungspauschale",
        'Travel Reimbursement 2025': 'Reisekosten 2025',
        'Date': 'Datum',
        'Time': 'Uhrzeit',
        'Day': 'Tag',

        'Departing day': 'Tagespauschale (Abfahrt)',
        'Full days': 'Volle Tage',
        'Arriving day': 'Tagespauschale (Ankunft)',
        '**Sum**': '**Summe**',
        'Reimbursement Total': 'Summen',
    }

    def __init__(self, calc: Calc) -> None:
        self.calc = calc
        self.language = "en-US"

    def t(self, txt):
        if self.language == "de-DE":
            return self.t_de_de[txt]
        return txt

    def date_picker(self, attrname):
        with ui.input(self.t('Date')) as date_input:
            with ui.menu().props('no-parent-event') as menu:
                with ui.date().bind_value(date_input):
                    with ui.row().classes('justify-end'):
                        ui.button('Close', on_click=menu.close).props('flat')
            with date_input.add_slot('append'):
                ui.icon('edit_calendar').on('click', menu.open).classes('cursor-pointer')
            date_input.on_value_change(lambda x: setattr(self.calc, attrname, datetime.strptime(x.value, "%Y-%m-%d").date()))

    def time_picker(self, attrname):
        with ui.input(self.t('Time')) as time_input:
            with ui.menu().props('no-parent-event') as menu:
                with ui.time().bind_value(time_input):
                    with ui.row().classes('justify-end'):
                        ui.button('Close', on_click=menu.close).props('flat')
            with time_input.add_slot('append'):
                ui.icon('access_time').on('click', menu.open).classes('cursor-pointer')
            time_input.on_value_change(lambda x: setattr(self.calc, attrname, datetime.strptime(x.value, "%H:%M").time()))


    @ui.refreshable_method
    def deduction_grid(self):
        with ui.grid(columns=4).classes("items-center"):
            self.calc.meal_deductions.clear()
            if self.calc.from_date == None or self.calc.to_date == None:
                ui.label(self.t("Please select begin and end of travel"))
                return
            delta = self.calc.to_date - self.calc.from_date
            for i in range(delta.days + 1):
                self.calc.meal_deductions.append([False, False, False])
                current_day = self.calc.from_date + timedelta(days=i)
                ui.label(f'{self.t("Day")} {current_day.strftime("%x")}')

                def set(row, column, val):
                    self.calc.meal_deductions[row][column] = val
                    self.result.refresh()

                ui.checkbox(on_change=lambda x, i=i: set(i, 0, x.value))
                ui.checkbox(on_change=lambda x, i=i: set(i, 1, x.value))
                ui.checkbox(on_change=lambda x, i=i: set(i, 2, x.value))
            self.result.refresh()

    def left_row(self):
        with ui.column().classes("col-3"):
            with ui.card().classes("full-width no-row-gap"):
                ui.markdown(self.t('**Employee**'))
                ui.textarea().classes("full-width")
                ui.markdown(self.t('**Recipient**'))
                ui.textarea().classes("full-width")
            with ui.card().classes("full-width"):
                ui.markdown(self.t('**Travel Information**'))
                ui.label(self.t('Begin of travel'))
                with ui.column():
                    self.date_picker("from_date")
                    self.time_picker("from_time")
                ui.label(self.t('End of travel'))
                with ui.column():
                    self.date_picker("to_date")
                    self.time_picker("to_time")
                ui.label(self.t('Destination'))
                def on_change(vcea):
                    self.calc.destination = vcea.value
                ui.select(self.calc.countries, on_change=on_change)

                ui.button(self.t('Refresh'), on_click=lambda: self.deduction_grid.refresh()).classes("print-hide")

    def right_row(self):
        with ui.column():
            with ui.card().classes("full-width"):
                ui.markdown(f'**{self.t("Meal deductions")}**')
                self.deduction_grid()
    
            ui.html('<div style="break-after:page;" class="print-only"></div>', sanitize=False)
            ui.html('<div style="margin-top: 4em" class="print-only"></div>', sanitize=False)

            with ui.card().classes("full-width"):
                self.result()

    @ui.refreshable_method
    def result(self):
        ui.markdown(f'**{self.t("Reimbursement Total")}**')

        try:
            res = self.calc.calculate()
        except AssertionError as e:
            res = 0
            ui.label(f"Error: {repr(e)}")

        with ui.grid(columns=2):        
            ui.label(self.t('Departing day'))
            ui.label(f'{self.calc.per_diem_rate().half_day} €').style('text-align: right')
            ui.label(self.t('Full days'))
            ui.label(f'{self.calc.per_diem_full_days()} €').style('text-align: right')
            ui.label(self.t('Arriving day'))
            ui.label(f'{self.calc.per_diem_rate().half_day} €').style('text-align: right')
            ui.label(self.t('Meal deductions'))
            ui.label(f'{res - (2 * self.calc.per_diem_rate().half_day + self.calc.per_diem_full_days())} €').style('text-align: right')

            ui.separator()
            ui.separator()
            ui.markdown(self.t('**Sum**'))
            ui.markdown(f"**{res} €**").style('text-align: right')

    def menu(self):
        with ui.header(elevated=True).style('background-color: #3874c8').classes('items-center justify-between'):
            ui.label(self.t('Travel Reimbursement 2025'))

            with ui.button(icon='menu').classes("print-hide"):
                with ui.menu(): 
                    ui.link('/en-US', '/en-US')
                    ui.separator()
                    ui.link('/de-DE', '/de-DE')


    def index(self, language_code: str = "en-US"):
        self.language = language_code
        locale.setlocale(locale.LC_ALL, self.language.replace("-", "_") + ".UTF-8")

        ui.add_body_html(f'''
            <script defer src="/_nicegui/{__version__}/static/lang/{language_code}.umd.prod.js"></script>
            <script>
                document.addEventListener('DOMContentLoaded', function() {{
                    Quasar.lang.set(Quasar.lang["{language_code.replace('-', '')}"])
                }})
            </script>
        ''')

        with ui.row().classes("no-wrap"):
            self.left_row()
            self.right_row()

    def root(self):
        ui.add_css("""
            @media print {
                font-size: 12px; 
                line-height: 80%;
            }
            .no-row-gap {
                row-gap: 0;
            }
            """)
        self.menu()
        ui.sub_pages({'/{language_code}': self.index, '/': self.index})

    def run(self):
        ui.run(self.root, title="Travel Reimbursement")
