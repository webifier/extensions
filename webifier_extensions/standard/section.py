from __future__ import annotations

from typing import Any, ClassVar

from webifier.core.base import GenericTemplateRenderer, NodeContext, RendererModule


class SectionRenderer(RendererModule):
    """Render a section container with label and children."""

    template: ClassVar[str] = "section.html"
    META_KEYS: ClassVar[frozenset[str]] = frozenset(
        {
            "kind",
            "template",
            "label",
            "background",
            "style",
            "freeform",
            "defaults",
        }
    )

    def process(self, data: dict[str, Any], ctx: NodeContext, builder) -> dict[str, Any]:
        """Process children, resolve background images."""
        processed = {}
        children = []

        # If a custom template is specified, use it to render the inner content
        # instead of recursing into individual children.
        inner_template = data.get("template")

        for key, value in data.items():
            if key in self.META_KEYS:
                processed[key] = value
                continue
            if inner_template:
                # Don't recurse — the template will handle children
                children.append({"key": key, "html": "", "data": value})
            else:
                child_html = builder.process_node(value, ctx.child(key))
                children.append({"key": key, "html": child_html, "data": value})

        processed["_children"] = children

        # Render inner content with custom template if specified
        if inner_template:
            tmpl_renderer = GenericTemplateRenderer(template=inner_template)
            inner_data = {k: v for k, v in data.items() if k not in self.META_KEYS}
            processed["_inner_html"] = tmpl_renderer.render(inner_data, ctx, builder)

        processed = builder.resolve_background(processed, ctx)

        # Parse label config
        label = processed.get("label", ctx.key)
        if isinstance(label, dict):
            processed["_label_text"] = label.get("text", ctx.key)
            processed["_label_position"] = label.get("position", "left")
            processed["_label_disabled"] = False
        elif label is False:
            processed["_label_text"] = ""
            processed["_label_disabled"] = True
            processed["_label_position"] = "left"
        else:
            processed["_label_text"] = str(label)
            processed["_label_disabled"] = False
            processed["_label_position"] = "left"

        return processed
