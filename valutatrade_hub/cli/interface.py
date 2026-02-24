import argparse
import sys
import os
import json
from ..core.usecases import (
    register_user,
    login_user,
    get_user_portfolio,
    buy_currency,
    sell_currency,
    get_rate,
    _load_json,
    USERS_FILE,
    User
)
from ..parser_service.updater import RatesUpdater
from ..parser_service.storage import RatesStorage
from ..core.exceptions import ApiRequestError

# ===== Файл для хранения текущей сессии =====
SESSION_FILE = os.path.join(os.path.dirname(__file__), "../../data/session.json")
current_user = None

# ===== Функции работы с сессией =====
def save_session(user: User):
    os.makedirs(os.path.dirname(SESSION_FILE), exist_ok=True)
    with open(SESSION_FILE, "w", encoding="utf-8") as f:
        json.dump({"user_id": user.user_id}, f)

def load_session():
    if not os.path.exists(SESSION_FILE):
        return None
    with open(SESSION_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    user_id = data.get("user_id")
    if not user_id:
        return None
    # Ищем пользователя в users.json
    users = _load_json(USERS_FILE)
    u = next((u for u in users if u["user_id"] == user_id), None)
    if u:
        user = User(user_id=u["user_id"], username=u["username"], password="")
        user._salt = u["salt"]
        user._hashed_password = u["hashed_password"]
        return user
    return None

# ===== MAIN CLI =====
def main():
    global current_user
    current_user = load_session()

    parser = argparse.ArgumentParser(description="Консольный интерфейс валютного кошелька")
    subparsers = parser.add_subparsers(dest="command")

    # --- Регистрация и логин ---
    reg_parser = subparsers.add_parser("register", help="Создать нового пользователя")
    reg_parser.add_argument("--username", required=True)
    reg_parser.add_argument("--password", required=True)

    login_parser = subparsers.add_parser("login", help="Войти в систему")
    login_parser.add_argument("--username", required=True)
    login_parser.add_argument("--password", required=True)

    subparsers.add_parser("logout", help="Выйти из системы")

    # --- Портфель ---
    portfolio_parser = subparsers.add_parser("show-portfolio", help="Показать портфель пользователя")
    portfolio_parser.add_argument("--base", default="USD")

    # --- Покупка/Продажа ---
    buy_parser = subparsers.add_parser("buy", help="Купить валюту")
    buy_parser.add_argument("--currency", required=True)
    buy_parser.add_argument("--amount", required=True, type=float)

    sell_parser = subparsers.add_parser("sell", help="Продать валюту")
    sell_parser.add_argument("--currency", required=True)
    sell_parser.add_argument("--amount", required=True, type=float)

    # --- Получить курс ---
    rate_parser = subparsers.add_parser("get-rate", help="Получить курс валют")
    rate_parser.add_argument("--from", dest="from_code", required=True)
    rate_parser.add_argument("--to", dest="to_code", required=True)

    # --- Parser Service команды ---
    update_parser = subparsers.add_parser("update-rates", help="Обновить курсы валют")
    update_parser.add_argument("--source", choices=["coingecko", "exchangerate"], default="all")

    show_parser = subparsers.add_parser("show-rates", help="Показать курсы из кеша")
    show_parser.add_argument("--currency", type=str)
    show_parser.add_argument("--top", type=int)
    show_parser.add_argument("--base", type=str, default="USD")

    args = parser.parse_args()

    try:
        # --- REGISTER ---
        if args.command == "register":
            user = register_user(args.username, args.password)
            print(f"Пользователь '{user.username}' зарегистрирован (id={user.user_id}). Войдите: login --username {user.username} --password ****")

        # --- LOGIN ---
        elif args.command == "login":
            user = login_user(args.username, args.password)
            current_user = user
            save_session(user)
            print(f"Вы вошли как '{user.username}'")

        # --- LOGOUT ---
        elif args.command == "logout":
            if current_user:
                print(f"Пользователь '{current_user.username}' вышел")
                current_user = None
                if os.path.exists(SESSION_FILE):
                    os.remove(SESSION_FILE)
            else:
                print("Сначала выполните login")

        # --- SHOW PORTFOLIO ---
        elif args.command == "show-portfolio":
            if not current_user:
                print("Сначала выполните login")
                sys.exit(1)
            portfolio = get_user_portfolio(current_user)
            total = 0.0
            print(f"Портфель пользователя '{current_user.username}' (база: {args.base}):")
            for code, wallet in portfolio.wallets.items():
                converted = wallet.balance  # курс 1:1 для простоты
                total += converted
                print(f"- {code}: {wallet.balance:.4f} → {converted:.2f} {args.base}")
            print("-" * 40)
            print(f"ИТОГО: {total:.2f} {args.base}")

        # --- BUY ---
        elif args.command == "buy":
            if not current_user:
                print("Сначала выполните login")
                sys.exit(1)
            buy_currency(current_user, args.currency, args.amount)
            print(f"Куплено {args.amount} {args.currency} для пользователя '{current_user.username}'")

        # --- SELL ---
        elif args.command == "sell":
            if not current_user:
                print("Сначала выполните login")
                sys.exit(1)
            sell_currency(current_user, args.currency, args.amount)
            print(f"Продано {args.amount} {args.currency} для пользователя '{current_user.username}'")

        # --- GET RATE ---
        elif args.command == "get-rate":
            rate_value = get_rate(args.from_code.upper(), args.to_code.upper())
            print(f"Курс {args.from_code.upper()} → {args.to_code.upper()}: {rate_value}")

        # --- UPDATE RATES ---
        elif args.command == "update-rates":
            try:
                updater = RatesUpdater()
                updater.run_update()
                print("Обновление курсов завершено")
            except ApiRequestError as e:
                print(f"Ошибка обновления: {e}")

        # --- SHOW RATES ---
        elif args.command == "show-rates":
            storage = RatesStorage()
            if not os.path.exists(storage.rates_file):
                print("Локальный кеш курсов пуст. Выполните 'update-rates'")
                sys.exit(1)
            with open(storage.rates_file, "r", encoding="utf-8") as f:
                snapshot = json.load(f)
            pairs = snapshot.get("pairs", {})
            filtered = {k: v for k, v in pairs.items() if args.currency is None or k.startswith(args.currency.upper())}
            top_n = args.top or len(filtered)
            sorted_pairs = sorted(filtered.items(), key=lambda x: x[1]["rate"], reverse=True)[:top_n]
            print(f"Rates from cache (updated at {snapshot.get('last_refresh')}):")
            for k, v in sorted_pairs:
                print(f"- {k}: {v['rate']}")

        else:
            parser.print_help()

    except Exception as e:
        print(f"Ошибка: {e}")


if __name__ == "__main__":
    main()