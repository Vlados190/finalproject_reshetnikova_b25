ValutaTrade Hub

Консольный интерфейс для работы с валютным портфелем с поддержкой криптовалют и фиатных валют.

Структура проекта

valutatrade_hub/
├─ cli/ # Командный интерфейс
│ └─ interface.py
├─ core/ # Модели, usecases, исключения
│ ├─ usecases.py
│ ├─ models.py
│ ├─ exceptions.py
│ └─ logging_config.py
├─ parser_service/ # Получение курсов валют из API
│ ├─ updater.py
│ ├─ storage.py
│ └─ api_clients.py
├─ data/ # Хранилища JSON
│ ├─ users.json
│ ├─ portfolios.json
│ └─ rates.json
└─ pyproject.toml

Установка

```bash
# Установка зависимостей через Poetry
poetry install

# Запуск CLI
poetry run python -m valutatrade_hub.cli.interface <команда> [аргументы]
```

Примеры команд CLI
# Регистрация пользователя
python -m valutatrade_hub.cli.interface register --username USER --password PASS

# Вход в систему
python -m valutatrade_hub.cli.interface login --username USER --password PASS

# Просмотр портфеля
python -m valutatrade_hub.cli.interface show-portfolio --base USD

# Покупка валюты
python -m valutatrade_hub.cli.interface buy --currency BTC --amount 0.001

# Продажа валюты
python -m valutatrade_hub.cli.interface sell --currency BTC --amount 0.001

# Получение курса
python -m valutatrade_hub.cli.interface get-rate --from BTC --to USD

# Обновление курсов через Parser Service
python -m valutatrade_hub.cli.interface update-rates

# Просмотр кешированных курсов
python -m valutatrade_hub.cli.interface show-rates --top 5 --base USD

Примечания
Все данные пользователей и портфелей хранятся в data/.
TTL курсов валют и кеширование реализовано через rates.json.
Исключения (недостаточно средств, неизвестная валюта, ошибки API) корректно обрабатываются CLI

https://asciinema.org/connect/25a2620d-41dd-4505-ab38-b396853f2ca4 
