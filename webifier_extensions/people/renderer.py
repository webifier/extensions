from __future__ import annotations

from typing import Any, ClassVar

from webifier.core.base import NodeContext

from webifier_extensions.standard.section import SectionRenderer


class PeopleRenderer(SectionRenderer):
    """Render a labeled section containing a configurable people grid."""

    template: ClassVar[str] = "section.html"
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
        processed = dict(data)
        processed.setdefault("template", "people.html")
        people = processed.get("people", processed.get("content", []))
        if isinstance(people, list):
            processed["people"] = [
                self.process_person(person, ctx, builder) if isinstance(person, dict) else person
                for person in people
            ]
        return super().process(processed, ctx, builder)

    def process_person(self, person: dict, ctx: NodeContext, builder) -> dict:
        person = dict(person)
        person.setdefault("title", person.get("role"))
        if "roles" in person and "tags" not in person:
            person["tags"] = person["roles"]
        if "contact" in person and "links" not in person:
            person["links"] = person["contact"]
        if "description" in person and "bio" not in person:
            person["bio"] = person["description"]

        image = person.get("image") or person.get("avatar")
        if isinstance(image, str) and image:
            if not image.startswith(("http", "data:")):
                new_path = builder.files.copy_file(
                    image,
                    image,
                    src_dir=ctx.assets_src_dir,
                    target_dir=ctx.assets_target_dir or builder.assets_dir,
                )
                if new_path:
                    person["image"] = new_path
            else:
                person["image"] = image
        elif "github" in person:
            person["image"] = f"https://github.com/{person['github']}.png"

        if "github" in person and "links" not in person:
            person["links"] = [
                {
                    "text": "GitHub",
                    "link": f"https://github.com/{person['github']}",
                    "icon": "fab fa-github",
                }
            ]

        if "links" in person and isinstance(person["links"], list):
            processed_links = []
            for link in person["links"]:
                if isinstance(link, dict):
                    href = link.get("href", link.get("link", ""))
                    if isinstance(href, str) and href.startswith("mailto://"):
                        href = f"mailto:{href.removeprefix('mailto://')}"
                        if "href" in link:
                            link["href"] = href
                        else:
                            link["link"] = href
                    if "icon" not in link and isinstance(href, str):
                        if "github.com" in href:
                            link["icon"] = "fab fa-github"
                        elif href.startswith("mailto"):
                            link["icon"] = "fas fa-envelope"
                        elif "linkedin.com" in href:
                            link["icon"] = "fab fa-linkedin"
                        elif href.startswith(("http://", "https://")):
                            link["icon"] = "fas fa-globe"
                    if isinstance(href, str):
                        icon = link.get("icon", "")
                        if "github.com" in href:
                            link["icon"] = "fab fa-github"
                            link.setdefault("text", "GitHub")
                            if "image" not in person:
                                username = href.rstrip("/").split("/")[-1]
                                if username:
                                    person["image"] = f"https://github.com/{username}.png"
                        elif href.startswith("mailto"):
                            link.setdefault("text", "Email")
                        elif "linkedin.com" in href:
                            link.setdefault("text", "LinkedIn")
                        elif href.startswith(("http://", "https://")):
                            link.setdefault("text", "Website")
                        if icon == "fas fa-github":
                            link["icon"] = "fab fa-github"
                    link = builder._process_link(link, ctx)
                processed_links.append(link)
            person["links"] = processed_links

        if "image" not in person and "initials" not in person and isinstance(person.get("name"), str):
            initials = "".join(word[0] for word in person["name"].split()[:2] if word)
            if initials:
                person["initials"] = initials.upper()

        if "bio" in person and isinstance(person["bio"], str):
            person["bio"] = builder.render_markdown(
                person["bio"],
                assets_src_dir=ctx.assets_src_dir,
                assets_target_dir=ctx.assets_target_dir,
            )

        return person
