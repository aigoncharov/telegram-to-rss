from telegram_to_rss.connection import connect
from telegram_to_rss.client import init_client


def main():
    client = init_client()
    connect(client)


if __name__ == "__main__":
    main()
