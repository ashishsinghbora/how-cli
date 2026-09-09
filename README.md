# how-cli
An AI-based CLI assistant to help you with command line & shell.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Demo 
https://github.com/user-attachments/assets/effefe1a-c0ed-4b60-838c-98f992f6c25f

## Features

- ⚡ **Deferred & Lazy LLM Initialization**: Zero heavy imports during `--help` or startup, preventing startup crashes.
- 🦙 **Local LLM Support (Ollama)**: Run 100% offline with Ollama models (`qwen2.5-coder`, `llama3.2`, etc.) with no API keys required.
- 🎯 **Intelligent Environment & Project Context**: Automatically detects your active shell, available package managers (`apt`, `brew`, `dnf`, `pacman`, etc.), and project root markers (`package.json`, `Cargo.toml`, `pyproject.toml`, `go.mod`, `Dockerfile`).
- 🛡️ **Safety Guardrails**: Heuristic pattern detection warns against destructive commands (`rm -rf`, `dd if=`, `mkfs`, `> /dev/sd`, `chmod -R 777`, `git reset --hard`, `git push --force`, fork bombs, curl-pipe-to-shell) and gates execution with an explicit confirmation phrase.
- 📋 **Interactive Action Menu & Clipboard**:
  - `[E]xecute`: Safely runs generated commands step-by-step, halting on non-zero exits.
  - `[C]opy`: Copies commands directly to your system clipboard via `pyperclip`.
  - `[M]odify`: Lets you edit commands inline before executing.
  - `[A]bort`: Cleanly exits with status 0.
- 🔧 **`how fix` Diagnostic Command**: Inspects the last failed shell command from history or stderr and diagnoses fixes.

---

## Installation

**1. Using `pip`**
```bash
pip install -U how-cli
```

**2. Manual Installation**
```bash
git clone https://github.com/FireHead90544/how-cli.git && cd how-cli
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

---

## Usage

```console
$ how [OPTIONS] COMMAND [ARGS]...
```

**Options**:
* `-v, --version`: Shows the version of the application.
* `--help`: Show help message and exit.

**Commands**:
* `setup`: Sets up the LLM provider, API key, custom model, or local endpoint.
* `to`: Sends a task description to the LLM and returns the commands.
* `fix`: Diagnoses the last failed command from shell history or stderr.

---

## `how setup`

Configure your preferred LLM provider. Supports both cloud providers (OpenAI, Anthropic, Google, Groq) and local models via Ollama.

**Interactive Mode**:
```bash
how setup
```

**Non-Interactive Mode**:
```bash
# Using local Ollama (no API key needed!)
how setup --no-interactive --provider Ollama --model qwen2.5-coder:latest --endpoint http://localhost:11434

# Using OpenAI
how setup --no-interactive --provider OpenAI --api-key "sk-..." --model gpt-4o

# Using Groq
how setup --no-interactive --provider GroqLLaMa --api-key "gsk_..."
```

---

## `how to`

Translates a natural language query into concrete shell commands tailored to your system and project.

```bash
how to "find all files larger than 100MB"
how to "install dependencies"
```

After commands are generated, the interactive action menu appears:
```text
Options: [E]xecute | [C]opy | [M]odify | [A]bort
Select an action [e/c/m/a/E/C/M/A] (a):
```

### Safety Guardrails
When a destructive command is detected (e.g. `rm -rf`, `git push --force`), `how` warns you with a prominent alert panel:
```text
╭─────────────────────────── SAFETY GUARDRAIL ALERT ───────────────────────────╮
│ WARNING: Destructive or High-Risk Command(s) Detected!                       │
│ • Recursive Force Delete: rm -rf node_modules                                │
│   Permanently deletes files and directories recursively without              │
│ confirmation.                                                                │
│                                                                              │
│ To prevent accidental damage, type the exact confirmation phrase:            │
│ I UNDERSTAND THE RISKS                                                       │
╰──────────────────────────────────────────────────────────────────────────────╯
```
Typing `y` is rejected; you must explicitly enter `I UNDERSTAND THE RISKS` before execution is permitted.

---

## `how fix`

Diagnoses why your last command failed and suggests the fix.

```bash
# Automatically read the last failed command from ~/.bash_history or ~/.zsh_history:
how fix

# Provide the command and stderr explicitly:
how fix -c "git push origin main" -e "error: failed to push some refs" -x 1
```

---

## Providers

| Provider | Default Model | Package | Requires Key | Tested |
|:--------:|:-------------:|:-------:|:------------:|:------:|
| **Ollama** (Local) | `qwen2.5-coder:latest` | `langchain-ollama` | ❌ No | ✅ |
| GoogleGenAI | `gemma-4-31b-it` | `langchain-google-genai` | ✅ Yes | ✅ |
| GoogleVertexAI | `gemma-4-31b-it` | `langchain-google-vertexai` | ✅ Yes | ❌ |
| GroqMistralAI | `mixtral-8x7b-32768` | `langchain-groq` | ✅ Yes | ✅ |
| GroqLLaMa | `qwen/qwen3.8-27b` | `langchain-groq` | ✅ Yes | ✅ |
| OpenAI | `gpt-4o` | `langchain-openai` | ✅ Yes | ✅ |
| Anthropic | `claude-3-5-sonnet-20240620` | `langchain-anthropic` | ✅ Yes | ✅ |

---

## Shell Integration

You can bind `how to` directly to a keyboard shortcut (e.g. `Ctrl+G`) in your shell to immediately convert your typed command buffer into an AI prompt:

### Zsh (`~/.zshrc`)
```bash
how-widget() {
  BUFFER="how to \"$BUFFER\""
  zle accept-line
}
zle -N how-widget
bindkey '^G' how-widget
```

### Bash (`~/.bashrc`)
```bash
how-widget() {
  local cmd="how to \"$READLINE_LINE\""
  READLINE_LINE=""
  eval "$cmd"
}
bind -x '"\C-g": how-widget'
```

---

## License
`how-cli` is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Honourable Mentions
This project is inspired by [kynnyhsap's](https://github.com/kynnyhsap) [how](https://github.com/kynnyhsap/how).

## Maintainers

- [@FireHead90544](https://github.com/FireHead90544) — Creator & Primary Maintainer
- [@ashishsinghbora](https://github.com/ashishsinghbora) — Contributor
