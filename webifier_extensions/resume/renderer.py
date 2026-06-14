from __future__ import annotations

from webifier_extensions.standard.section import SectionRenderer


class ResumeExperienceRenderer(SectionRenderer):
    """Section renderer using the first-party resume experience template."""

    def process(self, data, ctx, builder):
        data = dict(data)
        data.setdefault("template", "experience.html")
        return super().process(data, ctx, builder)


class ResumePublicationsRenderer(SectionRenderer):
    """Section renderer using the first-party resume publications template."""

    def process(self, data, ctx, builder):
        data = dict(data)
        data.setdefault("template", "publications.html")
        return super().process(data, ctx, builder)
