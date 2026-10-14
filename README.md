# LeetCode Daily AI

This project generates a LeetCode Daily Challenge solution for manual review. It runs in GitHub Actions at **09:00 Asia/Kolkata** (`03:30 UTC`) and saves successful runs under `solutions/YYYY-MM-DD/`. It never submits to LeetCode and never stores LeetCode credentials, cookies, or tokens.

## Source limitation

LeetCode does not provide a documented, unauthenticated public API for the daily challenge in this project. This repository therefore does **not** scrape LeetCode pages or call private/reverse-engineered endpoints. Configure one of these permitted inputs:

- `DAILY_PROBLEM_SOURCE_URL`: an HTTPS JSON endpoint that you control or are authorized to use, returning `title`, `url`, `statement`, and optional `examples`.
- `DAILY_PROBLEM_URL`: a manually selected public problem URL. This fallback records the URL, but the statement must be supplied by the provider or reviewer, so a JSON source is recommended.
- `DAILY_PROBLEM_JSON_PATH`: a local JSON file for local/manual runs.

Example JSON:

```json
{"title":"Two Sum","url":"https://leetcode.com/problems/two-sum/","statement":"...","examples":[{"input":"nums = [2,7,11,15], target = 9","output":"[0,1]"}]}
```

## Setup

1. Create a repository secret named `AI_API_KEY` containing the key for your chosen OpenAI-compatible provider.
2. Add repository variables under **Settings > Secrets and variables > Actions > Variables**:
	- `DAILY_PROBLEM_SOURCE_URL` (recommended) or `DAILY_PROBLEM_URL`
	- `AI_API_URL` (optional; defaults to OpenAI chat completions)
	- `AI_MODEL` (optional; defaults to `gpt-4o-mini`)
3. Merge this workflow into the default branch. Scheduled workflows run from the default branch.
4. Run it manually from the Actions tab with **Run workflow**. A manual `problem_url` input can override the repository variable.

For local development, use Python 3.12+, copy `.env.example`, export its values, and run:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
python -m daily_solver.main
```

## Output and validation

Each successful run writes `solution.md` and `metadata.json` to `solutions/YYYY-MM-DD/`. The solution includes the title, URL, explanation, complexity, implementation, and available example tests. Before writing, syntax is parsed and generated tests run in a temporary directory using an isolated Python interpreter with a sanitized environment, CPU, memory, file-descriptor, and wall-clock limits. Generated code is still untrusted: review it manually before submission.

The workflow commits only when `solutions/` changed, so rerunning the same date does not create duplicate commits. A failed generation or validation exits before any commit.

## Provider costs

AI usage is billed by the provider and varies by model, prompt length, and retry count. The default model is only a convenience; configure a cheaper model or a compatible self-hosted endpoint if appropriate. The workflow makes at most `MAX_RETRIES` retries (default `2`) after the initial request.

## Troubleshooting

- **No problem source configured:** set `DAILY_PROBLEM_SOURCE_URL`, `DAILY_PROBLEM_JSON_PATH`, or `DAILY_PROBLEM_URL`.
- **AI key error:** verify the exact secret name `AI_API_KEY`; secrets are never printed.
- **Provider response error:** check `AI_API_URL`, `AI_MODEL`, provider quota, and that the endpoint returns OpenAI-compatible `choices[0].message.content` JSON.
- **Validation failure:** inspect the Actions log. The generated artifact is not committed when tests fail.
- **No commit:** the dated output is unchanged, which is expected on a repeat run.

## Scope and safety

This tool prepares files for human review only. It does not log in to, submit to, or interact with LeetCode beyond URLs present in configured problem data. Keep API keys in GitHub Secrets and do not add them to `.env.example`, solution files, or commits.