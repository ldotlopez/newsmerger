"""The `googlechat` sink posts summarized items (title, the `summary` option's
annotation, link and image, see `WebhookOptions`) as a card to a
Google Chat space through an incoming webhook, given either as its `url` or
as its `channel` (space id) and `token`, in the `plugins` section (the
default) or in each use. What was delivered is in the ledger
(`inspect deliveries`), so nothing is ever posted twice unless forced.
"""

import html
import re
from typing import Any, Self
from urllib.parse import quote, urlsplit, urlunsplit

import pydantic
import requests
from pydantic import SecretStr

from ..db import Database
from ..models import SourceItem
from ..sinks import BaseItemSink, DeliveryOptions, SinkType
from . import PluginTypes

# The API key Google puts in every incoming webhook URL; only the token is secret.
WEBHOOK_KEY = "AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI"

# Chat shows no image from Blogger's host, so those go through this proxy.
BLOGGER_HOST = "blogger.googleusercontent.com"
IMAGE_PROXY = "https://wsrv.nl/?url="
# The size segment of a Blogger image path (`s72-c`, `w1200`, ...); feeds
# give 72px thumbnails, so cards ask for the full size instead.
BLOGGER_SIZE = re.compile(r"[swh]\d+(-[\w-]+)?")
BLOGGER_FULL_SIZE = "s1600"


class GoogleChatError(Exception):
    """A message could not be posted."""


def chat_image_url(image_url: str) -> str:
    """Where Chat can fetch the image: Blogger's at full size, through the
    proxy; any other as is."""
    parts = urlsplit(image_url)
    if parts.hostname != BLOGGER_HOST:
        return image_url
    segments = [
        BLOGGER_FULL_SIZE if BLOGGER_SIZE.fullmatch(segment) else segment
        for segment in parts.path.split("/")
    ]
    full_size = urlunsplit(parts._replace(path="/".join(segments)))
    return IMAGE_PROXY + quote(full_size, safe="")


def build_card(
    title: str,
    summary: str,
    uri: str,
    link_text: str = "original article",
    image_url: str | None = None,
) -> dict[str, Any]:
    """The message: title and summary, the image if any, and a link button."""
    # The paragraph is Chat's HTML subset, so the text must escape `<>&`.
    text = html.escape(summary, quote=False).replace("\n", "<br>")
    widgets: list[dict[str, Any]] = [
        {
            "textParagraph": {
                "text": f"<b>{html.escape(title, quote=False)}</b><br><br>{text}"
            }
        }
    ]
    if image_url is not None:
        widgets.append(
            {"image": {"imageUrl": chat_image_url(image_url), "altText": title}}
        )
    widgets.append(
        {
            "buttonList": {
                "buttons": [{"text": link_text, "onClick": {"openLink": {"url": uri}}}]
            }
        }
    )
    return {
        "cardsV2": [{"cardId": "item", "card": {"sections": [{"widgets": widgets}]}}]
    }


class WebhookOptions(DeliveryOptions):
    url: SecretStr | None = None
    channel: str | None = None
    token: SecretStr | None = None
    item_image: bool = True  # the item's image, when it has one, in the card
    item_url_text: str = "original article"
    summary: str = "summary"  # the annotation key posted as the summary

    @pydantic.model_validator(mode="after")
    def url_or_channel_and_token(self) -> Self:
        parts = (self.channel, self.token)
        if (self.url is None and None not in parts) or (
            self.url is not None and parts == (None, None)
        ):
            return self
        raise ValueError("set either `url` or both `channel` and `token`")

    def webhook_url(self) -> SecretStr:
        if self.url is not None:
            return self.url
        assert self.channel is not None and self.token is not None
        return SecretStr(
            f"https://chat.googleapis.com/v1/spaces/{quote(self.channel)}/messages"
            f"?key={WEBHOOK_KEY}&token={quote(self.token.get_secret_value())}"
        )


class GoogleChatSink(BaseItemSink[WebhookOptions]):
    name = "googlechat"
    options_model = WebhookOptions

    @classmethod
    def required_key(cls, options: WebhookOptions) -> str:
        return options.summary

    def send(self, db: Database, subject: SourceItem) -> dict[str, str]:
        options = self.options
        summaries = db.get_annotation_values([subject], key=options.summary)
        image = subject.data.get("image")
        if not (options.item_image and isinstance(image, str) and image.strip()):
            image = None
        message = build_card(
            subject.title,
            str(summaries[subject.key]),
            subject.uri,
            options.item_url_text,
            image,
        )
        try:
            response = requests.post(
                options.webhook_url().get_secret_value(),
                json=message,
                timeout=30,
            )
            result = response.json()
        except requests.RequestException as e:
            # Only the class: the message holds the URL, which embeds the token.
            raise GoogleChatError(type(e).__name__) from None
        if not response.ok:
            raise GoogleChatError(result.get("error", {}).get("message", str(result)))
        return {"message": result["name"]}


def __newsmerger_plugin__() -> PluginTypes:
    return [(GoogleChatSink.name, SinkType, GoogleChatSink)]
