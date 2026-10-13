import unittest

import chatbot
import vector_store


class TestGroqModelSelection(unittest.TestCase):
    def test_default_model_is_available_on_groq(self):
        llm = chatbot.create_beauty_chatbot("fake-key")
        self.assertEqual(llm.model_name, "openai/gpt-oss-20b")


class TestSearchBehavior(unittest.TestCase):
    def test_unrelated_weather_query_returns_no_results(self):
        results = vector_store.search_products("what is the weather today", product_type="skincare", k=6)
        self.assertEqual(results, [])

    def test_serum_price_query_keeps_serum_relevance_first(self):
        results = vector_store.search_products("serums between $20 and $40", product_type="skincare", k=6)
        self.assertTrue(results)
        self.assertIn("serum", results[0].page_content.lower())

    def test_brand_alias_ignores_substrings_in_other_words(self):
        self.assertIsNone(vector_store.normalize_brand("myself"))
        self.assertIsNone(vector_store.normalize_brand("shelf"))
        self.assertIsNone(vector_store.normalize_brand("show"))
        self.assertEqual(vector_store.normalize_brand("elf makeup"), "e.l.f.")

    def test_chat_context_keeps_previous_serum_hint(self):
        history = [{"role": "user", "content": "oily skin serum"}]
        query = chatbot.build_search_context(history, "anything cheaper under $10?")
        self.assertIn("serum", query.lower())
        self.assertIn("cheaper", query.lower())

    def test_detect_focus_prefers_one_category_when_both_are_present(self):
        self.assertEqual(chatbot.detect_focus([], "oily skin and curly hair"), "skincare")


if __name__ == "__main__":
    unittest.main()
