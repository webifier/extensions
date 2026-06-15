from __future__ import annotations

import os
import re
from difflib import SequenceMatcher
from typing import Any, ClassVar

from bs4 import BeautifulSoup, NavigableString, Tag
from webifier.core.base import NodeContext, RendererModule


class ContentPageRenderer(RendererModule):
    """Render a content page (markdown/notebook output wrapped in a page layout)."""

    template: ClassVar[str] = "content.html"
    META_KEYS: ClassVar[frozenset[str]] = frozenset(
        {
            "kind",
            "template",
            "content",
            "metadata",
            "title",
            "nav",
            "footer",
            "config",
            "colab",
            "page_url",
            "source_path",
        }
    )
    METADATA_KEYS: ClassVar[frozenset[str]] = frozenset(
        {
            "title",
            "header",
            "meta",
            "nav",
            "footer",
            "style",
            "config",
            "favicon",
        }
    )

    def process(self, data: dict[str, Any], ctx: NodeContext, builder) -> dict[str, Any]:
        processed = dict(data)
        content_config = builder.page_config(processed).get("content_pages", {})
        if isinstance(content_config, dict) and (content_config.get("cleanup") or content_config.get("toc")):
            processed["content"] = self.normalize_content(
                processed.get("content", ""),
                processed,
                cleanup=bool(content_config.get("cleanup")),
                toc=bool(content_config.get("toc")),
                asset_base=builder.base_url.rstrip("/"),
            )
        before_content = []
        after_content = []
        metadata = processed.get("metadata", {})
        comments_section = None
        if isinstance(metadata, dict):
            metadata_ctx = ctx
            source_path = processed.get("source_path")
            if isinstance(source_path, str) and source_path:
                metadata_ctx = ctx.child("metadata", assets_src_dir=os.path.dirname(source_path))
            author_items = []
            author_section = None
            for key in ("authors", "reviewers"):
                value = metadata.get(key)
                if not isinstance(value, dict):
                    continue
                if author_section is None:
                    author_section = dict(value)
                content = value.get("people", value.get("content", []))
                if isinstance(content, list):
                    author_items.extend(content)
            if author_items:
                author_section = author_section or {}
                author_section["kind"] = "people"
                author_section["content"] = author_items
                author_section["label"] = {"position": "top", "text": "Authors"}
                after_content.append(
                    {
                        "key": "authors",
                        "html": builder.process_node(author_section, metadata_ctx.child("authors")),
                        "data": author_section,
                    }
                )
            for key, value in metadata.items():
                if key in self.METADATA_KEYS or key in {"authors", "reviewers"}:
                    continue
                section = {
                    "key": key,
                    "html": builder.process_node(value, metadata_ctx.child(key)),
                    "data": value,
                }
                if key == "comments":
                    comments_section = section
                    after_content.append(section)
                else:
                    before_content.append(section)
        if isinstance(content_config, dict) and comments_section is None:
            comments_config = content_config.get("comments")
            if comments_config:
                comments_data = dict(comments_config) if isinstance(comments_config, dict) else {}
                comments_data.setdefault("kind", "comments")
                comments_data.setdefault("label", False)
                after_content.append(
                    {
                        "key": "comments",
                        "html": builder.process_node(comments_data, ctx.child("comments")),
                        "data": comments_data,
                    }
                )
        processed["_before_content_sections"] = before_content
        processed["_after_content_sections"] = after_content
        return processed

    def normalize_content(self, html: str, data: dict[str, Any], cleanup: bool, toc: bool, asset_base: str = "") -> str:
        soup = BeautifulSoup(html, "html.parser")
        root = soup.find("body") or soup
        content_root = root.find("main") or root
        metadata = data.get("metadata", {})
        titles = {data.get("title", "")}
        if isinstance(metadata, dict):
            titles.add(metadata.get("title", ""))
            header = metadata.get("header", {})
            if isinstance(header, dict):
                titles.add(header.get("title", ""))
        normalized_titles = {
            re.sub(r"[^a-z0-9]+", "", str(title).lower())
            for title in titles
            if title
        }

        if cleanup:
            for anchor in content_root.select("a.anchor-link"):
                anchor.decompose()

            for font in list(content_root.find_all("font")):
                try:
                    font_size = float(str(font.get("size", "")).strip())
                except ValueError:
                    font_size = 0
                if font_size >= 5.5:
                    text = font.get_text(" ", strip=True)
                    if text:
                        heading = soup.new_tag("h2")
                        heading.string = text
                        font.replace_with(heading)
                        continue
                font.unwrap()

            for tag in content_root.find_all(["h1", "h2", "h3", "h4"]):
                text = tag.get_text(" ", strip=True)
                if text.startswith("#"):
                    tag.clear()
                    tag.append(re.sub(r"^#+\s*", "", text))

            for tag in content_root.find_all(style=True):
                declarations = []
                for declaration in str(tag.get("style", "")).split(";"):
                    if ":" not in declaration:
                        continue
                    name, value = declaration.split(":", 1)
                    if name.strip().lower() in {"direction", "line-height", "font-family"}:
                        continue
                    declarations.append(f"{name.strip()}: {value.strip()}")
                if declarations:
                    tag["style"] = "; ".join(declarations)
                else:
                    del tag["style"]

            while True:
                first = next(
                    (
                        item
                        for item in content_root.contents
                        if isinstance(item, Tag) or (isinstance(item, NavigableString) and item.strip())
                    ),
                    None,
                )
                if not isinstance(first, Tag):
                    break
                text = first.get_text(" ", strip=True)
                normalized_text = re.sub(r"[^a-z0-9]+", "", text.lower())
                leading_heading = first.find(["h1", "h2", "h3"])
                normalized_leading_heading = ""
                if leading_heading:
                    normalized_leading_heading = re.sub(
                        r"[^a-z0-9]+", "", leading_heading.get_text(" ", strip=True).lower()
                    )
                heading_matches_title = any(
                    len(normalized_leading_heading) > 8
                    and len(title) > 8
                    and (
                        normalized_leading_heading == title
                        or SequenceMatcher(None, normalized_leading_heading, title).ratio() >= 0.78
                    )
                    for title in normalized_titles
                )
                old_notebook_metadata = any(
                    marker in text.lower()
                    for marker in ("compiled by", "author:", "date created:", "last modified:", "description:")
                )
                is_duplicate_title = normalized_text in normalized_titles or (
                    heading_matches_title
                    and not first.find(["pre", "code", "table"])
                    and (old_notebook_metadata or len(text.split()) <= 12)
                )
                is_title_slide = (
                    first.name == "div"
                    and (
                        (
                            first.find(["h1", "h2"])
                            and (first.get("align") == "center" or "text-align" in str(first.get("style", "")))
                        )
                        or (
                            first.find(
                                lambda tag: isinstance(tag, Tag)
                                and tag.name == "div"
                                and (tag.get("align") == "center" or "text-align" in str(tag.get("style", "")))
                            )
                            and any(
                                phrase in text.lower()
                                for phrase in (
                                    "sharif university",
                                    "computer engineering",
                                    "artificial intelligence",
                                    "spring 2021",
                                )
                            )
                        )
                        or text.lower().startswith("ai -")
                    )
                )
                if is_duplicate_title or is_title_slide or first.name == "hr":
                    first.decompose()
                    continue
                break

            for first in list(content_root.find_all(["div", "section"], recursive=False))[:3]:
                text = first.get_text(" ", strip=True)
                normalized_text = re.sub(r"[^a-z0-9]+", "", text.lower())
                centered_heading = first.find(
                    lambda tag: isinstance(tag, Tag)
                    and tag.name == "div"
                    and (
                        (
                            tag.find(["h1", "h2"])
                            and (tag.get("align") == "center" or "text-align" in str(tag.get("style", "")))
                        )
                        or (
                            (tag.get("align") == "center" or "text-align" in str(tag.get("style", "")))
                            and any(
                                phrase in tag.get_text(" ", strip=True).lower()
                                for phrase in (
                                    "sharif university",
                                    "computer engineering",
                                    "artificial intelligence",
                                    "spring 2021",
                                )
                            )
                        )
                        or tag.get_text(" ", strip=True).lower().startswith("ai -")
                    )
                )
                if centered_heading and not first.find(["pre", "code", "img", "table"]):
                    first.decompose()
                    continue
                if normalized_text in normalized_titles and not first.find(["pre", "code", "img", "table"]):
                    first.decompose()

                centered_title = first.find(
                    lambda tag: isinstance(tag, Tag)
                    and tag.name == "div"
                    and (tag.get("align") == "center" or "text-align" in str(tag.get("style", "")))
                    and any(
                        title and title in re.sub(r"[^a-z0-9]+", "", tag.get_text(" ", strip=True).lower())
                        for title in normalized_titles
                    )
                )
                if centered_title:
                    centered_title.decompose()

            first_heading = content_root.find(["h1", "h2"])
            if first_heading:
                previous_content = [
                    item
                    for item in first_heading.previous_elements
                    if isinstance(item, Tag)
                    and item in content_root.descendants
                    and item.name in {"p", "ul", "ol", "pre", "code", "img", "table"}
                ]
                normalized_heading = re.sub(r"[^a-z0-9]+", "", first_heading.get_text(" ", strip=True).lower())
                heading_matches_title = any(
                    len(normalized_heading) > 8
                    and len(title) > 8
                    and (
                        normalized_heading == title
                        or SequenceMatcher(None, normalized_heading, title).ratio() >= 0.78
                    )
                    for title in normalized_titles
                )
                if not previous_content and heading_matches_title:
                    first_heading.decompose()

            for heading in list(content_root.find_all(["h1", "h2"])):
                normalized_heading = re.sub(r"[^a-z0-9]+", "", heading.get_text(" ", strip=True).lower())
                heading_matches_title = any(
                    len(normalized_heading) > 8
                    and len(title) > 8
                    and (
                        normalized_heading == title
                        or SequenceMatcher(None, normalized_heading, title).ratio() >= 0.78
                    )
                    for title in normalized_titles
                )
                if heading_matches_title:
                    heading.decompose()

            for heading in list(content_root.find_all(["h1", "h2", "h3"])):
                text = heading.get_text(" ", strip=True)
                if self.is_math_heading(text):
                    paragraph = soup.new_tag("p")
                    paragraph["class"] = "wf-math-display"
                    paragraph.extend(heading.contents)
                    heading.replace_with(paragraph)

            for heading in list(content_root.find_all("h1")):
                heading.name = "h2"

            for heading in list(content_root.find_all(["h1", "h2", "h3", "h4"])):
                text = re.sub(r"[^a-z ]+", "", heading.get_text(" ", strip=True).lower()).strip()
                if text not in {"table of contents", "table of content", "contents"}:
                    continue
                sibling = heading.next_sibling
                heading.decompose()
                while sibling:
                    current = sibling
                    sibling = sibling.next_sibling
                    if isinstance(current, Tag) and current.name in {"h1", "h2", "h3", "h4"}:
                        break
                    current.extract()

            for tag in list(content_root.find_all(["h1", "h2", "h3", "h4", "p", "div"])):
                if not tag.get_text(" ", strip=True) and not tag.find(["img", "svg", "canvas", "video", "iframe"]):
                    tag.decompose()

            if not any(
                heading.get_text(" ", strip=True).lower() == "introduction"
                for heading in content_root.find_all(["h1", "h2", "h3"])
            ):
                first_heading = content_root.find(["h1", "h2", "h3"])
                if first_heading:
                    opening_tag = None
                    for tag in content_root.find_all(["p", "div", "section", "article"]):
                        if tag is first_heading or first_heading in tag.descendants:
                            continue
                        if tag.find(["h1", "h2", "h3", "h4", "pre", "code", "table"]):
                            continue
                        text = tag.get_text(" ", strip=True)
                        if len(text.split()) >= 18:
                            opening_tag = tag
                            break
                    if opening_tag and any(item is opening_tag for item in first_heading.previous_elements):
                        insertion_target = opening_tag
                        while insertion_target.parent and insertion_target.parent is not content_root:
                            insertion_target = insertion_target.parent
                        heading = soup.new_tag("h2")
                        heading.string = "Introduction"
                        insertion_target.insert_before(heading)

        headings = []
        used_ids = set()
        if toc:
            for heading in content_root.find_all(["h1", "h2", "h3", "h4"]):
                text = heading.get_text(" ", strip=True)
                if not text:
                    continue
                slug = heading.get("id") or re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "section"
                base_slug = slug
                counter = 2
                while slug in used_ids:
                    slug = f"{base_slug}-{counter}"
                    counter += 1
                used_ids.add(slug)
                heading["id"] = slug
                headings.append({"level": int(heading.name[1]), "title": text, "href": f"#{slug}"})

        toc_nav = None
        if toc and len(headings) >= 3:
            nav = soup.new_tag("nav")
            nav["class"] = "wf-content-toc is-collapsed"
            nav["aria-label"] = "Table of contents"
            title = soup.new_tag("h2")
            button = soup.new_tag("button")
            button["type"] = "button"
            button["class"] = "wf-content-toc-toggle"
            button["aria-expanded"] = "false"
            label = soup.new_tag("span")
            label.string = "Table of Contents"
            icon = soup.new_tag("span")
            icon["class"] = "wf-content-toc-toggle-icon"
            icon["aria-hidden"] = "true"
            icon.string = "▸"
            button.append(icon)
            button.append(label)
            title.append(button)
            nav.append(title)
            items = soup.new_tag("ol")
            for heading in headings:
                item = soup.new_tag("li")
                item["class"] = f"wf-content-toc-level-{heading['level']}"
                link = soup.new_tag("a", href=heading["href"])
                link.string = heading["title"]
                item.append(link)
                items.append(item)
            nav.append(items)
            root.insert(0, nav)
            toc_nav = nav

        if data.get("colab"):
            actions = soup.new_tag("div")
            actions["class"] = "wf-content-actions"
            link = soup.new_tag("a", href=str(data["colab"]))
            link["class"] = "wf-content-colab-link"
            link["target"] = "_blank"
            link["rel"] = "noopener noreferrer"
            link["aria-label"] = "Open in Colab"
            link["title"] = "Open in Colab"
            image = soup.new_tag("img", src=f"{asset_base}/assets/images/colab-badge.svg")
            image["alt"] = "Open in Colab"
            link.append(image)
            actions.append(link)
            if toc_nav:
                toc_nav.insert_after(actions)
            else:
                root.insert(0, actions)

        if root is not soup:
            return "".join(str(child) for child in root.contents)
        return str(root)

    def is_math_heading(self, text: str) -> bool:
        stripped = text.strip()
        if not stripped.startswith("$") or not stripped.endswith("$"):
            return False
        inner = stripped.strip("$").strip()
        if inner and set(inner) <= {"=", "-", " ", "\t"}:
            return True
        return any(marker in stripped for marker in ("\\", "_", "^", "{", "}", "\\sum", "\\gamma", "\\infty"))

    def render(self, data: dict[str, Any], ctx: NodeContext, builder) -> str:
        if "_before_content_sections" not in data or "_after_content_sections" not in data:
            data = self.process(data, ctx, builder)
        return super().render(data, ctx, builder)
