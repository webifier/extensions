from __future__ import annotations

import os
from html import escape

from markupsafe import Markup
from webifier.core.base import resolve_renderer
from webifier.core.extensions import AssetMount, Extension, ExtensionContext
from webifier.core.loader import read_yaml
from webifier.interface.io import prepend_baseurl, strip_suffixes

from webifier_extensions._resources import package_path


class PdfExtension(Extension):
    id = "webifier.pdf"
    dependencies = ("webifier.standard",)
    default_config = {
        "height": "min(82vh, 1100px)",
        "toolbar": True,
        "download": True,
    }
    assets = [
        AssetMount(
            package_path("webifier_extensions.pdf", "assets"),
            "assets/webifier/pdf",
        )
    ]

    def register(self, ctx: ExtensionContext) -> None:
        self.config_namespace = ctx.instance_name
        super().register(ctx)
        for key in (".pdf", "pdf"):
            ctx.register_content_renderer(key, self.build_pdf_page)
        ctx.add_hook("head", self.render_head)

    def build_pdf_page(self, builder, src: str, ctx):
        if not os.path.isfile(src):
            print(f"  Warning: PDF file not found: {src}")
            return None

        metadata_path = os.path.join(os.path.dirname(src), "page.yml")
        if not os.path.isfile(metadata_path):
            metadata_path = os.path.join(os.path.dirname(src), "metadata.yml")
        metadata = read_yaml(metadata_path) if os.path.isfile(metadata_path) else {}
        title = metadata.get("title") or os.path.splitext(os.path.basename(src))[0].replace("-", " ").title()
        pdf_url = builder.files.copy_file(src, src)
        page_data = {
            "metadata": metadata,
            "title": title,
            "page_url": prepend_baseurl(
                strip_suffixes(src, builder._content_suffixes()),
                builder.base_url,
            ),
            "source_path": src,
            "_content_config_namespace": self.config_namespace,
            "pdf": {
                "src": pdf_url,
                "source_path": src,
            },
        }
        if builder.root_data:
            page_data["nav"] = builder.root_data.get("nav")
            page_data["footer"] = builder.root_data.get("footer")

        page_config = builder.page_config(page_data)
        pdf_config = page_config.get(self.config_namespace, {})
        if not isinstance(pdf_config, dict):
            pdf_config = {}
        height = pdf_config.get("height", self.default_config["height"])
        view = pdf_config.get("view", "FitH")
        pdf_src = f"{pdf_url}#view={escape(str(view), quote=True)}" if view else pdf_url

        actions = []
        if pdf_config.get("toolbar", True):
            actions.append(
                f'<a class="wf-pdf-link" href="{escape(pdf_url)}" target="_blank" rel="noopener">Open PDF</a>'
            )
        if pdf_config.get("download", True):
            actions.append(f'<a class="wf-pdf-link" href="{escape(pdf_url)}" download>Download</a>')
        actions_html = f'<div class="wf-pdf-actions">{"".join(actions)}</div>' if actions else ""
        body_html = Markup(
            "\n".join(
                [
                    '<section class="wf-pdf-document">',
                    f'<iframe class="wf-pdf-frame" src="{escape(pdf_src)}" title="{escape(title)}" '
                    f'style="--wf-pdf-height: {escape(str(height))};"></iframe>',
                    actions_html,
                    "</section>",
                ]
            )
        )

        content_pages = dict(page_config.get("content_pages", {}))
        if "toc" in pdf_config:
            content_pages["toc"] = pdf_config["toc"]
        if "cleanup" in pdf_config:
            content_pages["cleanup"] = pdf_config["cleanup"]
        if "toc" not in content_pages:
            content_pages["toc"] = False
        page_config["content_pages"] = content_pages
        page_data["content"] = body_html
        page_data["config"] = page_config
        renderer = resolve_renderer("content-page", jinja_env=builder.jinja_env)
        return renderer.render(page_data, ctx, builder)

    def render_head(self, builder, *, baseurl: str = "", page=None, **_kwargs) -> str:
        if isinstance(page, dict) and page.get("pdf"):
            prefix = baseurl.rstrip("/")
            return Markup(f'<link rel="stylesheet" href="{prefix}/assets/webifier/pdf/css/pdf.css">')
        return ""
