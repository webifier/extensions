from __future__ import annotations

from webifier.core.extensions import Extension


class ChaptersExtension(Extension):
    id = "webifier.chapters"
    dependencies = ("webifier.standard",)
    renderers = {
        "chapters": "webifier_extensions.chapters.renderer.ChaptersRenderer",
    }
