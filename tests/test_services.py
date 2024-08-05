"""Тесты модуля services"""

import json

from src.services import profitable_categories_cashback


# Тест функции profitable_categories_cashback
def test_profitable_categories_cashback(transactions_lst: list[dict]) -> None:
    result = profitable_categories_cashback(transactions_lst, 2018, 1)
    assert json.loads(result) == {"Другое": 50.0, "ЖКХ": 5.05, "Цветы": 1.0}


# Тест функции profitable_categories_cashback с нулевым результатом
def test_profitable_categories_cashback_empty(transactions_lst: list[dict]) -> None:
    result = profitable_categories_cashback(transactions_lst, 2020, 1)
    assert json.loads(result) == {}
