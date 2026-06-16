from __future__ import annotations

from markupsafe import Markup
from webifier.core.extensions import Extension, ExtensionContext


class GoogleAnalyticsExtension(Extension):
    id = "webifier.analytics.google"

    def register(self, ctx: ExtensionContext) -> None:
        super().register(ctx)
        ctx.add_hook("head", self.render_head)

    def render_head(self, builder, *, config=None, instance_name: str = "analytics", **_kwargs) -> str:
        analytics = {}
        if isinstance(config, dict):
            analytics = config.get(instance_name, {})
        if analytics is False or (
            isinstance(analytics, dict) and analytics.get("enabled") is False
        ):
            return ""
        if not isinstance(analytics, dict):
            analytics = {}
        measurement_id = analytics.get("measurement_id") or analytics.get("id")
        if not measurement_id:
            return ""
        return Markup(
            "\n".join(
                [
                    "<!-- Global site tag (gtag.js) - Google Analytics -->",
                    f'<script async src="https://www.googletagmanager.com/gtag/js?id={measurement_id}"></script>',
                    "<script>",
                    "  window.dataLayer = window.dataLayer || [];",
                    "  function gtag(){dataLayer.push(arguments);}",
                    "  gtag('js', new Date());",
                    f"  gtag('config', '{measurement_id}');",
                    "</script>",
                ]
            )
        )
