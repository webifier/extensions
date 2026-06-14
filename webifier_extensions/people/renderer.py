from __future__ import annotations

from typing import Any, ClassVar

from webifier.core.base import NodeContext, RendererModule


class PeopleRenderer(RendererModule):
    """Render a grid of people cards."""

    template: ClassVar[str] = "macros/people.html"
    META_KEYS: ClassVar[frozenset[str]] = frozenset(
        {
            "kind",
            "template",
            "label",
            "background",
            "style",
            "content",
        }
    )

    def process(self, data: dict[str, Any], ctx: NodeContext, builder) -> dict[str, Any]:
        """Process each person entry."""
        processed = dict(data)
        if "content" in processed and isinstance(processed["content"], list):
            people = []
            for person in processed["content"]:
                if isinstance(person, dict):
                    person = _process_person(person, ctx, builder)
                people.append(person)
            processed["content"] = people
        return processed

    def render(self, data: dict[str, Any], ctx: NodeContext, builder) -> str:
        template = builder.jinja_env.get_template(self.template)
        return template.module.render_people(data)


def _process_person(person: dict, ctx: NodeContext, builder) -> dict:
    """Process a single person dict — resolve images, render bio."""
    # Resolve profile image
    if "image" in person:
        img = person["image"]
        if isinstance(img, str) and not img.startswith(("http", "data:")):
            new_path = builder.files.copy_file(
                img,
                img,
                src_dir=ctx.assets_src_dir,
                target_dir=ctx.assets_target_dir or builder.assets_dir,
            )
            if new_path:
                person["image"] = new_path
        elif "github" in person:
            person["image"] = f"https://github.com/{person['github']}.png"

    # GitHub-derived image fallback
    if "image" not in person and "github" in person:
        person["image"] = f"https://github.com/{person['github']}.png"

    # Render bio as markdown
    if "bio" in person and isinstance(person["bio"], str):
        person["bio"] = builder.render_markdown(
            person["bio"],
            assets_src_dir=ctx.assets_src_dir,
            assets_target_dir=ctx.assets_target_dir,
        )

    # Process contact links
    if "contact" in person and isinstance(person["contact"], list):
        processed_links = []
        for link in person["contact"]:
            if isinstance(link, dict):
                link = builder._process_link(link, ctx)
            processed_links.append(link)
        person["contact"] = processed_links

    return person
