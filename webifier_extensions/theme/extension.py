from __future__ import annotations

from markupsafe import Markup
from webifier.core.extensions import AssetMount, Extension, ExtensionContext

from webifier_extensions._resources import package_path


class ThemeExtension(Extension):
    id = "webifier.theme"
    config_key = "theme"
    default_config = {
        "switcher": True,
        "default": "system",
    }
    assets = [AssetMount(package_path("webifier_extensions.theme", "assets"), "assets")]

    def register(self, ctx: ExtensionContext) -> None:
        super().register(ctx)
        ctx.add_hook("head", self.render_head)

    def render_head(self, builder, *, baseurl: str = "", config=None, **_kwargs) -> str:
        theme = (config or {}).get("theme", {}) if isinstance(config, dict) else {}
        default = theme.get("default", "system")
        switcher = theme.get("switcher", True)
        custom_themes = theme.get("themes", []) or []
        switcher_js = "true" if switcher else "false"
        links = [
            "<script>",
            "(function () {",
            f"  const switcherEnabled = {switcher_js};",
            '  const stored = switcherEnabled ? localStorage.getItem("webifier-theme") : null;',
            f'  const selected = stored || "{default}";',
            '  const systemDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;',
            '  const resolved = selected === "system" ? (systemDark ? "dark" : "light") : selected;',
            "  document.documentElement.dataset.wfTheme = selected;",
            "  document.documentElement.dataset.wfResolvedTheme = resolved;",
            '  document.documentElement.dataset.bsTheme = resolved === "dark" ? "dark" : "light";',
            "})();",
            "</script>",
            f'<link rel="stylesheet" href="{baseurl}/assets/css/theme.css">',
        ]
        for item in custom_themes:
            href = item.get("css") if isinstance(item, dict) else None
            if not href:
                continue
            if "://" not in href and not href.startswith("/"):
                href = f"{baseurl}/{href}"
            links.append(f'<link rel="stylesheet" href="{href}">')
        if switcher:
            links.append(f'<script defer src="{baseurl}/assets/js/theme.js"></script>')
        return Markup("\n".join(links))
