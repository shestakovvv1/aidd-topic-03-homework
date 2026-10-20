from config.settings import TINKOFF_TOKEN, logger

try:
    from tinkoff.invest import Client
    TINKOFF_AVAILABLE = True
except ImportError:
    TINKOFF_AVAILABLE = False
    logger.warning("Tinkoff API not available. Market data fetching disabled.")


def get_last_data(share):
    if not TINKOFF_AVAILABLE or not TINKOFF_TOKEN:
        logger.warning(f"Tinkoff API not available for share {share.id}")
        return [share.last_price or 0, None]
    
    try:
        with Client(TINKOFF_TOKEN) as client:
            resp = client.market_data.get_last_prices(figi=[share.figi])
            resp = resp.last_prices.pop()
            logger.info(f"Get last data for share with id {share.id}")
            return [resp.price.units, resp.time]
    except Exception as e:
        logger.error(f"Error fetching last data for share {share.id}: {e}")
        return [share.last_price or 0, None]
