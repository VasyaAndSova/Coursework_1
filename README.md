# Курсовой проект по Python
## Описание
Приложение для анализа транзакций, которые находятся в Excel-файле.
## Задачи
1. Веб-страницы:
   + Главная
2. Сервисы:
   + Выгодные категории повышенного кешбэка
3. Отчеты:
   + Траты по категории
## Модули
* Модуль веб-страниц `views.py`
  + Функция главной страницы `main_page`
* Модуль сервисов `services.py`
  + Фунция выгодных категорий повышенного кешбэка `profitable_categories_cashback`
* Модуль отчетов `reports.py`
  + Функция трат по категориям `spending_by_category`
  + Декоратор для функций-отчетов, который записывает в файл результат,
  	который возвращает функция, формирующая отчет `save_reports`
* Модуль вспомоготельных функций `utils.py`
  + Функция получения DataFrame из файла`get_transactions`
  + Функция получения приветствия по времени суток `get_greeting`
  + Функция получения начальной и конечной даты для фильтрациии`get_period`
  + Функция фильтрации DataFrame по дате `filter_expenses_by_date`
  + Функция анализа трат по картам `card_cost_analysis`
  + Функция получения топ N трат `get_top_n_expenses`
  + Функция получения ползовательских настроек из файла`get_user_settings`
  + Функция получения курса валют `get_exchange_rate`
  + Функция получения цен на акции`get_stocks_price`
* main.py
  + `get_year` Получает у ползователя год
  + `get_month` Получает у ползователя месяц
  + `get_day` Получает у ползователя день
  + `show_main_page` Отображает главную страницу
  + `show_servces` Отображает сервисы
  + `show_reports` Отображает отчеты
## Логирование
Проект имеет логирование с использованием logging
в следующих модулях:
* services.py
* reports.py
* utils.py
## Линтеры
* `flake8`
* `black`
* `mypy`
* `isort`
* `types-requests`
* `pandas-stubs`
* `types-python-dateutil`
## Зависимости
* `requests`
* `python-dotenv`
* `pandas`
* `openpyxl`
* `xlrd`
## Установка
1. Клонировать проект
```
<https://github.com/VasyaAndSova/Coursework_1.git>
```
2. Установить зависимости
```
poetry install
```
3. Регистрация и получение токена:
	<https://apilayer.com/marketplace/exchangerates_data-api>
4. Регистрация и получение токена:
	<https://site.financialmodelingprep.com/>
5. Создать файл .env из копии  .env.example и заменить
    значения переменных реальными данными (Токенами)
## Запуск
main.py
## Тестирование
Проект покрыт юнит-тестами
* Запуск теста: `pytest`
* Покрытие кода: `pytest --cov`
