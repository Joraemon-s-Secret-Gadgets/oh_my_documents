# Agent Instructions for project plan supplemental docs

`supplemental/*.md` files store supporting notes, rationale, and extracted detail for the project plan.

## Source of Truth

- `../sections/*.md` is the editing source for project-plan body content.
- `../00_project_plan.md` is the integrated representative document assembled from section files.
- Supplemental files are not standalone representative documents.

## Update Rule

- Keep supplemental documents in this folder, not in the `docs/00_project_plan/` root.
- When supplemental content should become part of the project plan, update the matching `../sections/*.md` first and then regenerate `../00_project_plan.md`.
- Do not create an `index.md` file in this folder.
