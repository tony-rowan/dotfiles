# AGENTS

This repository contains a small set of personal dotfiles for a macOS development setup. It is a
public-facing repo, but it is maintained primarily for personal use rather than as a general
purpose dotfiles framework.

## Purpose

The repo stores shell, terminal, and tmux configuration, along with a few helper scripts used to
apply or support that setup.

## Structure

- `bin/`: repo-level helper scripts
- `src/`: the actual config files and supporting shell utilities

## Rules

- Any change to the repo structure, setup process, or documented behaviour must also be reflected
  in `README.md`.
- `bin/apply` and `bin/sync` must manage the same set of tracked config paths in opposite
  directions.
- When adding URLs to Markdown files, use Markdown reference links instead of inline links.
