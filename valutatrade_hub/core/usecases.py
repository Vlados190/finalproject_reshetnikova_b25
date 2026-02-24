import json
import os
from datetime import datetime
from .models import User, Portfolio, Wallet

DATA_DIR = os.path.join(os.path.dirname(__file__), "../../data")
USERS_FILE = os.path.join(DATA_DIR, "users.json")
PORTFOLIOS_FILE = os.path.join(DATA_DIR, "portfolios.json")


def _load_json(file_path: str):
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read().strip()
        if not content:
            return []
        return json.loads(content)


def _save_json(file_path: str, data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def register_user(username: str, password: str) -> User:
    users = _load_json(USERS_FILE)
    if any(u["username"] == username for u in users):
        raise ValueError(f"Имя пользователя '{username}' уже занято")
    user_id = max((u["user_id"] for u in users), default=0) + 1
    user = User(user_id=user_id, username=username, password=password)
    users.append({
        "user_id": user.user_id,
        "username": user.username,
        "hashed_password": user._hashed_password,
        "salt": user._salt,
        "registration_date": user.registration_date
    })
    _save_json(USERS_FILE, users)

    portfolios = _load_json(PORTFOLIOS_FILE)
    portfolios.append({"user_id": user.user_id, "wallets": {}})
    _save_json(PORTFOLIOS_FILE, portfolios)
    return user


def login_user(username: str, password: str) -> User:
    users = _load_json(USERS_FILE)
    for u in users:
        if u["username"] == username:
            user = User(
                user_id=u["user_id"],
                username=u["username"],
                password=password,
                registration_date=u.get("registration_date")
            )
            user._salt = u["salt"]
            user._hashed_password = u["hashed_password"]
            if user.verify_password(password):
                return user
            else:
                raise ValueError("Неверный пароль")
    raise ValueError(f"Пользователь '{username}' не найден")


def get_user_portfolio(user: User) -> Portfolio:
    portfolios = _load_json(PORTFOLIOS_FILE)
    data = next((p for p in portfolios if p["user_id"] == user.user_id), None)
    wallets = {}
    if data:
        for code, w in data.get("wallets", {}).items():
            wallets[code] = Wallet(code, w.get("balance", 0.0))
    return Portfolio(user, wallets)


def save_user_portfolio(portfolio: Portfolio):
    portfolios = _load_json(PORTFOLIOS_FILE)
    found = False
    for p in portfolios:
        if p["user_id"] == portfolio.user.user_id:
            p["wallets"] = {c: {"balance": w.balance} for c, w in portfolio.wallets.items()}
            found = True
            break
    if not found:
        portfolios.append({
            "user_id": portfolio.user.user_id,
            "wallets": {c: {"balance": w.balance} for c, w in portfolio.wallets.items()}
        })
    _save_json(PORTFOLIOS_FILE, portfolios)


def buy_currency(user: User, currency_code: str, amount: float):
    if amount <= 0:
        raise ValueError("Сумма покупки должна быть больше 0")
    portfolio = get_user_portfolio(user)
    if currency_code not in portfolio.wallets:
        portfolio.add_currency(currency_code)
    wallet = portfolio.get_wallet(currency_code)
    wallet.deposit(amount)
    save_user_portfolio(portfolio)


def sell_currency(user: User, currency_code: str, amount: float):
    portfolio = get_user_portfolio(user)
    wallet = portfolio.get_wallet(currency_code)
    if not wallet:
        raise ValueError(f"Нет кошелька для валюты {currency_code}")
    wallet.withdraw(amount)
    save_user_portfolio(portfolio)


def get_rate(from_code: str, to_code: str) -> float:
    return 1.0