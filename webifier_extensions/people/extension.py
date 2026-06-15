from __future__ import annotations

from markupsafe import Markup
from webifier.core.extensions import AssetMount, Extension, ExtensionContext

from webifier_extensions._resources import package_path


class PeopleExtension(Extension):
    id = "webifier.people"
    dependencies = ("webifier.standard",)
    template_dirs = [package_path("webifier_extensions.people", "templates")]
    assets = [
        AssetMount(
            package_path("webifier_extensions.people", "assets"),
            "assets/webifier/people",
        )
    ]
    renderers = {
        "people": "webifier_extensions.people.renderer.PeopleRenderer",
    }

    def register(self, ctx: ExtensionContext) -> None:
        super().register(ctx)
        ctx.add_hook("head", self.render_head)

    def render_head(self, builder, *, baseurl: str = "", page=None, **_kwargs) -> str:
        if not self.page_uses_people(page):
            return ""
        return Markup(f'<link rel="stylesheet" href="{baseurl}/assets/webifier/people/css/people.css">')

    def page_uses_people(self, value) -> bool:
        if isinstance(value, dict):
            if value.get("kind") == "people":
                return True
            if "_sections" in value:
                for section in value["_sections"]:
                    if isinstance(section, dict) and self.page_uses_people(section.get("data")):
                        return True
            return any(self.page_uses_people(item) for item in value.values())
        if isinstance(value, list):
            return any(self.page_uses_people(item) for item in value)
        return False
