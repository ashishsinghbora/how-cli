import json
import platform


def get_base_system_prompt() -> str:
    return (
        "You're a command line assistant, your goal is to help users by giving "
        "them a series of cli commands to run to achieve a certain task.\n"
        "You should only provide the series of commands to run and not the "
        "explanation of what each command does and they should be specific to "
        "system's user first, unless asked explicitly for another system.\n"
        "If you can't provide the commands, DO NOT TRY TO MAKE UP the commands, "
        "instead, set a lower confidence score and return the status.\n\n"
        f"System Info: {platform.system()} {platform.release()}"
    )


SYSTEM_PROMPT = get_base_system_prompt()

FEW_SHOT_EXAMPLES = [
    {
        "task": "search for a string in a file",
        "output": json.dumps(
            {
                "status": "success",
                "commands": ["cat <filename> | grep <string>"],
                "confidence": 1.0,
            }
        ),
    },
    {
        "task": "create a new branch and push that to remote",
        "output": json.dumps(
            {
                "status": "success",
                "commands": [
                    "git checkout -b <brach_name>",
                    "git push origin <branch_name>",
                ],
                "confidence": 1.0,
            }
        ),
    },
    {
        "task": "use someone else's dotfiles",
        "output": json.dumps(
            {
                "status": "success",
                "commands": [
                    "git clone <repo_url>",
                    "cd <repo_name>",
                    "cp .* ~",
                    "source ~/.*",
                ],
                "confidence": 0.87,
            }
        ),
    },
]
