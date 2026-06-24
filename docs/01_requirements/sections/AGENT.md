# Agent Instructions for requirements sections

`sections/*.md` files are the chapter-level editing source for `../01_requirements.md`.

## Source of Truth

- Edit the matching section file first when changing representative document content.
- `../01_requirements.md` is the integrated representative document assembled from these section files.
- Each section file must contain the same content as the matching top-level `#` section in `../01_requirements.md` after synchronization.
- Do not treat section files as unrelated standalone documents.

## Update Rule

- When a section file changes, regenerate or update `../01_requirements.md` in the same change.
- The split boundary is a top-level Markdown heading that starts with `# `.
- Do not create an `index.md` file in this folder.
