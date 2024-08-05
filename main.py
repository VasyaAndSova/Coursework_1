"""Основная логика программы"""

import calendar
import json
import os
from datetime import datetime

from src.reports import spending_by_category
from src.services import profitable_categories_cashback
from src.utils import get_transactions
from src.views import main_page

FILE_SOURSE = os.path.join("data", "operations.xlsx")
FILE_TO_SAVE_REPORT = "category_report.xlsx"

transactions_df = get_transactions(FILE_SOURSE)
transactions_lst = transactions_df.to_dict("records")


def get_year() -> int:
    """Функция получает у пользователя год"""
    while True:
        try:
            year = int(input("Введите год: "))
            if 1 <= year <= 9999:
                return year
        except ValueError:
            pass


def get_month() -> int:
    """Функция получает у пользователя месяц"""
    while True:
        try:
            month = int(input("Введите месяц: "))
            if 1 <= month <= 12:
                return month
        except ValueError:
            pass


def get_day(year: int, month: int) -> int:
    """Функция получает у пользователя день"""
    while True:
        try:
            day = int(input("Введите день: "))
            if 1 <= day <= calendar.monthrange(year, month)[1]:
                return day
        except ValueError:
            pass


def show_main_page() -> None:
    """Функция отображения страницы «Главная»"""
    print("Главная страница")
    # Запрос даты у ползователя
    year = get_year()
    month = get_month()
    day = get_day(year, month)
    # Полученная дата + текущее время
    date = datetime.now()
    date = date.replace(year=year, month=month, day=day)
    date_str = datetime.strftime(date, "%Y-%m-%d %H:%M:%S")
    # Запрос информации для отображения
    data = json.loads(main_page(transactions_df, date_str))
    # Прветствие
    print("\n", data["greeting"], "\n")

    print("Расходы в зтом месяце:")
    if not data["cards"]:
        print("  Не найдено")
    for card in data["cards"]:
        print("Карта:", card["last_digits"])
        print("Расходы:", card["total_spent"])
        print("Кэшбэк:", card["cashback"], "\n")

    print("Топ 5 расходов в этом месяце:")
    if not data["top_transactions"]:
        print("  Не найдено")
    for trans in data["top_transactions"]:
        print(trans["date"], "Потрачено:", trans["amount"])
        print("Категория:", trans["category"])
        print(trans["description"], "\n")

    print("Курсы валют:")
    for currency in data["currency_rates"]:
        print(currency["currency"], currency["rate"])
    print()

    print("Цены на акции:")
    for stock in data["stock_prices"]:
        print(stock["stock"], stock["price"])
    print()


def show_servces() -> None:
    """Функция отображения категории «Сервисы»"""
    print(
        """Сервис позволяет проанализировать, какие категории были наиболее
выгодными для выбора в качестве категорий повышенного кешбэка."""
    )
    # Запрос даты у ползователя
    year = get_year()
    month = get_month()
    # Запрос информации для отображения
    categories_dict_ = profitable_categories_cashback(transactions_lst, year, month)
    categories_dict = json.loads(categories_dict_)
    # Отображение
    if categories_dict:
        print(f"В указанном месяце найдено {len(categories_dict)} категорий расходов.")
        print("На каждой категории можно заработать кешбэка:")
        for key, value in categories_dict.items():
            print(key, value)
    else:
        print("В указанном месяце расходов не найдено")


def show_reports() -> None:
    """Функция отображения категории «Отчеты»"""
    print(
        """Отчеты позволяют отобразить траты по заданной категории за
последние три месяца (от переданной даты). И сохранить их в файл."""
    )
    # Запрос категории у ползователя
    category = input("Введите категорию: ")

    if input("Использовать текущую дату? да/нет: ").lower() == "да":
        print(f"Выбрана текущая дата: {datetime.now()}")
        transactions = spending_by_category(transactions_df, category)

    else:
        # Запрос даты у ползователя
        year = get_year()
        month = get_month()
        day = get_day(year, month)
        date_str = datetime.strftime(datetime(year, month, day), "%Y-%m-%d %H:%M:%S")
        print(f"Выбрана дата: {date_str}")
        # Запрос информации для отображения
        transactions = spending_by_category(transactions_df, category, date_str)
    transactions = json.loads(transactions)
    # Отображение
    if transactions:
        print(f"Расходов по категории «{category.lower()}» за указанный период: {len(transactions)}\n")
        for tr in transactions:
            print("Дата:", tr["Дата операции"][:10], "Номер карты:", tr["Номер карты"])
            print("Описание:", tr["Описание"])
            print("Сумма:", tr["Сумма платежа"], "\n")


def main() -> None:
    """Главная функция (точка входа)"""
    while True:
        print("Выберите задачу: (Главная, Сервисы, Отчеты)")
        task = input(">>").lower()
        if task == "главная":
            show_main_page()
        elif task == "сервисы":
            show_servces()
        elif task == "отчеты":
            show_reports()


if __name__ == "__main__":
    main()
