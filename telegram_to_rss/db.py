from tortoise import Tortoise


async def init_feeds_db(db_path: str):
    await Tortoise.init(
        db_url="sqlite://{}".format(db_path),
        modules={"models": ["telegram_to_rss.models"]},
    )
    # Generate the schema
    await Tortoise.generate_schemas(safe=True)


async def close_feeds_db():
    await Tortoise.close_connections()
