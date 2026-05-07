# CLAUDE.md

This repository contains a small set of personal dotfiles for a macOS development setup. It is a
public-facing repo, but it is maintained primarily for personal use rather than as a general
purpose dotfiles framework.

## Purpose

The repo stores shell, terminal, tmux, Zed editor, and Claude Code configuration, along with a
Brewfile and a few helper scripts used to apply or support that setup.

## Structure

- `bin/`: repo-level helper scripts (`apply`, `setup`, `sync`)
- `src/`: the actual config files and supporting shell utilities

Tracked paths under `src/` mirror their destination under `$HOME`. For example,
`src/.config/zed/settings.json` applies to `~/.config/zed/settings.json`.

`src/Brewfile` is the exception — it lives in the repo but is not copied anywhere; `bin/setup`
runs `brew bundle --file` against it directly.

## Rules

- Any change to the repo structure, setup process, or documented behaviour must also be reflected
  in `README.md`.
- `bin/apply` and `bin/sync` must manage the same set of tracked config paths in opposite
  directions.
- When adding URLs to Markdown files, use Markdown reference links instead of inline links.
