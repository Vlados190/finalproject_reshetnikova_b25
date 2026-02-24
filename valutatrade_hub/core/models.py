# valutatrade_hub/core/models.py
import hashlib
import os
from datetime import datetime
from typing import Dict


class User:
    def __init__(self, user_id: int, username: str, password: str,
                 registration_date: str = None):
        self._user_id = user_id
        self.username = username
        self._salt = os.urandom(8).hex()
        self._hashed_password = self._hash_password(password)
        self._registration_date = registration_date or datetime.now().isoformat()

    def _hash_password(self, password: str) -> str:
        return hashlib.sha256((password + self._salt).encode()).hexdigest()

    def verify_password(self, password: str) -> bool:
        return self._hash_password(password) == self._hashed_password

    @property
    def user_id(self):
        return self._user_id

    @property
    def registration_date(self):
        return self._registration_date

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, value):
        if not value:
            raise ValueError("Имя пользователя не может быть пустым")
        self._username = value


class Wallet:
    def __init__(self, currency_code: str, balance: float = 0.0):
        self.currency_code = currency_code.upper()
        self._balance = balance

    def deposit(self, amount: float):
        if amount <= 0:
            raise ValueError("Сумма пополнения должна быть положительной")
        self._balance += amount

    def withdraw(self, amount: float):
        if amount <= 0:
            raise ValueError("Сумма снятия должна быть положительной")
        if amount > self._balance:
            raise ValueError(f"Недостаточно средств: доступно {self._balance} {self.currency_code}, требуется {amount} {self.currency_code}")
        self._balance -= amount

    @property
    def balance(self):
        return self._balance

    @balance.setter
    def balance(self, value):
        if value < 0:
            raise ValueError("Баланс не может быть отрицательным")
        self._balance = value

    def get_balance_info(self) -> float:
        return self._balance


class Portfolio:
    def __init__(self, user: User, wallets: Dict[str, Wallet] = None):
        self._user = user
        self._wallets = wallets or {}

    @property
    def user(self) -> User:
        return self._user

    @property
    def wallets(self) -> Dict[str, Wallet]:
        return self._wallets

    def add_currency(self, currency_code: str):
        currency_code = currency_code.upper()
        if currency_code in self._wallets:
            raise ValueError(f"Кошелек {currency_code} уже существует")
        self._wallets[currency_code] = Wallet(currency_code)

    def get_wallet(self, currency_code: str) -> Wallet:
        return self._wallets.get(currency_code.upper())

    def get_total_value(self, base_currency="USD", exchange_rates=None) -> float:
        if exchange_rates is None:
            exchange_rates = {"USD": 1.0, "EUR": 1.1, "BTC": 60000.0}
        total = 0.0
        for wallet in self._wallets.values():
            rate = exchange_rates.get(wallet.currency_code, 0)
            total += wallet.balance * rate
        return total