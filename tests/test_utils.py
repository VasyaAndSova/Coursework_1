"""Тесты модуля utils"""

import json
import os
from datetime import datetime
from unittest.mock import Mock, patch

import pandas as pd
import pytest
import requests

from src.utils import (
    card_cost_analysis,
    filter_expenses_by_date,
    get_exchange_rate,
    get_greeting,
    get_period,
    get_stocks_price,
    get_top_n_expenses,
    get_transactions,
    get_user_settings,
)


# Тест функции get_transactions
def test_get_transactions() -> None:
    result = get_transactions(os.path.join("data", "operations.xlsx"))
    assert result.shape == (6705, 15)


# Тест функции get_transactions с несуществующим файлом
def test_get_transactions_error() -> None:
    result = get_transactions("transactions.xlsx")
    assert result.shape == (0, 0)


# Тест фунции get_greeting
@pytest.mark.parametrize(
    "date, greeting",
    [
        ("2021-01-10 08:30:00", "Доброе утро"),
        ("2022-04-15 13:20:00", "Добрый день"),
        ("2023-09-20 18:40:00", "Добрый вечер"),
        ("2024-12-31 01:10:00", "Доброй ночи"),
    ],
)
def test_get_greeting(date: str, greeting: str) -> None:
    result = get_greeting(date)
    assert result == greeting


# Тест функции get_period
@pytest.mark.parametrize(
    "date, start_date",
    [
        ("2021-01-10 08:30:00", "2021-01-01 00:00:00"),
        ("2022-04-15 13:20:00", "2022-04-01 00:00:00"),
        ("2023-09-20 18:40:00", "2023-09-01 00:00:00"),
        ("2024-12-31 01:10:00", "2024-12-01 00:00:00"),
    ],
)
def test_get_period(date: str, start_date: str) -> None:
    result = get_period(date)
    assert datetime.strftime(result[0], "%Y-%m-%d %H:%M:%S") == start_date
    assert datetime.strftime(result[1], "%Y-%m-%d %H:%M:%S") == date


# Тест функции filter_expenses_by_date
def test_filter_expenses_by_date(transactions: pd.DataFrame, start_date: datetime, end_date: datetime) -> None:
    result = filter_expenses_by_date(transactions, start_date, end_date)
    assert result["Дата операции"].iloc[0] == "01.01.2018 00:00:00"
    assert result["Сумма платежа"].iloc[0] == -100.50
    assert result["Статус"].iloc[0] == "OK"
    assert result["Номер карты"].iloc[0] == "*4516"


# Тест функции filter_expenses_by_date с пустым датафреймом
def test_filter_expenses_by_date_empty(start_date: datetime, end_date: datetime) -> None:
    result = filter_expenses_by_date(pd.DataFrame(), start_date, end_date)
    assert result.shape == (0, 0)


# Тест функции card_cost_analysis
def test_card_cost_analysis(transactions: pd.DataFrame) -> None:
    result = card_cost_analysis(transactions)
    assert result == [
        {"last_digits": "*4516", "total_spent": 100.50, "cashback": 1.0},
        {"last_digits": "*7815", "total_spent": 505.30, "cashback": 5.05},
    ]


# Тест функции card_cost_analysis с пустым датафреймом
def test_card_cost_analysis_empty() -> None:
    result = card_cost_analysis(pd.DataFrame())
    assert result == []


# Тест функции get_top_n_expenses
def test_get_top_n_expenses(transactions: pd.DataFrame) -> None:
    result = get_top_n_expenses(transactions, 1)
    assert result == [{"date": "01.02.2018", "amount": 505.3, "category": "ЖКХ", "description": "Электричество"}]


# Тест функции get_top_n_expenses с пустым датафреймом
def test_get_top_n_expenses_empty() -> None:
    result = get_top_n_expenses(pd.DataFrame())
    assert result == []


# Тест функции get_user_settings
def test_get_user_settings() -> None:
    result = get_user_settings("user_settings.json")
    assert result == (["USD", "EUR"], ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"])


# Тест функции get_user_settings с несуществующим файлом
def test_get_user_settings_error() -> None:
    result = get_user_settings("settings.json")
    assert result == (["USD"], ["AAPL"])


# Тест функции get_user_settings с поврежденным файлом json
@patch("json.load")
def test_get_user_settings_bad_json(mock_json: Mock) -> None:
    mock_json.side_effect = json.decoder.JSONDecodeError("", "}", 0)
    result = get_user_settings("user_settings.json")
    assert result == (["USD"], ["AAPL"])
    mock_json.assert_called_once()


class MockRequestsGet:

    def __init__(self, status_code: int, ret_value: dict | list[dict]) -> None:
        self.status_code = status_code
        self.ret_value = ret_value

    def json(self) -> dict | list[dict]:
        return self.ret_value


# Тест функции get_exchange_rate
@patch("requests.get")
def test_get_exchange_rate(mock_get: Mock) -> None:
    mock_get.return_value = MockRequestsGet(
        status_code=200,
        ret_value={
            "success": True,
            "timestamp": 1718906044,
            "base": "RUB",
            "date": "2024-06-20",
            "rates": {"USD": 0.011462},
        },
    )
    result = get_exchange_rate(["USD"])
    assert result == [
        {"currency": "USD", "rate": 87.24},
    ]
    mock_get.assert_called_once()


# Тест функции get_exchange_rate с ошибкой ответа сервера
@patch("requests.get")
def test_get_exchange_rate_bad_answer(mock_get: Mock) -> None:
    mock_get.return_value = MockRequestsGet(status_code=400, ret_value={})
    result = get_exchange_rate(["USD"])
    assert result == [
        {"currency": "USD", "rate": 0.0},
    ]
    mock_get.assert_called_once()


# Тест функции get_exchange_rate с ошибкой запроса
@patch("requests.get")
def test_get_exchange_rate_error(mock_get: Mock) -> None:
    mock_get.side_effect = requests.exceptions.RequestException
    result = get_exchange_rate(["USD"])
    assert result == [
        {"currency": "USD", "rate": 0.0},
    ]
    mock_get.assert_called_once()


# Тест функции get_stocks_price
@patch("requests.get")
def test_get_stocks_price(mock_get: Mock) -> None:
    mock_get.return_value = MockRequestsGet(
        status_code=200, ret_value=[{"symbol": "AAPL", "price": 209.3, "volume": 47239002}]
    )
    result = get_stocks_price(["AAPL"])
    assert result == [
        {"stock": "AAPL", "price": 209.3},
    ]
    mock_get.assert_called_once()


# Тест функции get_stocks_price с ошибкой ответа сервера
@patch("requests.get")
def test_get_stocks_price_bad_answer(mock_get: Mock) -> None:
    mock_get.return_value = MockRequestsGet(status_code=400, ret_value=[])
    result = get_stocks_price(["AAPL"])
    assert result == [
        {"stock": "AAPL", "price": 0.0},
    ]
    mock_get.assert_called_once()


# Тест функции get_stocks_price с ошибкой запроса
@patch("requests.get")
def test_get_stocks_price_error(mock_get: Mock) -> None:
    mock_get.side_effect = requests.exceptions.RequestException
    result = get_stocks_price(["AAPL"])
    assert result == [
        {"stock": "AAPL", "price": 0.0},
    ]
    mock_get.assert_called_once()
