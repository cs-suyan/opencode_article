from src.article_generator import ArticleGenerator


def test_word_count_guideline():
    gen = ArticleGenerator(api_key="test")
    assert gen._word_count_guideline(0).startswith("1000")
    assert gen._word_count_guideline(1).startswith("800")
    assert gen._word_count_guideline(5).startswith("600")
    assert gen._word_count_guideline(10).startswith("500")
