from __future__ import annotations

from typing import Any, ClassVar

from webifier.core.base import NodeContext, RendererModule


class CommentsRenderer(RendererModule):
    """Render an Utterances comment widget."""

    template: ClassVar[str] = "macros/comments.html"
    META_KEYS: ClassVar[frozenset[str]] = frozenset(
        {
            "kind",
            "template",
            "label",
            "background",
            "style",
            "repo",
            "issue_term",
            "issue_label",
            "theme",
            "crossorigin",
        }
    )

    def process(self, data: dict[str, Any], ctx: NodeContext, builder) -> dict[str, Any]:
        """No children to process — just pass config through."""
        # Inject global config for repo fallback
        data["_config"] = builder.config
        return data

    def render(self, data: dict[str, Any], ctx: NodeContext, builder) -> str:
        template = builder.jinja_env.get_template(self.template)
        return template.module.render_comments(data, data.get("_config"))
