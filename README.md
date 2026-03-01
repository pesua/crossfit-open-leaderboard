# openscrollytelling

## Dev Container Setup

This project includes a Claude Code devcontainer configuration for isolated development.

### What's configured

- **Network policy**: Fully permissive — all inbound and outbound traffic allowed via iptables rules at container start.
- **Tool permissions**: All Claude Code tools (`Bash`, `Read`, `Edit`, `Write`, `WebFetch`, `WebSearch`, `Grep`, `Glob`, `Task`, `mcp__*`) are pre-allowed in `.claude/settings.json`. Global config tools are inherited automatically via setting merge.
- **Actions**: All actions allowed without interactive permission prompts.

### Files

```
.devcontainer/devcontainer.json   # Container image, network caps, permissive firewall
.claude/settings.json             # Claude Code tool permissions (project-level)
```

### Usage

Open the project in VS Code or a compatible editor and reopen in container, or run:

```sh
devcontainer up --workspace-folder .
```
