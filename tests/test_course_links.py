"""课程参考来源和术语复用链接的边界检查。"""
import unittest
from check_course import COURSE, allowed_course_link

class CourseLinksTest(unittest.TestCase):
    def test_official_sources(self):
        self.assertTrue(allowed_course_link(COURSE / "lesson.md", "https://docs.python.org/3/"))
        self.assertFalse(allowed_course_link(COURSE / "lesson.md", "https://fake-docs.python.org/3/"))

    def test_wiki_only_in_glossary(self):
        href = "https://github.com/lixudong1649/jdp-wiki/blob/main/content/terms/python-interpreter.md"
        self.assertTrue(allowed_course_link(COURSE / "附录" / "术语表.md", href))
        self.assertFalse(allowed_course_link(COURSE / "lesson.md", href))

    def test_wiki_scope(self):
        prefix = "https://github.com/lixudong1649/jdp-wiki/blob/main/content/terms/"
        for href in [prefix + "../README.md", prefix + "term.md?raw=1",
                     prefix.replace("jdp-wiki", "other") + "term.md",
                     prefix.replace("https:", "http:") + "term.md",
                     prefix.replace("github.com", "github.com.evil.test") + "term.md"]:
            with self.subTest(href=href):
                self.assertFalse(allowed_course_link(COURSE / "附录" / "术语表.md", href))

if __name__ == "__main__":
    unittest.main()
