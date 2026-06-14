from __future__ import annotations

import os

from webifier.core.base import resolve_renderer
from webifier.core.extensions import Extension, ExtensionContext
from webifier.interface.io import prepend_baseurl, strip_suffixes

from .converter import convert_notebook


class NotebookExtension(Extension):
    id = "webifier.notebook"
    dependencies = ("webifier.standard",)

    def register(self, ctx: ExtensionContext) -> None:
        super().register(ctx)
        for key in (".ipynb", "notebook"):
            ctx.register_content_renderer(key, self.build_notebook_page)

    def build_notebook_page(self, builder, src: str, ctx):
        if not os.path.isfile(src):
            print(f"  Warning: notebook file not found: {src}")
            return None

        try:
            body_html, metadata = convert_notebook(builder, src, builder.assets_dir)
        except Exception as exc:
            print(f"  Warning: notebook conversion failed for {src}: {exc}")
            return None

        renderer = resolve_renderer("content-page", jinja_env=builder.jinja_env)
        page_data = {
            "content": body_html,
            "metadata": metadata,
            "title": metadata.get("title", os.path.basename(src)),
            "page_url": prepend_baseurl(
                strip_suffixes(src, builder._content_suffixes()),
                builder.base_url,
            ),
            "source_path": src,
        }
        if builder.root_data:
            page_data["nav"] = builder.root_data.get("nav")
            page_data["footer"] = builder.root_data.get("footer")
            page_data["config"] = builder.config
        if builder.repo_full_name:
            nb_dir = os.path.dirname(src)
            nb_name = strip_suffixes(os.path.basename(src), [".ipynb"])
            page_data["colab"] = (
                f"https://colab.research.google.com/github/"
                f"{builder.repo_full_name}/blob/master/{nb_dir}/{nb_name}.ipynb"
            )
        return renderer.render(page_data, ctx, builder)
