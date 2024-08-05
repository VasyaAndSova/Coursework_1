"""Основная логика для страницы «Сервисы»"""

import calendar
import json
import logging
import os
from collections import defaultdict
from datetime import datetime

ROOT = os.path.join(os.path.dirname(__file__), "..")

# Создание логера
logger = logging.getLogger(__name__)
# Создание хендлера
file_handler = logging.FileHandler(os.path.join(ROOT, "logs", "services.log"), "w")
# Создание форматера
file_formatter = logging.Formatter("%(asctime)s-%(funcName)s-%(levelname)s: %(message)s")
# Установка форматера
file_handler.setFormatter(file_formatter)
# Добавление хендлера к логеру
logger.addHandler(file_handler)
# Настройка уровня логирования
logger.setLevel(logging.DEBUG)


def profitable_categories_cashback(transactions: list[dict], year: int, month: int) -> str:
    """Функция сервиса принимает год, месяц для расчета и транзакции в формате списка словарей
    и возврвщает JSON с анализом, сколько на каждой категории можно заработать кешбэка в
    указанном месяце года."""
    num_days = calendar.monthrange(year, month)
    start_date = datetime(year=year, month=month, day=1, hour=0, minute=0, second=0)
    end_date = datetime(year=year, month=month, day=num_days[1], hour=23, minute=59, second=59)
    logger.info(f"Период для анализа: с {start_date} по {end_date}")
    filtered_dict: dict = defaultdict(float)
    logger.info("Начало фильтрации данных")
    count_transactions = 0
    # Фильтрация тразакций по периоду, и исключение пополнений и отмененных операций
    for tr in transactions:
        if (
            start_date <= datetime.strptime(tr["Дата операции"], "%d.%m.%Y %H:%M:%S") <= end_date
            and tr["Статус"] == "OK"
            and tr["Сумма платежа"] <= 0
        ):
            if str(tr["Категория"]) == "nan":
                filtered_dict["Другое"] += tr["Сумма платежа"] / 100 * (-1)
                count_transactions += 1
            else:
                filtered_dict[str(tr["Категория"])] += tr["Сумма платежа"] / 100 * (-1)
                count_transactions += 1
    logger.info(f"Найдено {count_transactions} транзакций в периоде")
    logger.info("Начало сортировки результата")
    # Сортировка словаря по значению и округление результатов
    sorted_list = sorted(filtered_dict.items(), key=lambda x: x[1], reverse=True)
    rounding_list = [(x[0], round(x[1], 2)) for x in sorted_list]
    result = dict(rounding_list)
    logger.info(f"Сортировка окончена, всего категорий {len(result)}")
    return json.dumps(result, indent=4)
