import os
from pathlib import Path
from platformdirs import user_data_dir

api_id = int(os.environ.get("TG_API_ID"))
api_hash = os.environ.get("TG_API_HASH")
password = os.environ.get("TG_PASSWORD")

update_interval_seconds = int(os.environ.get("UPDATE_INTERVAL") or 3600)
message_limit = int(os.environ.get("MESSAGE_LIMIT") or 100)

data_dir = Path(os.environ.get("DATA_DIR")) or Path(user_data_dir).joinpath(
    "telegram_to_rss"
)
data_dir.mkdir(mode=0o600, parents=True, exist_ok=True)

session_path = data_dir.joinpath("telegram_to-rss.session")
static_path = data_dir.joinpath("/static").mkdir(mode=0o600, exist_ok=True)
db_path = data_dir.joinpath("feeds.db")
