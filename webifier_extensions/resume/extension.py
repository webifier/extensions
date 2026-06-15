from __future__ import annotations

from markupsafe import Markup
from webifier.core.extensions import AssetMount, Extension, ExtensionContext

from webifier_extensions._resources import package_path


def _page_uses_resume(value) -> bool:
    if isinstance(value, dict):
        kind = value.get("kind")
        if kind in {"resume.experience", "resume-experience", "resume.publications"}:
            return True
        if "_sections" in value:
            for section in value["_sections"]:
                if isinstance(section, dict) and _page_uses_resume(section.get("data")):
                    return True
        return any(_page_uses_resume(item) for item in value.values())
    if isinstance(value, list):
        return any(_page_uses_resume(item) for item in value)
    return False


class ResumeExtension(Extension):
    id = "webifier.resume"
    dependencies = ("webifier.standard",)
    template_dirs = [package_path("webifier_extensions.resume")]
    assets = [
        AssetMount(
            package_path("webifier_extensions.resume", "assets"),
            "assets/webifier/resume",
        )
    ]
    renderers = {
        "resume.experience": "webifier_extensions.resume.renderer.ResumeExperienceRenderer",
        "resume-experience": "webifier_extensions.resume.renderer.ResumeExperienceRenderer",
        "resume.publications": "webifier_extensions.resume.renderer.ResumePublicationsRenderer",
    }

    def register(self, ctx: ExtensionContext) -> None:
        super().register(ctx)
        ctx.add_hook("head", self.render_head)

    def render_head(self, builder, *, baseurl: str = "", page=None, **_kwargs) -> str:
        if not _page_uses_resume(page):
            return ""
        prefix = baseurl.rstrip("/")
        return Markup(
            "\n".join(
                [
                    f'<link rel="stylesheet" href="{prefix}/assets/webifier/resume/css/resume.css">',
                    f'<script defer src="{prefix}/assets/webifier/resume/js/resume.js"></script>',
                ]
            )
        )
