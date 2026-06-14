# Webifier Extensions

First-party extensions for Webifier.

This distribution is installed automatically when users install `webifier`:

```shell
pip install webifier
```

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
