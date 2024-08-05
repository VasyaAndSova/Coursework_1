"""Тесты модуля views"""

import json
from unittest.mock import Mock

import pandas as pd

from src import utils
from src.views import main_page


# Тест функции main_page
def test_main_page(transactions: pd.DataFrame) -> None:
    mock_currency = Mock(
        return_value=[
            {"currency": "USD", "rate": 87.24},
        ]
    )
    mock_stock = Mock(
        return_value=[
            {"stock": "AAPL", "price": 209.3},
        ]
    )
    utils.get_exchange_rate = mock_currency
    utils.get_stocks_price = mock_stock
    result = main_page(transactions, "2018-02-17 12:20:00")
    assert json.loads(result) == {
        "greeting": "Добрый день",
        "cards": [
            {"last_digits": "*7815", "total_spent": 505.3, "cashback": 5.05},
        ],
        "top_transactions": [
            {"date": "01.02.2018", "amount": 505.3, "category": "ЖКХ", "description": "Электричество"},
        ],
        "currency_rates": [
            {"currency": "USD", "rate": 87.24},
        ],
        "stock_prices": [
            {"stock": "AAPL", "price": 209.3},
        ],
    }
    mock_currency.assert_called_once()
    mock_stock.assert_called_once()
