from __future__ import annotations

from typing import Any, ClassVar

from webifier.core.base import NodeContext, RendererModule


class ChaptersRenderer(RendererModule):
    """Render chapters as a Bootstrap accordion."""

    template: ClassVar[str] = "macros/chapters.html"
    META_KEYS: ClassVar[frozenset[str]] = frozenset(
        {
            "kind",
            "template",
            "label",
            "background",
            "style",
            "content",
        }
    )

    def process(self, data: dict[str, Any], ctx: NodeContext, builder) -> dict[str, Any]:
        """Process each chapter's content recursively."""
        processed = dict(data)
        if "content" in processed and isinstance(processed["content"], list):
            chapters = []
            for i, chapter in enumerate(processed["content"]):
                if isinstance(chapter, dict):
                    chapter_processed = {}
                    for key, value in chapter.items():
                        if key in ("title",):
                            chapter_processed[key] = value
                        else:
                            chapter_processed[key] = builder.process_node(
                                value, ctx.child(f"chapter-{i}")
                            )
                    chapters.append(chapter_processed)
                else:
                    chapters.append(chapter)
            processed["content"] = chapters
        return processed

    def render(self, data: dict[str, Any], ctx: NodeContext, builder) -> str:
        template = builder.jinja_env.get_template(self.template)
        return template.module.render_chapters(
            data,
            data.get("content", []),
            ctx.depth,
        )
