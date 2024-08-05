"""Модуль генерации отчетов"""

import json
import logging
import os
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Optional

import pandas as pd
from dateutil.relativedelta import relativedelta

from src.utils import filter_expenses_by_date

ROOT = os.path.join(os.path.dirname(__file__), "..")

# Создание логера
logger = logging.getLogger(__name__)
# Создание хендлера
file_handler = logging.FileHandler(os.path.join(ROOT, "logs", "reports.log"), "w")
# Создание форматера
file_formatter = logging.Formatter("%(asctime)s-%(funcName)s-%(levelname)s: %(message)s")
# Установка форматера
file_handler.setFormatter(file_formatter)
# Добавление хендлера к логеру
logger.addHandler(file_handler)
# Настройка уровня логирования
logger.setLevel(logging.DEBUG)


def save_reports(file_name: Optional[str] = None) -> Callable:
    """Декоратор для функций-отчетов, который
    записывает в файл ее результат."""

    def wrapper(func: Callable) -> Callable:
        @wraps(func)
        def inner(*args: tuple, **kwargs: dict) -> Any:
            result = func(*args, **kwargs)
            data = json.loads(result)
            if not os.path.exists(os.path.join(ROOT, "reports")):
                os.mkdir(os.path.join(ROOT, "reports"))
            if data:
                df = pd.DataFrame(data)
                if file_name is None:
                    df.to_excel(os.path.join(ROOT, "reports", f"{func.__name__}.xlsx"), engine="openpyxl", index=False)
                    logger.info(f"Отчет сохранен в файле {func.__name__}.xlsx")
                else:
                    df.to_excel(os.path.join(ROOT, "reports", file_name), engine="openpyxl", index=False)
                    logger.info(f"Отчет сохранен в файле {file_name}")
            else:
                print(f"Расходов по категории «{str(args[1]).lower()}» за указанный период не найдено")
                logger.info("Нет данных для сохранения")
            return result

        return inner

    return wrapper


@save_reports("category_report.xlsx")
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> str:
    """Функция принимает на вход: DataFrame с транзакциями, название категории,
    опциональную дату. Если дата не передана, то берется текущая дата.
    Возвращает траты по заданной категории за последние три месяца от переданной даты"""
    if date is None:
        end_date = datetime.now()
    else:
        end_date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    start_date = end_date - relativedelta(months=3)
    logger.info(f"Период для анализа: с {start_date} по {end_date}")
    # Фильтрация DataFrame по периоду, и исключение пополнений и отмененных операций
    logger.info("Фильтрация данных по периоду")
    transactions = filter_expenses_by_date(transactions, start_date, end_date)
    try:
        logger.info("Фильтрация по категории")
        transactions = transactions[transactions["Категория"].map(lambda x: str(x).lower()) == category.lower()]
        logger.info("Сортировка по дате")
        transactions["Дата операции"] = transactions["Дата операции"].map(
            lambda x: datetime.strptime(x, "%d.%m.%Y %H:%M:%S")
        )
        transactions = transactions.sort_values("Дата операции")
        transactions["Дата операции"] = transactions["Дата операции"].map(
            lambda x: datetime.strftime(x, "%d.%m.%Y %H:%M:%S")
        )
        logger.info("Обработка данных завершена")
        return json.dumps(transactions.to_dict("records"), indent=4)
    except KeyError as e:
        logger.error(f"Ошибка обработки данных: {e}")
        return json.dumps([], indent=4)
