from __future__ import annotations

from webifier.core.extensions import Extension


class PeopleExtension(Extension):
    id = "webifier.people"
    dependencies = ("webifier.standard",)
    renderers = {
        "people": "webifier_extensions.people.renderer.PeopleRenderer",
    }
