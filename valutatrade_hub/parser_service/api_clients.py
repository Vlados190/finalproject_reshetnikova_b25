import requests
from abc import ABC, abstractmethod
from datetime import datetime, timezone

from .config import config
from ..core.exceptions import ApiRequestError


class BaseApiClient(ABC):
    @abstractmethod
    def fetch_rates(self) -> dict:
        """
        Должен вернуть словарь в формате:
        {
            "BTC_USD": {
                "rate": 59337.21,
                "updated_at": "...",
                "source": "CoinGecko"
            }
        }
        """
        pass


class CoinGeckoClient(BaseApiClient):
    def fetch_rates(self) -> dict:
        try:
            ids = ",".join(
                config.CRYPTO_ID_MAP[code]
                for code in config.CRYPTO_CURRENCIES
                if code in config.CRYPTO_ID_MAP
            )

            params = {
                "ids": ids,
                "vs_currencies": config.BASE_CURRENCY.lower(),
            }

            response = requests.get(
                config.COINGECKO_URL,
                params=params,
                timeout=config.REQUEST_TIMEOUT,
            )

            if response.status_code != 200:
                raise ApiRequestError(
                    f"CoinGecko error: {response.status_code}"
                )

            data = response.json()
            result = {}

            timestamp = datetime.now(timezone.utc).isoformat()

            for code, coin_id in config.CRYPTO_ID_MAP.items():
                if coin_id in data:
                    rate = data[coin_id].get(config.BASE_CURRENCY.lower())
                    if rate:
                        pair = f"{code}_{config.BASE_CURRENCY}"
                        result[pair] = {
                            "rate": float(rate),
                            "updated_at": timestamp,
                            "source": "CoinGecko",
                        }

            return result

        except requests.exceptions.RequestException as e:
            raise ApiRequestError(f"CoinGecko network error: {e}")


class ExchangeRateApiClient(BaseApiClient):
    """
    Используем exchangerate.host — бесплатный API без ключа
    """

    def fetch_rates(self) -> dict:
        try:
            url = "https://api.exchangerate.host/latest"

            params = {
                "base": config.BASE_CURRENCY,
                "symbols": ",".join(config.FIAT_CURRENCIES),
            }

            response = requests.get(
                url,
                params=params,
                timeout=config.REQUEST_TIMEOUT,
            )

            if response.status_code != 200:
                raise ApiRequestError(
                    f"ExchangeRate error: {response.status_code}"
                )

            data = response.json()

            if "rates" not in data:
                raise ApiRequestError("Invalid response from ExchangeRate")

            result = {}
            timestamp = datetime.now(timezone.utc).isoformat()

            for code in config.FIAT_CURRENCIES:
                rate = data["rates"].get(code)
                if rate:
                    pair = f"{code}_{config.BASE_CURRENCY}"
                    result[pair] = {
                        "rate": float(rate),
                        "updated_at": timestamp,
                        "source": "ExchangeRate",
                    }

            return result

        except requests.exceptions.RequestException as e:
            raise ApiRequestError(f"ExchangeRate network error: {e}")