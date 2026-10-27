"""The `googlechat` sink posts summarized items (title, summary, link and
image, see `WebhookOptions`) to a
Google Chat space through an incoming webhook, given either as its `url` or
as its `channel` (space id) and `token`, in the section (the default) or in
each `deliver:` entry. What was delivered is in the ledger
(`inspect deliveries`), so nothing is ever posted twice unless forced.
"""

import html
from typing import Any, Self
from urllib.parse import quote

import pydantic
import requests
from pydantic import SecretStr

from ..db import Database
from ..models import SourceItem
from ..sinks import BaseItemSink, DeliveryOptions, Sink
from . import PluginObjects, PluginOptions, Services

# The API key Google puts in every incoming webhook URL; only the token is secret.
WEBHOOK_KEY = "AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI"


class GoogleChatError(Exception):
    """A message could not be posted."""


def build_text(
    title: str, summary: str, uri: str, link_text: str = "original article"
) -> str:
    # Chat parses `<url|label>` links and `*bold*`, so the text must escape `<>&`.
    return (
        f"*{html.escape(title, quote=False)}*\n\n"
        f"{html.escape(summary, quote=False)}\n\n"
        f"<{uri}|{html.escape(link_text, quote=False)}>"
    )


def image_card(image_url: str, alt_text: str) -> dict[str, Any]:
    """A card holding only the image, shown below the message text."""
    return {
        "cardId": "image",
        "card": {
            "sections": [
                {"widgets": [{"image": {"imageUrl": image_url, "altText": alt_text}}]}
            ]
        },
    }


class Options(PluginOptions):
    """Defaults for every entry."""

    url: SecretStr | None = None
    channel: str | None = None
    token: SecretStr | None = None


class WebhookOptions(DeliveryOptions):
    url: SecretStr | None = None
    channel: str | None = None
    token: SecretStr | None = None
    item_image: bool = True  # the item's image, when it has one, as a card
    item_url_text: str = "original article"

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
    requires = "summary"
    options_model = WebhookOptions

    def send(
        self, db: Database, subject: SourceItem, options: WebhookOptions
    ) -> dict[str, str]:
        summaries = db.get_annotation_values([subject], key="summary")
        message: dict[str, Any] = {
            "text": build_text(
                subject.title,
                str(summaries[subject.key]),
                subject.uri,
                options.item_url_text,
            )
        }
        image = subject.data.get("image")
        if options.item_image and isinstance(image, str) and image.strip():
            message["cardsV2"] = [image_card(image, subject.title)]
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


def __newsmerger_plugin__(services: Services, **options: Any) -> PluginObjects:
    sink = GoogleChatSink(Options.model_validate(options))
    return [(sink.name, Sink, sink)]
