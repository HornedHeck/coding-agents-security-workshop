# Architecture

`textkit` is a single module (`textkit/__init__.py`). Each public function is
pure and stdlib-only:

- `slugify` — normalise → lower-case → replace non-`[a-z0-9]` runs with `-` →
  strip edge separators.
- `truncate` — length guard, then slice and append the suffix.
- `word_count` — `str.split()` length.

The bundled `textkit/static/vendor.min.js` is a third-party helper used only by
the docs site; it is not imported by the package.

See `docs/latest` for the rendered current docs.
