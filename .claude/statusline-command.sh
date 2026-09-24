#!/bin/bash

# Read input from stdin
input=$(cat)

# Get values from JSON input
cwd=$(echo "$input" | jq -r '.workspace.current_dir')
model=$(echo "$input" | jq -r '.model.display_name')
effort=$(echo "$input" | jq -r '.effort.level // empty')
tokens_used=$(echo "$input" | jq -r '.context_window.total_input_tokens // 0')
tokens_total=$(echo "$input" | jq -r '.context_window.context_window_size // 0')
tokens_pct=$(echo "$input" | jq -r '.context_window.used_percentage // 0')

# Get git branch if in a git repo
git_info=""
branch=$(git -C "$cwd" -c core.useBuiltinFSMonitor=false -c core.fsmonitor=false symbolic-ref --short HEAD 2>/dev/null \
         || git -C "$cwd" -c core.useBuiltinFSMonitor=false -c core.fsmonitor=false rev-parse --short HEAD 2>/dev/null)
if [ -n "$branch" ]; then
    dirty=""
    if [ -n "$(git -C "$cwd" -c core.useBuiltinFSMonitor=false -c core.fsmonitor=false status --porcelain 2>/dev/null)" ]; then
        dirty=" *"
    fi
    git_info=" ($branch$dirty)"
fi

# Show only the folder name
short_cwd=$(basename "$cwd")

# Format token counts: e.g. 44200 -> "44.2k", 1000000 -> "1m"
tokens_used_fmt=$(awk "BEGIN { n=$tokens_used/1000; if(n>=100) printf \"%dk\",int(n); else printf \"%.1fk\",n }")
tokens_total_fmt=$(awk "BEGIN { n=$tokens_total; if(n>=1000000) printf \"%dm\",int(n/1000000); else printf \"%dk\",int(n/1000) }")
token_info="${tokens_used_fmt}/${tokens_total_fmt} tokens (${tokens_pct}%)"

# Build title string: path | tokens | model | effort
title="$short_cwd$git_info | $token_info | $model"
[ -n "$effort" ] && title="$title | $effort"

# Emit OSC 2 sequence to set the terminal window title.
# Claude Code passes this through to the terminal unchanged.
printf '\033]2;%s\007' "$title"

# Output to stdout so Claude Code's status bar also shows the path.
echo "$title"
