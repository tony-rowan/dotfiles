# dotfiles

Small, opinionated dotfiles for my own day-to-day macOS setup.

This is not a generic bootstrap framework or a fully automated workstation setup. It is a public
snapshot of a personal shell, terminal, and tmux configuration, plus a couple of utility scripts.

## Requirements and Assumptions

Install these first using your preferred method:

- macOS
- Alacritty
- `oh-my-zsh` installed at `~/.oh-my-zsh`
- `Source Code Pro ExtraLight`

Then install Homebrew itself and use it for the command-line dependencies:

- Homebrew

```sh
brew install git tmux tpm asdf
```

Assumptions baked into the config:

- tmux plugin manager is loaded from `/opt/homebrew/opt/tpm/share/tpm/tpm`.
- Optional machine-specific aliases live in `~/.aliases`.

## What is here

The repo has two top-level directories:

- `bin/` for repo helper scripts
- `src/` for the actual config files and shell utilities

```text
.
├── bin/
│   ├── AGENTS.md
│   ├── apply
│   └── sync
└── src/
    ├── .config/
    │   └── alacritty/
    ├── .default-gems
    ├── .zshrc
    ├── bin/
    └── tmux/
```

### Repo Scripts (`bin/`)

- `bin/apply`: copies the tracked config from `src/` into the matching locations under `$HOME`,
  including `~/bin/`, `~/.zshrc`, `~/.default-gems`, `~/.config/alacritty/`, and
  `~/.config/tmux/`.
- `bin/sync`: copies the current workstation config from `$HOME` back into the tracked locations
  under `src/`.

### Config (`src/`)

- `src/.zshrc`: `zsh` shell config; loads `oh-my-zsh`, enables the `asdf`, `git`, `ruby`, and
  `rails` plugins, and adds a few aliases and machine-local hooks.
- `src/.config/alacritty/`: Alacritty config; loads a separate theme file, uses `Source Code Pro
  ExtraLight`, and maps macOS-style key bindings for tmux control.
- `src/tmux/tmux.conf`: tmux config; sets status bar options, pane and window behaviour, mouse
  support, history size, and plugins.
- `src/tmux/shortpath.sh`: tmux helper script; shortens long paths in the status line.
- `src/bin/git-remove-other-branches`: git helper script; deletes every local branch except the
  current one.
- `src/.default-gems`: Ruby default gems file; installs a small baseline set of gems.
