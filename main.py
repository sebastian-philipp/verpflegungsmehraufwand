import csv
from typing import NamedTuple

from calc import Calc
import ui

ui_main = ui.UI(Calc())
ui_main.run()
