# Webifier Extensions

[![Docs](https://img.shields.io/badge/docs-webifier.github.io-blue)](https://webifier.github.io/)
[![PyPI](https://img.shields.io/pypi/v/webifier-extensions.svg)](https://pypi.org/project/webifier-extensions/)
[![Python Package](https://github.com/webifier/extensions/actions/workflows/python-publish.yml/badge.svg)](https://github.com/webifier/extensions/actions/workflows/python-publish.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

First-party extensions for Webifier.

This distribution is installed automatically when users install `webifier`:

```shell
pip install webifier
```

Documentation and examples live at [webifier.github.io](https://webifier.github.io/).

For local extension development, install this package in the same environment as
the local Webifier core.

Enable named instances in a site configuration:

```yaml
config:
  webifier:
    extensions:
      site:
        uses: webifier.standard
      markdown:
        uses: webifier.markdown
      search:
        uses: webifier.search
```

Extensions can register renderers, content renderers, templates, themes, assets,
resolvers, format loaders, hooks, and config defaults. Hooks are page-aware, so a
`head` hook can inspect the current page data or page-local config and inject
JavaScript only on pages that need it.
