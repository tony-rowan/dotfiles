# dotfiles

Small, opinionated dotfiles for my own day-to-day macOS setup.

This is not a generic bootstrap framework or a fully automated workstation setup. It is a public
snapshot of a personal shell, terminal, and tmux configuration, plus a couple of utility scripts.

## Requirements

Install these first using your preferred method:

- macOS
- [Source Code Pro ExtraLight][source-code-pro]
- [Alacritty][alacritty]
- [`oh-my-zsh`][oh-my-zsh]
- [Homebrew][homebrew]

## Setup

```sh
bin/setup
```

`bin/setup` installs the remaining Homebrew-managed tooling dependencies: `git`, [`tmux`][tmux],
[`tpm`][tpm], [`mise`][mise], [`neovim`][neovim], and [`Visual Studio Code`][visual-studio-code].

## Assumptions

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
│   ├── setup
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
- `bin/setup`: installs the Homebrew-managed third-party tools assumed by the repo.
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

[alacritty]: https://alacritty.org/
[source-code-pro]: https://fonts.adobe.com/fonts/source-code-pro
[oh-my-zsh]: https://ohmyz.sh/
[homebrew]: https://brew.sh/
[tmux]: https://github.com/tmux/tmux/wiki
[tpm]: https://github.com/tmux-plugins/tpm
[mise]: https://mise.jdx.dev/
[neovim]: https://formulae.brew.sh/formula/neovim
[visual-studio-code]: https://formulae.brew.sh/cask/visual-studio-code
