
import csv
from datetime import date, time
from math import ceil
from typing import NamedTuple


class Tagespauschale(NamedTuple):
    country: str
    full_day: int
    half_day: int

def read_csv() -> list[Tagespauschale]:
    out = []
    with open('tagespauschalen-2025.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter='	', quotechar='"')
        next(reader) # skip header
        for l in reader:
            if len(l) == 1:
                out.append(Tagespauschale(l[0],0,0))
            elif len(l) == 4:
                out.append(Tagespauschale(l[0].strip(),int(l[1]),int(l[2])))
            else:
                assert False, len(l)

    return out


class Calc:
    """
    https://esth.bundesfinanzministerium.de/lsth/2025/B-Anhaenge/Anhang-25/I/inhalt.html
    https://www.gesetze-im-internet.de/estg/__9.html -> (4a)
    """
    def __init__(self) -> None:
        self.tagespauschalen = read_csv()
        self.countries = dict(zip(range(len(self.tagespauschalen)), [country.country for country in self.tagespauschalen]))

        self.destination = 0
        self.from_date: date | None = None
        self.from_time: time | None = None
        self.to_date: date | None = None
        self.to_time: time | None = None
        self.meal_deductions: list[list[bool]] = []


    def calculate(self) -> int:
        assert self.from_date is not None
        assert self.from_time is not None
        assert self.to_date is not None
        assert self.to_time is not None

        tagespauschale = None
        for t in self.tagespauschalen:
            if t.country == self.countries[self.destination]:
                tagespauschale = t
                break
        assert tagespauschale is not None

        def meal_deduction(day, amount):
            assert tagespauschale is not None

            breakfast_deduction = tagespauschale.full_day * 0.2
            meal_deduction = tagespauschale.full_day * 0.4 

            if self.meal_deductions[day][0]:
                amount -= breakfast_deduction
            if self.meal_deductions[day][1]:
                amount -= meal_deduction
            if self.meal_deductions[day][2]:
                amount -= meal_deduction
            
            return max(ceil(amount), 0)


        if self.from_date == self.to_date:
            if self.to_time.hour - self.from_time.hour >= 8:
                return meal_deduction(0, tagespauschale.half_day)
            else:
                return 0

        day_amouts = []
        day_amouts.append(tagespauschale.half_day)
        day_amouts.extend([tagespauschale.full_day] * ((self.to_date - self.from_date).days - 1))
        day_amouts.append(tagespauschale.half_day)

        return sum([meal_deduction(i, a) for i,a in enumerate(day_amouts)])