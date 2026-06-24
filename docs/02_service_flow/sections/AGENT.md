# Agent Instructions for service_flow sections

`sections/*.md` files are the chapter-level editing source for `../02_service_flow.md`.

## Source of Truth

- Edit the matching section file first when changing representative document content.
- `../02_service_flow.md` is the integrated representative document assembled from these section files.
- Each section file must contain the same content as the matching top-level `#` section in `../02_service_flow.md` after synchronization.
- Do not treat section files as unrelated standalone documents.

## Update Rule

- When a section file changes, regenerate or update `../02_service_flow.md` in the same change.
- The split boundary is a top-level Markdown heading that starts with `# `.
- Do not create an `index.md` file in this folder.
