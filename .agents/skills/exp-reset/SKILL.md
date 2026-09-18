---
name: exp-reset
description: List and remove selected dated projects from this MVP workbench, with recoverable backups. Use when the user asks to delete practice projects or reset for another exercise; supports single or multiple selections.
---

# exp reset

Follow [AGENTS.md](../../../AGENTS.md) for workspace conventions. Run the bundled `scripts/reset.py` without arguments to list eligible projects. It finds the workbench from its own location, independent of the current directory.

When the user has not named exact targets, show the returned project names as a numbered list and ask them to select one or more (for example, “1, 3”). Wait for their answer; never infer “latest” or “all.” Map their choice to the names from that list and recheck availability. If the user already specified exact targets, that is the selection and authorization; do not ask again. An explanation of reset or finishing a build is not authorization to remove projects.

Preview the selection with `python3 <skill-directory>/scripts/reset.py --project <exact-name>`, repeating `--project` for multiple projects. Stop any known development server or watcher belonging to those projects using its exact process/session. If it cannot be stopped, report the blocker before proceeding. Do not broadly kill processes.

For an authorized selection, run the same command with `--apply`. It moves only those project directories into a timestamped `.practice-backups/` batch. It does not recreate them; use exp-build and the shared scaffold to start another project. Names must be dated direct children with the project marker. The script rejects missing or unrecognized targets before moving anything.

Report removed names and the backup location. Toolkit files, scaffold, and unselected projects remain in place. Browser storage, external databases, and cloud resources are outside this local operation. Never substitute repository-wide reset/clean commands or permanently delete backups.
