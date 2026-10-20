from config.settings import TINKOFF_TOKEN, logger


def get_last_data(share):
    if not TINKOFF_TOKEN:
        raise RuntimeError("TINKOFF_TOKEN is not configured")

    try:
        from tinkoff.invest import Client
    except ImportError as exc:
        raise RuntimeError(
            "Package tinkoff-investments is not installed"
        ) from exc

    with Client(TINKOFF_TOKEN) as client:
        resp = client.market_data.get_last_prices(figi=[share.figi])
        resp = resp.last_prices.pop()
        logger.info(f"Get last data for share with id {share.id}")
        price = resp.price.units + resp.price.nano / 1e9
        return [price, resp.time]
