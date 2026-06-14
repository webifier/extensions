from __future__ import annotations

from .analytics.google.extension import GoogleAnalyticsExtension
from .chapters.extension import ChaptersExtension
from .comments.extension import CommentsExtension
from .markdown.extension import MarkdownExtension
from .notebook.extension import NotebookExtension
from .people.extension import PeopleExtension
from .resume.extension import ResumeExtension
from .search.extension import SearchExtension
from .standard.extension import StandardExtension
from .theme.extension import ThemeExtension

EXTENSIONS = {
    "webifier.standard": StandardExtension,
    "webifier.markdown": MarkdownExtension,
    "webifier.notebook": NotebookExtension,
    "webifier.search": SearchExtension,
    "webifier.theme": ThemeExtension,
    "webifier.analytics.google": GoogleAnalyticsExtension,
    "webifier.comments": CommentsExtension,
    "webifier.people": PeopleExtension,
    "webifier.chapters": ChaptersExtension,
    "webifier.resume": ResumeExtension,
}
