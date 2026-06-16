from __future__ import annotations

from webifier.core.extensions import Extension, ExtensionContext


class SearchExtension(Extension):
    id = "webifier.search"
    default_config = {
        "content": True,
        "links": True,
        "ui": True,
    }

    def register(self, ctx: ExtensionContext) -> None:
        super().register(ctx)
        ctx.add_hook("after_build", self.save_search_index)

    def save_search_index(self, builder, **_kwargs) -> None:
        builder.save_search_json()
