import logging
from .api_clients import CoinGeckoClient, ExchangeRateApiClient
from .storage import RatesStorage
from ..core.logging_config import get_logger

logger = get_logger("parser")

class RatesUpdater:
    def __init__(self, clients=None):
        self.clients = clients or [CoinGeckoClient(), ExchangeRateApiClient()]
        self.storage = RatesStorage()

    def run_update(self):
        all_rates = {}
        for client in self.clients:
            name = client.__class__.__name__
            try:
                logger.info(f"Fetching from {name}...")
                rates = client.fetch_rates()
                logger.info(f"{name}: OK ({len(rates)} rates)")
                all_rates.update(rates)
            except Exception as e:
                logger.error(f"Failed to fetch from {name}: {e}")

        # запись истории и snapshot
        for pair, info in all_rates.items():
            pair_id = f"{pair}_{info['updated_at']}"
            self.storage.save_history(pair_id, {
                "id": pair_id,
                "from_currency": pair.split("_")[0],
                "to_currency": pair.split("_")[1],
                **info
            })
        self.storage.update_rates_snapshot(all_rates)
        logger.info(f"Update finished. Total rates: {len(all_rates)}")