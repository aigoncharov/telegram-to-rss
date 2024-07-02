from telegram_to_rss.server import app
from telegram_to_rss.config import host, port


def main():
    app.run(debug=True, port=port, host=host)


if __name__ == "__main__":
    main()
