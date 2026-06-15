from __future__ import annotations

from typing import Any, ClassVar

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
        before_content = []
        after_content = []
        metadata = processed.get("metadata", {})
        if isinstance(metadata, dict):
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
                        "html": builder.process_node(author_section, ctx.child("authors")),
                        "data": author_section,
                    }
                )
            for key, value in metadata.items():
                if key in self.METADATA_KEYS or key in {"authors", "reviewers"}:
                    continue
                section = {
                    "key": key,
                    "html": builder.process_node(value, ctx.child(key)),
                    "data": value,
                }
                if key == "comments":
                    after_content.append(section)
                else:
                    before_content.append(section)
        processed["_before_content_sections"] = before_content
        processed["_after_content_sections"] = after_content
        return processed

    def render(self, data: dict[str, Any], ctx: NodeContext, builder) -> str:
        if "_before_content_sections" not in data or "_after_content_sections" not in data:
            data = self.process(data, ctx, builder)
        return super().render(data, ctx, builder)
