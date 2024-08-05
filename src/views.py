"""Основная логика для страницы «Главная»"""

import json

import pandas as pd

from src import utils

SETTINGS_FILE = "user_settings.json"


def main_page(data_frame: pd.DataFrame, date: str) -> str:
    """Функция принимает на вход DataFrame с транзакциями и строку с датой и временем
    в формате: YYYY-MM-DD HH:MM:SS и возвращает JSON-ответ содержащий:
             Приветствие,
             Расходы и кешбек по картам,
             Топ-5 транзакций по сумме платежа.
             Курс валют.
             Стоимость акций из S&P500."""
    greeting = utils.get_greeting(date)
    start_date, end_date = utils.get_period(date)
    data_frame = utils.filter_expenses_by_date(data_frame, start_date, end_date)
    expenses = utils.card_cost_analysis(data_frame)
    top_transactions = utils.get_top_n_expenses(data_frame, n=5)
    user_currencies, user_stocks = utils.get_user_settings(SETTINGS_FILE)
    currency_rates = utils.get_exchange_rate(user_currencies)
    stock_prices = utils.get_stocks_price(user_stocks)

    answer = {
        "greeting": greeting,
        "cards": expenses,
        "top_transactions": top_transactions,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices,
    }
    return json.dumps(answer, indent=4)
