# TechScope Daily Scrapers

TechScope directory:

`<USER: SET THE FULL PATH TO THE TECHSCOPE DIRECTORY HERE>`

Use this directory as the working directory for all commands below.

## Workflow status checks

Do **not** continuously, periodically, or proactively check the workflow status during the session.

Check the workflow status only in these situations:

* When a **new session is started**.
* When the user explicitly asks about the status of the workflows, scrapers, or daily runs.
* When the user explicitly asks to run workflow `l` or `i`.

When performing a status check, read:

`<TechScope directory>/data-pipeline/scrapers/execution.json`

Use this file to determine whether workflows `l` and `i` have already run today.

Do not modify `execution.json`. The scripts update it automatically.


### Daily status rules

For each workflow:

* `status: "success"` and `last_run` is today → consider the workflow already completed for today. Do not suggest running it.
* `status: "error"` → notify the user that the previous run failed and suggest a retry.
* `last_run` is not today or does not exist → suggest running the workflow.
* If `last_run` is today but its recorded time is relevant to the user's request, take the time into account rather than treating the entire day as equivalent.

A status check by itself must **not** start any workflow unless the user explicitly asks to run it.

If a workflow has not run today, inform the user and ask whether they want to run it. Do not automatically start it.

## Workflow `l`

When the user asks to run workflow `l`, execute these steps in this exact order:

1. `python data-pipeline/scrapers/linkedin.py`
2. `start_chrome_debug.bat` located in `<TechScope directory>/start_chrome_debug.bat`
3. `python data-pipeline/scrapers/indeed_keywords.py`

Wait for each process to finish before starting the next one.

Never run steps in parallel.

If any step fails, stop the workflow immediately and notify the user. Do not continue with subsequent steps.

## Workflow `i`

When the user asks to run workflow `i`, execute these steps in this exact order:

1. Check whether Chrome Debug is already running.
2. If Chrome Debug is not running, execute `start_chrome_debug.bat` and wait for it to finish.
3. Execute `python data-pipeline/scrapers/indeed.py` and wait for it to finish.
4. Execute `python data-pipeline/scrapers/indeed_keywords.py` and wait for it to finish.

Never run steps in parallel.

If any step fails, stop the workflow immediately and notify the user. Do not continue with subsequent steps.

## After a workflow finishes

After workflow `l` or `i` finishes, re-read:

`<TechScope directory>/data-pipeline/scrapers/execution.json`

Report the final status to the user.

Do not edit `execution.json` manually.

## Explicit execution requests

If the user explicitly asks to run workflow `l` or `i`, execute it regardless of whether it has already run today.

Do not skip an explicitly requested workflow because `execution.json` says it already ran.

## Session behaviour

The agent must **not** repeatedly check `execution.json` throughout an active session.

After the initial session check has been performed, do not check the workflow status again unless:

* the user asks about the workflows or their status;
* the user asks to run `l` or `i`; or
* the agent needs to perform the post-run verification after executing a workflow.
