from pathlib import Path
from quart import utils
from telegram_to_rss.models import Feed, FeedEntry
from tortoise.query_utils import Prefetch
from telegram_to_rss.config import base_url
from telegram_to_rss.poll_telegram import parse_feed_entry_id
import re
from telegram_to_rss.client import telethon_dialog_id_to_tg_id
import xml.etree.ElementTree as ET
import logging

CLEAN_TITLE = re.compile("<.*?>")


def clean_title(raw_html):
    cleantext = re.sub(CLEAN_TITLE, "", raw_html).replace("\n", " ").strip()
    return cleantext


def generate_feed(feed_render_dir: Path, feed: Feed):
    logging.info("generate_feed %s %s", feed.name, feed.id)

    feed_url = "https://t.me/c/{}".format(telethon_dialog_id_to_tg_id(feed.id))

    rss_root_el = ET.Element("rss", {"version": "2.0"})

    rss_feed_el = ET.SubElement(rss_root_el, "channel")

    ET.SubElement(rss_feed_el, "title").text = feed.name
    ET.SubElement(rss_feed_el, "pubDate").text = feed.last_update.isoformat()
    ET.SubElement(
        rss_feed_el,
        "link",
        {"href": feed_url},
    )
    ET.SubElement(rss_feed_el, "description").text = feed.name

    for feed_entry in feed.entries:
        [feed_id, entry_id] = parse_feed_entry_id(feed_entry.id)
        feed_entry_url = "https://t.me/c/{}/{}".format(
            telethon_dialog_id_to_tg_id(feed_id), entry_id
        )

        rss_item_el = ET.SubElement(rss_feed_el, "item")

        ET.SubElement(rss_item_el, "guid").text = feed_entry_url

        message_text = clean_title(feed_entry.message)
        title = message_text[:100]
        ET.SubElement(rss_item_el, "title").text = title

        images = ""
        media_download_failure = False
        for media_path in feed_entry.media:
            if media_path == "FAIL":
                media_download_failure = True
            else:
                media_url = "{}/static/{}".format(base_url, media_path)
                images += '<br /><img src="{}"/>'.format(media_url)
        content = feed_entry.message.replace("\n", "<br />") + images
        if feed_entry.has_unsupported_media:
            content += "<br /><strong>This message has unsupported attachment. Open Telegram to view it.</strong>"
        if media_download_failure:
            content += "<br /><strong>Downloading some of the media for this message failed. Open Telegram to view it.</strong>"
        ET.SubElement(rss_item_el, "description").text = content

        ET.SubElement(rss_item_el, "pubDate").text = feed_entry.date.isoformat()
        ET.SubElement(rss_item_el, "link", {"href": feed_entry_url}).text = (
            feed_entry_url
        )

    final_feed_file = feed_render_dir.joinpath("{}.xml".format(feed.id))

    rss_xml_tree = ET.ElementTree(rss_root_el)
    rss_xml_tree.write(
        file_or_filename=final_feed_file, encoding="UTF-8", short_empty_elements=True
    )

    logging.info("generate_feed -> done %s %s", feed.name, feed.id)


async def update_feeds_cache(feed_render_dir: str):
    feeds = await Feed.all().prefetch_related(
        Prefetch("entries", queryset=FeedEntry.all().order_by("-date"))
    )

    for feed in feeds:
        await utils.run_sync(generate_feed)(feed_render_dir, feed)
