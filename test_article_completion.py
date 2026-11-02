"""完成直前で失敗した記事を、再課金や再生成なしで復旧できることを確認。"""
import ast
import re
import unittest
from html import escape
from pathlib import Path


class FakeProgress:
    def progress(self, *_args, **_kwargs):
        pass


class FakeStreamlit:
    def __init__(self):
        self.session_state = {}

    def progress(self, *_args, **_kwargs):
        return FakeProgress()


class ArticleCompletionTests(unittest.TestCase):
    def setUp(self):
        tree = ast.parse(Path(__file__).with_name("app.py").read_text())
        imports = [node for node in tree.body if isinstance(node, ast.ImportFrom) and node.module == "html"]
        self.assertTrue(any(alias.name == "escape" for node in imports for alias in node.names))
        names = {"markdown_to_wordpress_html", "generate_article_parts", "restore_finished_article"}
        functions = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in names]
        self.assertEqual(len(functions), len(names))
        self.st = FakeStreamlit()
        self.scope = {"st": self.st, "re": re, "escape": escape, "display_error": lambda exc: self.fail(str(exc))}
        exec(compile(ast.Module(body=functions, type_ignores=[]), "app.py", "exec"), self.scope)

    def test_saved_article_finishes_without_llm(self):
        work = {
            "keyword": "せんげん台 足の悩み", "intent": "読者の悩み", "outline": "## 見出し",
            "target_outlines": ["## 見出し"], "article_parts": ["## 見出し\n安全な本文 <script>"],
            "source": "competitor_research",
        }
        self.scope["write_article_heading"] = lambda *_args: self.fail("LLMを再実行しました")
        self.scope["restore_finished_article"](work, "seo_result", "unused")
        result = self.st.session_state["seo_result"]
        self.assertEqual(result["article"], work["article_parts"][0])
        self.assertIn("&lt;script&gt;", result["html_article"])
        self.assertEqual(result["source"], "competitor_research")

    def test_incomplete_article_is_left_for_resume(self):
        work = {"target_outlines": ["a", "b"], "article_parts": ["a"]}
        self.scope["restore_finished_article"](work, "seo_result", "unused")
        self.assertNotIn("seo_result", self.st.session_state)


if __name__ == "__main__":
    unittest.main()
