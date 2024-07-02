from telegram_to_rss.server import app
from telegram_to_rss.config import bind
import asyncio
from hypercorn.config import Config
from hypercorn.asyncio import serve
import argparse


# https://stackoverflow.com/a/46877092
def parse_hostport(bind_str: str | None) -> tuple[str | None, int | None]:
    if bind_str is None:
        return (None, None)

    out = bind_str.rsplit(":", 1)
    try:
        out[1] = int(out[1])
    except (IndexError, ValueError):
        # couldn't parse the last component as a port, so let's
        # assume there isn't a port.
        out = (bind_str, None)
    return out


def main():
    parser = argparse.ArgumentParser(
        prog="Telegram to RSS",
        description="Generate an RSS feed from your Telegram chats",
    )
    parser.add_argument("-d", "--dev", action="store_true")
    args = parser.parse_args()

    if args.dev:
        [host, port] = parse_hostport(bind)
        app.run(debug=True, host=host, port=port)
    else:
        config = Config()
        if bind:
            config.bind = bind
        asyncio.run(serve(app, config))
