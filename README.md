# LeetCode Daily AI

This project prepares one or two LeetCode solutions every day for manual review. It runs in GitHub Actions at **09:00 Asia/Kolkata** (`03:30 UTC`) and saves successful runs under `solutions/YYYY-MM-DD/<problem-slug>/`.

It uses a cost-saving hybrid strategy:

1. It selects reviewed solutions from `catalog/problems.json`. These use no AI and no API cost.
2. If the catalog has fewer entries than `DAILY_PROBLEM_COUNT`, it uses the configured AI provider only for the missing entries.

Add reviewed entries to the catalog to eliminate AI usage entirely. Set `DAILY_PROBLEM_COUNT` to `1` or `2`.
Before each run, add the URLs of problems you have already solved to `catalog/completed.json`.
Those entries are excluded from catalog selection. The workflow cannot inspect your LeetCode
account, because it never receives account credentials or session data.

## Source limitation

LeetCode does not provide a documented, unauthenticated public API for the daily challenge in this project. This repository therefore does **not** scrape LeetCode pages or call private/reverse-engineered endpoints. Configure one of these permitted inputs:

- `DAILY_PROBLEM_SOURCE_URL`: an HTTPS JSON endpoint that you control or are authorized to use, returning `title`, `url`, `statement`, and optional `examples`.
- `DAILY_PROBLEM_URL`: a manually selected public problem URL. This fallback records the URL, but the statement must be supplied by the provider or reviewer, so a JSON source is recommended.
- `DAILY_PROBLEM_JSON_PATH`: a local JSON file for local/manual runs.

Example JSON:

```json
{"title":"Two Sum","url":"https://leetcode.com/problems/two-sum/","statement":"...","examples":[{"input":"nums = [2,7,11,15], target = 9","output":"[0,1]"}]}
```

## GitHub Actions setup

1. Merge this workflow into the default branch. Scheduled workflows run from the default branch.
2. Add an Actions variable `DAILY_PROBLEM_COUNT` with value `1` or `2` (default `2`).
3. If the catalog is sufficient, no secret is needed. For AI fallback, add a repository secret
   named `AI_API_KEY` containing a newly generated provider key, and these variables:
   - `DAILY_PROBLEM_SOURCE_URL` (recommended) or `DAILY_PROBLEM_URL`
   - `AI_API_URL` (optional; defaults to OpenAI chat completions)
   - `AI_MODEL` (optional; defaults to `gpt-4o-mini`)
4. Run **Actions > LeetCode Daily Solver > Run workflow** once to verify setup. A manual `problem_url` input can override `DAILY_PROBLEM_URL` for an AI fallback.

Never paste an API key into source files, issues, pull requests, or chat. The key included in the
request that led to this change is exposed and must be revoked immediately in the provider
dashboard. Create a replacement key and save it only as the GitHub Actions `AI_API_KEY` secret.

For local development, use Python 3.12+, copy `.env.example`, export its values, and run:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
python -m daily_solver.main
```

## Output and validation

Each successful run writes `solution.md` and `metadata.json` to `solutions/YYYY-MM-DD/<problem-slug>/`. The solution includes the title, URL, explanation, complexity, implementation, and available example tests. Before writing, syntax is parsed and tests run in a temporary directory using an isolated Python interpreter with resource limits. Review generated code before submission.

The workflow commits only when `solutions/` changed, so rerunning the same date does not create duplicate commits. A failed generation or validation exits before any commit.

## LeetCode login and submission

This workflow intentionally does **not** log in to LeetCode or submit code. LeetCode does not provide a documented public submission API, and putting account passwords, session cookies, or browser tokens in GitHub Secrets would be unsafe. The generated files are committed for review.

To submit safely:

1. Open [leetcode.com](https://leetcode.com/) in your browser and sign in normally (email/password, Google, or GitHub).
2. Open the problem URL from the generated `solution.md`.
3. Copy the implementation into LeetCode's editor, select the matching language, and click **Run**.
4. Review the result and click **Submit** yourself.

## Provider costs

AI usage is billed only for catalog shortfalls and varies by provider, prompt length, and retry count. The workflow makes at most `MAX_RETRIES` retries (default `2`) after the initial request.

## Troubleshooting

- **Catalog shortfall:** add reviewed entries to `catalog/problems.json`, or configure AI fallback and a problem source.
- **Already solved problems are selected:** add their normalized LeetCode URLs to `catalog/completed.json`, one URL per list item.
- **No problem source configured:** set `DAILY_PROBLEM_SOURCE_URL`, `DAILY_PROBLEM_JSON_PATH`, or `DAILY_PROBLEM_URL` when AI fallback is enabled.
- **AI key error:** verify the exact secret name `AI_API_KEY`; secrets are never printed.
- **Provider response error:** check `AI_API_URL`, `AI_MODEL`, provider quota, and that the endpoint returns OpenAI-compatible `choices[0].message.content` JSON.
- **Validation failure:** inspect the Actions log. The generated artifact is not committed when tests fail.
- **No commit:** the dated output is unchanged, which is expected on a repeat run.

## Scope and safety

This tool prepares files for human review only. It does not log in to, submit to, or interact with LeetCode beyond URLs present in configured problem data. Keep API keys in GitHub Secrets and do not add them to `.env.example`, solution files, or commits.