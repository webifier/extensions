from __future__ import annotations

import os

from webifier.core.frontmatter import split_yaml_front_matter


def convert_notebook(builder, src: str, assets_dir: str) -> tuple[str, dict]:
    """Convert a Jupyter notebook to HTML body content.

    Uses nbconvert to export, then extracts the notebook container
    and post-processes HTML for asset resolution.
    """
    from bs4 import BeautifulSoup

    try:
        from nbconvert import HTMLExporter
    except ImportError as exc:
        raise ImportError(
            "nbconvert is required for notebook conversion. Install it with: pip install nbconvert"
        ) from exc

    notebook, metadata = read_notebook_with_metadata(src)

    exporter = HTMLExporter()
    body, _ = exporter.from_notebook_node(notebook)

    # Extract just the notebook content
    soup = BeautifulSoup(body, "html.parser")
    container = soup.find(id="notebook-container") or soup.find("body") or soup
    content = str(container)

    # Post-process HTML for asset resolution
    from webifier.core.html import process_html

    content = process_html(
        builder,
        content,
        assets_src_dir=os.path.dirname(src),
        assets_target_dir=assets_dir,
    )

    return content, metadata


def read_notebook_with_metadata(src: str) -> tuple[object, dict]:
    import nbformat

    with open(src) as f:
        notebook = nbformat.read(f, as_version=4)

    cells = notebook.get("cells", [])
    if not cells or cells[0].get("cell_type") != "markdown":
        return notebook, {}

    metadata, first_cell_body = split_yaml_front_matter(cells[0].get("source", ""))
    if not metadata:
        return notebook, {}
    if first_cell_body.strip():
        cells[0]["source"] = first_cell_body.lstrip("\n")
    else:
        notebook["cells"] = cells[1:]
    return notebook, metadata
