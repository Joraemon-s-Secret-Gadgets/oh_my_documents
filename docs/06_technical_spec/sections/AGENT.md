# Agent Instructions for technical_spec sections

`sections/*.md` files are the chapter-level editing source for `../06_technical_spec.md`.

## Source of Truth

- Edit the matching section file first when changing representative document content.
- `../06_technical_spec.md` is the integrated representative document assembled from these section files.
- Each section file must contain the same content as the matching top-level `#` section in `../06_technical_spec.md` after synchronization.
- Do not treat section files as unrelated standalone documents.

## Update Rule

- When a section file changes, regenerate or update `../06_technical_spec.md` in the same change.
- The split boundary is a top-level Markdown heading that starts with `# `.
- Do not create an `index.md` file in this folder.
