# telegram-to-rss

Generate an RSS feed from your Telegram chats. You digital minimalism friend.

## How to get the most of it

> Digital minimalism is a strategy to help people optimize their use of technology and keep from being overwhelmed by it.

1. Create a separate Telegram account to subscribe to various channels available only as Telegram feeds (yep, they exist!)
2. Convert all of them to RSS feeds using this app
3. Be in power of your information consumption with a single place to get it - your RSS reader!

## Quick start

### Docker 

Coming soon

### Bare bone Python

1. `pip install telegram-to-rss`
2. Get `api_id` an `api_hash` at https://my.telegram.org
3. Run in your terminal `TG_API_ID=api_id TG_API_HASH=api_hash BASE_URL=server_url python telegram_to_rss` 
   1. Example: `TG_API_ID=00000000 TG_API_HASH=7w8sdsd3g334r333refdwd3qqrwe BASE_URL=example.myserver.com python telegram_to_rss`
4. If you have 2FA enabled on your Telegram account set `TG_PASSWORD` with your account password as well: `TG_API_ID=api_id TG_API_HASH=api_hash TG_PASSWORD=your_password BASE_URL=server_url python telegram_to_rss`
5. Go to `http://127.0.0.1:5000`
6. Scan the QR code with your Telegram app
7. Give it a few seconds to log in
8. Get redirected to a page with a list of all your chats available as RSS feeds.
   1. If the list is incomplete, give it a few minutes on the first start to generate the RSS feeds.
   2. Subsequent updated should be much faster!

## Configuration

Available environment variables (\* marks required ones):
- \* `TG_API_ID` - api_id from https://my.telegram.org  
- \* `TG_API_HASH` - api_hash from https://my.telegram.org
- \* `BASE_URL` - address of your server that hosts this app, used in RSS feeds to correctly set image addresses
- `TG_PASSWORD` - your telegram password, required if 2fa is enabled on the account
- `BIND` - `host:port` to bind to on the server. Default: `127.0.0.1:5000`
- `LOGLEVEL` - log level for the app ([supported values](https://docs.python.org/3/library/logging.html#logging-levels)). Default: `INFO`
- `DATA_DIR` - path to store the database, RSS feeds and other static files. Default: `user_data_dir` from [platformdirs](https://github.com/platformdirs/platformdirs?tab=readme-ov-file#platformdirs-to-the-rescue)
- `FEED_SIZE` - size of the RSS feed. When your RSS feed grows larger than the limit, older entries are going to be discarded. Default: 100.
- `POLL_BATCH_SIZE` - how many messages we fetch from Telegram every `UPDATE_INTERVAL` seconds. Also a number of items we fetch for any new feed. Might behave weirdly with the values over 100. Could be improved by iterating through Telegram API calls in multiple batches, but I never got to it. You know, 20% effort - 80% result :palm_tree: :sunny: :tropical_drink: Default value: 20.
- `UPDATE_INTERVAL` - how often the app should fetch new messages from Telegram and regenerate RSS feeds (in seconds). Default: 3600.