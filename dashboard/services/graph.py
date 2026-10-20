from datetime import timedelta

from plotly.graph_objs import Scatter
from plotly.offline import plot

from config.settings import TINKOFF_TOKEN, logger


def get_graph(share):
    if not TINKOFF_TOKEN:
        return (
            "<p class='text-muted'>График недоступен: не задан TINKOFF_TOKEN "
            "в настройках приложения.</p>"
        )

    try:
        from tinkoff.invest import CandleInterval, Client
        from tinkoff.invest.utils import now

        with Client(TINKOFF_TOKEN) as client:
            x_data, y_data = [], []
            for candle in client.get_all_candles(
                figi=share.figi,
                from_=now() - timedelta(days=180),
                interval=CandleInterval.CANDLE_INTERVAL_DAY,
            ):
                x_data.append(candle.time.date())
                price = candle.close.units + candle.close.nano / 1e9
                y_data.append(price)
        plot_div = plot(
            [
                Scatter(
                    x=x_data,
                    y=y_data,
                    mode="lines",
                    name=share.ticker,
                    opacity=0.8,
                    marker_color="red",
                )
            ],
            output_type="div",
            show_link=False,
            link_text="",
        )
        return plot_div
    except Exception as exc:
        logger.error("Failed to build graph for share %s: %s", share.id, exc)
        return f"<p class='text-danger'>Не удалось загрузить график: {exc}</p>"
