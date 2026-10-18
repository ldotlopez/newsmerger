import unittest
from unittest.mock import Mock, patch

from newsmerger.models import SourceItem
from newsmerger.processors.telegram import MAX_CAPTION_LENGTH, Processor, build_caption


class TelegramProcessorTests(unittest.TestCase):
    def make_processor(self) -> Processor:
        processor = Processor(Mock(), bot_token="token", chat_id="chat")
        processor.db = Mock()
        processor.db.get_annotations.return_value = {
            "summarize": {"summary": "A summary"}
        }
        return processor

    def make_item(self, data: dict | None = None) -> SourceItem:
        return SourceItem(
            source=Mock(),
            uid="item-1",
            title="An <important> title",
            uri="https://example.test/article?a=1&b=2",
            data=data or {},
        )

    @staticmethod
    def response() -> Mock:
        response = Mock()
        response.json.return_value = {
            "ok": True,
            "result": {"message_id": 42},
        }
        return response

    @patch("newsmerger.processors.telegram.requests.post")
    def test_sends_photo_with_caption_and_original_link(self, post: Mock) -> None:
        post.return_value = self.response()
        processor = self.make_processor()

        result = processor.process_item(
            self.make_item({"image": "https://example.test/image.jpg"})
        )

        (request_url,) = post.call_args.args
        payload = post.call_args.kwargs["json"]
        self.assertTrue(request_url.endswith("/sendPhoto"))
        self.assertEqual(payload["photo"], "https://example.test/image.jpg")
        self.assertEqual(payload["parse_mode"], "HTML")
        self.assertIn("&lt;important&gt;", payload["caption"])
        self.assertIn(
            'href="https://example.test/article?a=1&amp;b=2"', payload["caption"]
        )
        self.assertEqual(result, {"message_id": 42})

    @patch("newsmerger.processors.telegram.requests.post")
    def test_falls_back_to_text_without_image(self, post: Mock) -> None:
        post.return_value = self.response()
        processor = self.make_processor()

        processor.process_item(self.make_item())

        (request_url,) = post.call_args.args
        payload = post.call_args.kwargs["json"]
        self.assertTrue(request_url.endswith("/sendMessage"))
        self.assertIn("text", payload)
        self.assertNotIn("photo", payload)

    @patch("newsmerger.processors.telegram.requests.post")
    def test_already_posted_item_is_not_posted_again(self, post: Mock) -> None:
        processor = self.make_processor()
        processor.db.get_annotations.return_value = {"telegram": {"message_id": 7}}

        result = processor.process_item(self.make_item())

        post.assert_not_called()
        self.assertEqual(result, {"message_id": 7})

    def test_caption_is_bounded_and_keeps_link(self) -> None:
        caption = build_caption(
            "Title",
            "A" * 2000,
            "https://example.test/article",
        )

        self.assertLessEqual(len(caption), MAX_CAPTION_LENGTH)
        self.assertIn("Original article", caption)
        self.assertIn("https://example.test/article", caption)


if __name__ == "__main__":
    unittest.main()
