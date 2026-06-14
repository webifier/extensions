from __future__ import annotations

from webifier.core.extensions import Extension, ExtensionContext


class MarkdownExtension(Extension):
    id = "webifier.markdown"
    renderers = {
        "markdown": "webifier_extensions.markdown.renderer.MarkdownRenderer",
    }

    def register(self, ctx: ExtensionContext) -> None:
        super().register(ctx)
        for key in (".md", ".markdown", "md", "markdown"):
            ctx.register_content_renderer(key, self.build_markdown_page)

    def build_markdown_page(self, builder, src: str, ctx):
        return builder._build_markdown_page(src, ctx)
