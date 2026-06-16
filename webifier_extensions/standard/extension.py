from __future__ import annotations

from webifier.core.extensions import AssetMount, Extension

from webifier_extensions._resources import package_path


class StandardExtension(Extension):
    id = "webifier.standard"
    template_dirs = [package_path("webifier_extensions.standard", "templates")]
    assets = [AssetMount(package_path("webifier_extensions.standard", "assets"), "assets")]
    renderers = {
        "page": "webifier_extensions.standard.page.PageRenderer",
        "section": "webifier_extensions.standard.section.SectionRenderer",
        "content-page": "webifier_extensions.standard.content_page.ContentPageRenderer",
        "links": "webifier_extensions.standard.links.LinksRenderer",
        "freeform": "webifier_extensions.standard.freeform.FreeformRenderer",
    }
    config_defaults = {
        "defaults": {
            "page": "page",
            "section": "section",
            "links": "links",
            "markdown": "markdown",
        },
        "content_pages": {
            "cleanup": False,
            "toc": True,
        },
    }
