"""Модуль вспомогательных функций"""

import json
import logging
import os
from datetime import datetime

import pandas as pd
import requests
from dotenv import load_dotenv

ROOT = os.path.join(os.path.dirname(__file__), "..")
DEFAULT_CURRENCIES = ["USD"]
DEFAULT_STOCKS = ["AAPL"]
CURRENCY_URL = "https://api.apilayer.com/exchangerates_data/latest"
STOCK_URL = "https://financialmodelingprep.com/api/v3/quote-short/"

if not os.path.exists(os.path.join(ROOT, "logs")):
    os.mkdir(os.path.join(ROOT, "logs"))  # Создать папку «logs», если ее нет.

# Создание логера
logg = logging.getLogger(__name__)
# Создание хендлера
file_handler = logging.FileHandler(os.path.join(ROOT, "logs", "utils.log"), "w")
# Создание форматера
file_formatter = logging.Formatter("%(asctime)s-%(funcName)s-%(levelname)s: %(message)s")
# Установка форматера
file_handler.setFormatter(file_formatter)
# Добавление хендлера к логеру
logg.addHandler(file_handler)
# Настройка уровня логирования
logg.setLevel(logging.DEBUG)


def get_transactions(path_file: str) -> pd.DataFrame:
    """Функция получает данные о транзакциях из указанного Excel файла"""
    try:
        logg.info(f"Чтение файла «{path_file}»")
        df = pd.read_excel(os.path.join(ROOT, path_file))
        logg.info("Данные получены")
        return df
    except FileNotFoundError as e:
        logg.error(f"Ошибка открытия файла: {e}")
        return pd.DataFrame()  # Вернуть пустой DataFrame


def get_greeting(date: str) -> str:
    """Функция принимает дату в виде строки и возвращает строку
    с приетствим в соответствии со временем суток"""
    hour = datetime.strptime(date, "%Y-%m-%d %H:%M:%S").hour
    logg.info(f"Время {hour}ч.")
    if 6 <= hour < 12:
        logg.info("Это утро")
        return "Доброе утро"
    elif 12 <= hour < 18:
        logg.info("Это день")
        return "Добрый день"
    elif 17 <= hour <= 23:
        logg.info("Это вечер")
        return "Добрый вечер"
    else:
        logg.info("Это ночь")
        return "Доброй ночи"


def get_period(date: str) -> tuple[datetime, datetime]:
    """Функция принимает дату в виде строки и возвращает две даты в виде объекта
    datetime с начала месяца, на который выпадает входящая дата, по входящую дату."""
    date_obj = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    start_date = date_obj.replace(day=1, hour=0, minute=0, second=0)
    end_date = date_obj
    logg.info(f"Период для анализа: с {start_date} по {end_date}")
    return start_date, end_date


def filter_expenses_by_date(df: pd.DataFrame, start_date: datetime, end_date: datetime) -> pd.DataFrame:
    """Функция принимает DataFrame с данными о трнзакциях, начальную и конечную даты в виде объекта
    datetime. И возвращает DataFrame, отфильтрованный по указанному периоду, с исключением пополнений
    и отмененных операций"""
    try:
        logg.info("Начало фильтрации данных по периоду и исключение пополнений и отмененных операций")
        df = df[
            (df["Дата операции"].map(lambda x: datetime.strptime(x, "%d.%m.%Y %H:%M:%S")) >= start_date)
            & (df["Дата операции"].map(lambda x: datetime.strptime(x, "%d.%m.%Y %H:%M:%S")) <= end_date)
            & (df["Сумма платежа"] <= 0)
            & (df["Статус"] == "OK")
        ]
        logg.info("Данные отфильтрованы")
        return df
    except KeyError as e:
        logg.error(f"Ошибка обработки файла: {e}")
        return pd.DataFrame()  # Вернуть пустой DataFrame


def card_cost_analysis(df: pd.DataFrame) -> list[dict]:
    """Функция принимает DataFrame с данными о трнзакциях и возвращает список словарей
    с номером карты, расходами и кэшбэком"""
    try:
        logg.info("Начало обработки данных")
        # Новый DataDrame с необходимыми столбцами
        result_df = pd.DataFrame(
            {
                "last_digits": df["Номер карты"].map(lambda x: "No number" if str(x) == "nan" else x),
                "total_spent": df["Сумма платежа"] * (-1),
                "cashback": round(df["Сумма платежа"] / 100 * (-1), 2),
            }
        )
        # Группировка по номеру карты и суммирование расходов и кэшбека
        result_df = result_df.groupby("last_digits", as_index=False, dropna=False)[["total_spent", "cashback"]].sum()
        logg.info("Обработка завершена")
        return result_df.to_dict("records")
    except KeyError as e:
        logg.error(f"Ошибка обработки данных: {e}")
        return []


