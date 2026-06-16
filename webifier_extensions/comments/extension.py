from __future__ import annotations

from webifier.core.extensions import Extension


class CommentsExtension(Extension):
    id = "webifier.comments"
    renderers = {
        "comments": "webifier_extensions.comments.renderer.CommentsRenderer",
    }
