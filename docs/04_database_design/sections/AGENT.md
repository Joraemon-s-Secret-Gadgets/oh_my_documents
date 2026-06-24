# Agent Instructions for database_design sections

`sections/*.md` files are the chapter-level editing source for `../04_database_design.md`.

## Source of Truth

- Edit the matching section file first when changing representative document content.
- `../04_database_design.md` is the integrated representative document assembled from these section files.
- Each section file must contain the same content as the matching top-level `#` section in `../04_database_design.md` after synchronization.
- Do not treat section files as unrelated standalone documents.

## Update Rule

- When a section file changes, regenerate or update `../04_database_design.md` in the same change.
- The split boundary is a top-level Markdown heading that starts with `# `.
- Do not create an `index.md` file in this folder.
