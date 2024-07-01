from telegram_to_rss.server import app


def main():
    app.run(debug=True, port=5001)


if __name__ == "__main__":
    main()
