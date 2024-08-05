"""Фикстуры для pytest"""

from datetime import datetime

import pandas as pd
import pytest


# Список транзакций как Датафрейм
@pytest.fixture
def transactions() -> pd.DataFrame:
    data = {
        "Дата операции": ["01.01.2018 00:00:00", "01.02.2018 00:00:00"],
        "Сумма платежа": [-100.50, -505.30],
        "Статус": ["OK", "OK"],
        "Номер карты": ["*4516", "*7815"],
        "Категория": ["Супермаркеты", "ЖКХ"],
        "Описание": ["Магнит", "Электричество"],
    }
    df = pd.DataFrame(data)
    return df


# Список транзакций как список словарей
@pytest.fixture
def transactions_lst() -> list[dict]:
    return [
        {
            "Дата операции": "01.01.2018 00:00:00",
            "Сумма платежа": -100.50,
            "Статус": "OK",
            "Категория": "Цветы",
        },
        {"Дата операции": "05.01.2018 00:00:00", "Сумма платежа": -505.3, "Статус": "OK", "Категория": "ЖКХ"},
        {"Дата операции": "10.01.2018 00:00:00", "Сумма платежа": -5000.0, "Статус": "OK", "Категория": "nan"},
    ]


# Начальная дата
@pytest.fixture
def start_date() -> datetime:
    return datetime.strptime("01.01.2018 00:00:00", "%d.%m.%Y %H:%M:%S")


# Конечная дата
@pytest.fixture
def end_date() -> datetime:
    return datetime.strptime("31.01.2018 00:00:00", "%d.%m.%Y %H:%M:%S")
