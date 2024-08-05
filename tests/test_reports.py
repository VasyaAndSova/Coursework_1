"""Тесты модуля reports"""

import json
import os

import pandas as pd

from src.reports import save_reports, spending_by_category

ROOT = os.path.join(os.path.dirname(__file__), "..")


# Тест функции spending_by_category
def test_spending_by_category(transactions: pd.DataFrame) -> None:
    result = spending_by_category(transactions, "Супермаркеты", "2018-02-25 00:00:00")
    assert json.loads(result) == [
        {
            "Дата операции": "01.01.2018 00:00:00",
            "Сумма платежа": -100.50,
            "Статус": "OK",
            "Номер карты": "*4516",
            "Категория": "Супермаркеты",
            "Описание": "Магнит",
        }
    ]


# Тест функции spending_by_category с пустым результатом
def test_spending_by_category_empty(transactions: pd.DataFrame) -> None:
    result = spending_by_category(transactions, "Супермаркеты")
    assert json.loads(result) == []


# Тест функции spending_by_category с неверным Датафреймом
def test_spending_by_category_error() -> None:
    result = spending_by_category(pd.DataFrame(), "Супермаркеты", "2018-02-25 00:00:00")
    assert json.loads(result) == []


# Тест декоратора save_reports
def test_save_reports() -> None:
    @save_reports("test_report.xlsx")
    def example_func() -> str:
        return json.dumps([{"key": "A", "value": 1}, {"key": "B", "value": 2}])

    example_func()
    df = pd.read_excel(os.path.join(ROOT, "reports", "test_report.xlsx"))
    assert df.to_dict() == {"key": {0: "A", 1: "B"}, "value": {0: 1, 1: 2}}


# Тест декоратора save_reports с файлом по умолчанию
def test_save_reports_default() -> None:
    @save_reports()
    def example_func() -> str:
        return json.dumps([{"key": "A", "value": 1}, {"key": "B", "value": 2}])

    example_func()
    df = pd.read_excel(os.path.join(ROOT, "reports", "example_func.xlsx"))
    assert df.to_dict() == {"key": {0: "A", 1: "B"}, "value": {0: 1, 1: 2}}
