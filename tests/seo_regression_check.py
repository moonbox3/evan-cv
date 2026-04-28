#!/usr/bin/env python3
"""Static SEO regression checks for the Jekyll site."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def strip_markup(text: str) -> str:
    text = re.sub(r"(?s)^---.*?---", " ", text)
    text = re.sub(r"(?s)<style.*?</style>", " ", text)
    text = re.sub(r"(?s)<script.*?</script>", " ", text)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    text = re.sub(r"{%.*?%}|{{.*?}}", " ", text)
    return re.sub(r"\s+", " ", text)


def word_count(text: str) -> int:
    return len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'-]*", strip_markup(text)))


def assert_true(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def main() -> int:
    failures: list[str] = []

    default = read("_layouts/default.html")
    post = read("_layouts/post.html")
    blog_index = read("blog/index.html")
    welcome = read("_posts/2026-02-24-welcome.md")

    for path in ("robots.txt", "sitemap.xml", "llms.txt"):
        assert_true((ROOT / path).exists(), f"{path} must exist", failures)

    assert_true('rel="canonical"' in default, "default layout must emit canonical URL", failures)
    assert_true('property="og:url"' in default, "default layout must emit og:url", failures)
    assert_true('name="twitter:card"' in default, "default layout must emit twitter:card", failures)
    assert_true('"@type": "Person"' in default, "default layout must include Person JSON-LD", failures)
    assert_true('"@type": "WebSite"' in default, "default layout must include WebSite JSON-LD", failures)

    assert_true('"@type": "BlogPosting"' in post, "post layout must include BlogPosting JSON-LD", failures)
    assert_true("author-bio" in post, "post layout must render visible author attribution", failures)

    assert_true(word_count(blog_index) >= 120, "blog index must have at least 120 words of indexable copy", failures)
    assert_true(word_count(welcome) >= 600, "welcome post must have at least 600 words", failures)
    assert_true("/#projects" in welcome, "welcome post must link to the Projects section", failures)
    assert_true("/#contact" in welcome, "welcome post must link to the Contact section", failures)

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    print("SEO regression checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
