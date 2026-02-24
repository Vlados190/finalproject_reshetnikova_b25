from functools import wraps
from .logging_config import logger

def log_action(action):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            username = kwargs.get("username") or getattr(args[0], "username", None)
            currency = kwargs.get("currency_code") or kwargs.get("code") or ""
            amount = kwargs.get("amount", "")
            try:
                result = func(*args, **kwargs)
                logger.info(f"{action} user='{username}' currency='{currency}' amount={amount} result=OK")
                return result
            except Exception as e:
                logger.error(f"{action} user='{username}' currency='{currency}' amount={amount} result=ERROR error='{e}'")
                raise
        return wrapper
    return decorator