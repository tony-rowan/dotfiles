#!/bin/bash
# Claude Code status line: cwd | git branch | model (+ effort/thinking) | context window |
# session usage window
#
# Reads the JSON status payload from stdin (see Claude Code docs for schema) and prints
# a single-line summary. Designed to work in any project directory, not just one repo.

input=$(cat)

# --- Working directory -------------------------------------------------
cwd=$(echo "$input" | jq -r '.workspace.current_dir // .cwd // empty')
display_cwd="$cwd"
if [ -n "$cwd" ] && [ -n "$HOME" ]; then
  case "$cwd" in
    "$HOME"/*) display_cwd="~${cwd#"$HOME"}" ;;
    "$HOME") display_cwd="~" ;;
  esac
fi

# --- Git branch (only if cwd is inside a git repo) ----------------------
git_branch=""
git_diffstat=""
if [ -n "$cwd" ] && [ -d "$cwd" ]; then
  if (cd "$cwd" 2>/dev/null && git --no-optional-locks rev-parse --is-inside-work-tree >/dev/null 2>&1); then
    git_branch=$(cd "$cwd" 2>/dev/null && git --no-optional-locks branch --show-current 2>/dev/null)
    if [ -z "$git_branch" ]; then
      # Detached HEAD: fall back to a short commit hash.
      git_branch=$(cd "$cwd" 2>/dev/null && git --no-optional-locks rev-parse --short HEAD 2>/dev/null)
    fi

    # Diff +/- counts against HEAD (staged + unstaged); omitted entirely when pristine.
    numstat=$(cd "$cwd" 2>/dev/null && git --no-optional-locks diff --numstat HEAD 2>/dev/null)
    if [ -n "$numstat" ]; then
      read -r added deleted <<<"$(echo "$numstat" | awk '{ if ($1 != "-") a+=$1; if ($2 != "-") d+=$2 } END { print a+0, d+0 }')"
      if [ "$added" -gt 0 ] || [ "$deleted" -gt 0 ]; then
        git_diffstat="+${added}/-${deleted}"
        git_diffstat_added="$added"
        git_diffstat_deleted="$deleted"
      fi
    fi
  fi
fi

# --- Model ---------------------------------------------------------------
model=$(echo "$input" | jq -r '.model.display_name // empty')

# --- Reasoning effort / thinking (merged into the model segment below) ---
effort=$(echo "$input" | jq -r '.effort.level // empty')
thinking_enabled=$(echo "$input" | jq -r '.thinking.enabled // false')
effort_label=""
if [ -n "$effort" ]; then
  effort_label="effort:$effort"
elif [ "$thinking_enabled" = "true" ]; then
  effort_label="thinking:on"
fi

# --- Context window size + usage ------------------------------------------
# context_window_size and used_percentage come pre-calculated from Claude Code;
# used_percentage is null before the first API response of the session.
ctx_size=$(echo "$input" | jq -r '.context_window.context_window_size // empty')
ctx_used_pct=$(echo "$input" | jq -r '.context_window.used_percentage // empty')

format_k() {
  # Compact a token count like 200000 into "200k"
  awk -v n="$1" 'BEGIN { printf "%dk", (n + 500) / 1000 }'
}

ctx_label=""
if [ -n "$ctx_size" ]; then
  ctx_label=$(format_k "$ctx_size")
  if [ -n "$ctx_used_pct" ] && [ "$ctx_used_pct" != "null" ]; then
    ctx_used_rounded=$(awk -v p="$ctx_used_pct" 'BEGIN { printf "%.0f", p }')
    ctx_label="ctx:${ctx_label} (${ctx_used_rounded}% used)"
  else
    ctx_label="ctx:${ctx_label}"
  fi
fi

# --- Session usage window (5-hour Claude.ai rate limit window) ------------
# rate_limits.five_hour is only present for subscribers after the first API
# response of the session, so this section is omitted otherwise.
session_used_pct=$(echo "$input" | jq -r '.rate_limits.five_hour.used_percentage // empty')
session_resets_at=$(echo "$input" | jq -r '.rate_limits.five_hour.resets_at // empty')

session_label=""
if [ -n "$session_used_pct" ] && [ "$session_used_pct" != "null" ]; then
  session_used_rounded=$(awk -v p="$session_used_pct" 'BEGIN { printf "%.0f", p }')
  session_label="5h:${session_used_rounded}%"
  if [ -n "$session_resets_at" ] && [ "$session_resets_at" != "null" ]; then
    # BSD date (macOS): %l is the space-padded (no leading zero) hour.
    session_reset_time=$(date -r "$session_resets_at" "+%l:%M %p" 2>/dev/null | sed 's/^ *//')
    [ -n "$session_reset_time" ] && session_label="${session_label} (resets ${session_reset_time})"
  fi
fi

# --- Colors (subtle; the status line is already rendered dimmed) ----------
DIM=$'\033[2m'
BLUE=$'\033[34m'
GREEN=$'\033[32m'
DARK_GREEN="${DIM}${GREEN}"
RED=$'\033[31m'
MAGENTA=$'\033[35m'
CYAN=$'\033[36m'
RESET=$'\033[0m'
SEP="${DIM} | ${RESET}"

parts=()
[ -n "$display_cwd" ] && parts+=("${BLUE}${display_cwd}${RESET}")
if [ -n "$git_branch" ]; then
  if [ -n "$git_diffstat" ]; then
    git_diffstat_colored="${DARK_GREEN}+${git_diffstat_added}${RESET}${DIM}/${RESET}${RED}-${git_diffstat_deleted}${RESET}"
    parts+=("${GREEN}${git_branch}${RESET}${DIM} ${RESET}${git_diffstat_colored}")
  else
    parts+=("${GREEN}${git_branch}${RESET}")
  fi
fi

model_segment=""
if [ -n "$model" ]; then
  model_segment="${MAGENTA}${model}"
  [ -n "$effort_label" ] && model_segment="${model_segment} (${effort_label})"
  model_segment="${model_segment}${RESET}"
fi
[ -n "$model_segment" ] && parts+=("$model_segment")

[ -n "$ctx_label" ] && parts+=("${CYAN}${ctx_label}${RESET}")
[ -n "$session_label" ] && parts+=("${DIM}${session_label}${RESET}")

out=""
for part in "${parts[@]}"; do
  if [ -z "$out" ]; then
    out="$part"
  else
    out="${out}${SEP}${part}"
  fi
done

printf '%s' "$out"