def get_top_n_expenses(df: pd.DataFrame, n: int = 5) -> list[dict]:
    """Функция принимает DataFrame с данными о трнзакциях и возвращает список словарей с N
    транзакциями, имеющими наибольшие расходы."""
    try:
        logg.info("Начало обработки данных")
        # Новый DataFrame с необходимыми столбцами
        result_df = pd.DataFrame(
            {
                "date": df["Дата операции"].map(lambda x: x[:10]),
                "amount": df["Сумма платежа"] * (-1),
                "category": df["Категория"],
                "description": df["Описание"],
            }
        )
        # Сортировка по убыванию расходов и отбор первых N результатов
        result_df = result_df.sort_values("amount", ignore_index=True, ascending=False).head(n)
        logg.info("Обработка завершена")
        return result_df.to_dict("records")
    except KeyError as e:
        logg.error(f"Ошибка обработки данных: {e}")
        return []


def get_user_settings(path_file: str) -> tuple[list[str], list[str]]:
    """Функция принимает путь к файлу с пользовательскими настройками
    и возвращает список с user_currencies и список с user_stocks"""
    try:
        logg.info(f"Открытие файла «{path_file}»")
        with open(os.path.join(ROOT, path_file)) as file:
            logg.info("Файл открыт")
            try:
                logg.info(f"Загрузка файла «{path_file}»")
                user_settings = json.load(file)
                logg.info("Файл загружен")
            except json.JSONDecodeError as e:
                logg.error(f"Ошибка загрузки файла: {e}")
                logg.error("Применены настройки по умолчанию")
                return DEFAULT_CURRENCIES, DEFAULT_STOCKS
    except FileNotFoundError as e:
        logg.error(f"Ошибка открытия файла: {e}")
        logg.error("Применены настройки по умолчанию")
        return DEFAULT_CURRENCIES, DEFAULT_STOCKS

    user_currencies = user_settings.get("user_currencies", DEFAULT_CURRENCIES)
    user_stocks = user_settings.get("user_stocks", DEFAULT_STOCKS)
    logg.info("Настройки успешно получены")
    return user_currencies, user_stocks


def get_exchange_rate(currencies: list[str]) -> list[dict]:
    """Функция принимает список валют для отображения, делает соответствующий
    запрос API и возвращает список словарей с курсами валют"""
    load_dotenv(os.path.join(ROOT, ".env"))
    headers = {"apikey": os.getenv("CURRENCY_APIKEY")}
    params = {"base": "RUB", "symbols": ",".join(currencies)}
    try:
        logg.info("Запрос курса валют у API сервера")
        response = requests.get(CURRENCY_URL, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            logg.info("Курс валют получен")
            return [dict(currency=x, rate=round(1 / y, 2)) for x, y in response.json()["rates"].items()]
        else:
            logg.error("Ошибка ответа сервера")
            logg.error("Установлены нулевые курсы валют")
            return [dict(currency=x, rate=0.0) for x in currencies]
    except requests.exceptions.RequestException:
        logg.error("Ошибка запроса")
        logg.error("Установлены нулевые курсы валют")
        return [dict(currency=x, rate=0.0) for x in currencies]


def get_stocks_price(stocks: list[str]) -> list[dict]:
    """Функция принимает список акций для отображения, делает соответствующий
    запрос API и возвращает список словарей с ценами на акции"""
    load_dotenv(os.path.join(ROOT, ".env"))
    url = STOCK_URL + ",".join(stocks)
    params = {"apikey": os.getenv("STOCK_APIKEY")}
    try:
        logg.info("Запрос цен на акции у API сервера")
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            logg.info("Цены на акции получены")
            return [dict(stock=x["symbol"], price=x["price"]) for x in response.json()]
        else:
            logg.error("Ошибка ответа сервера")
            logg.error("Установлены нулевые цены на акции")
            return [dict(stock=x, price=0.0) for x in stocks]
    except requests.exceptions.RequestException:
        logg.error("Ошибка запроса")
        logg.error("Установлены нулевые цены на акции")
        return [dict(stock=x, price=0.0) for x in stocks]
