from datetime import date, time
from math import ceil
from calc import Calc
import pytest

def test_9h():
    """
    14 Euro für den Kalendertag, an dem der Arbeitnehmer ohne Übernachtung
    außerhalb seiner Wohnung mehr als 8 Stunden von seiner Wohnung und der
    ersten Tätigkeitsstätte abwesend ist
    """
    c = Calc()

    c.destination = {v:k for k,v in c.countries.items()}["Deutschland"]
    c.from_date = date(2015, 1, 1)
    c.from_time = time(10, 0)
    c.to_date = date(2015, 1, 1)
    c.to_time = time(19, 0)
    c.meal_deductions.append([False,False,False])

    assert c.calculate() == 14

def test_7h():
    """
    14 Euro für den Kalendertag, an dem der Arbeitnehmer ohne Übernachtung
    außerhalb seiner Wohnung mehr als 8 Stunden von seiner Wohnung und der
    ersten Tätigkeitsstätte abwesend ist
    """
    c = Calc()

    c.destination = {v:k for k,v in c.countries.items()}["Deutschland"]
    c.from_date = date(2015, 1, 1)
    c.from_time = time(10, 0)
    c.to_date = date(2015, 1, 1)
    c.to_time = time(17, 0)
    c.meal_deductions.append([False,False,False])

    assert c.calculate() == 0

def test_over_night():
    """
    jeweils 14 Euro für den An- und Abreisetag, wenn der Arbeitnehmer an diesem,
    einem anschließenden oder vorhergehenden Tag außerhalb seiner Wohnung übernachtet,
    """
    c = Calc()

    c.destination = {v:k for k,v in c.countries.items()}["Deutschland"]
    c.from_date = date(2015, 1, 1)
    c.from_time = time(20, 0)
    c.to_date = date(2015, 1, 2)
    c.to_time = time(10, 0)
    c.meal_deductions.append([False,False,False])
    c.meal_deductions.append([False,False,False])


    assert c.calculate() == 14 + 14

def test_full_day():
    """
    28 Euro für jeden Kalendertag, an dem der Arbeitnehmer 24 Stunden von
    seiner Wohnung und ersten Tätigkeitsstätte abwesend ist,
    """
    c = Calc()

    c.destination = {v:k for k,v in c.countries.items()}["Deutschland"]
    c.from_date = date(2015, 1, 1)
    c.from_time = time(12, 0)
    c.to_date = date(2015, 1, 3)
    c.to_time = time(12, 0)
    c.meal_deductions.append([False,False,False])
    c.meal_deductions.append([False,False,False])
    c.meal_deductions.append([False,False,False])

    assert c.calculate() == 14 + 28 + 14

def test_full_day_meal_deduction():
    """
    Wird dem Arbeitnehmer anlässlich oder während einer Tätigkeit außerhalb seiner ersten 
    Tätigkeitsstätte vom Arbeitgeber oder auf dessen Veranlassung von einem Dritten eine 
    Mahlzeit zur Verfügung gestellt, sind die nach den Sätzen 3 und 5 ermittelten Verpflegungspauschalen zu kürzen:
        1. für Frühstück um 20 Prozent,
        2. für Mittag- und Abendessen um jeweils 40 Prozent,
    der nach Satz 3 Nummer 1 gegebenenfalls in Verbindung mit Satz 5 maßgebenden 
    Verpflegungspauschale für einen vollen Kalendertag
    """
    c = Calc()

    breakfast_deduction = 28 * 0.2
    meal_deduction = 28 * 0.4 

    c.destination = {v:k for k,v in c.countries.items()}["Deutschland"]
    c.from_date = date(2015, 1, 1)
    c.from_time = time(12, 0)
    c.to_date = date(2015, 1, 3)
    c.to_time = time(12, 0)
    c.meal_deductions.append([False,False,True])
    c.meal_deductions.append([False,True,False])
    c.meal_deductions.append([True,False,False])

    assert c.calculate() == ceil(14 - meal_deduction) + ceil(28 - meal_deduction) + ceil(14 - breakfast_deduction)