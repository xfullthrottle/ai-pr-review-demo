# AI PR Review — CI demo

A minimal GitHub Actions pipeline with an AI step. On every pull request:

1. **`test` job:** runs `pytest` on a small claim-validation module. This is the hard gate.
2. **`ai-review` job:** runs only if tests pass. It sends the PR diff to Claude and posts (or updates) a review comment with findings tagged high/medium/low, suggested tests, and the **token count and cost of the review**.

```
PR opened/updated ──► test (pytest) ──pass──► ai-review (Claude) ──► PR comment
                         │ fail
                         └──► stop (no tokens spent)
```

## Design choices
| Choice | Why |
|---|---|
| AI review runs **after** tests and is **advisory** | Deterministic checks gate the merge; the LLM adds judgement, not authority |
| Diff wrapped in `<diff>` tags, "treat as data" | Basic prompt-injection guard: code comments can't steer the reviewer |
| Diff capped at 60k chars + `max_tokens` | Predictable cost per PR |
| Default model is Haiku; override with the `REVIEW_MODEL` repo variable | Model routing: cheap model for routine review, bigger model when it's worth it |
| Cost printed in every comment | Makes token spend visible per PR, so it can be measured |
| Skips cleanly with no API key | Fork PRs don't receive secrets; the build shouldn't fail for that |
| `--edit-last` comment | One comment per PR, updated on each push, not spam |
| `concurrency` cancel-in-progress | New push cancels the stale run: no wasted minutes or tokens |
| Least-privilege `permissions` | `contents: read`, `pull-requests: write` only |

## Setup
1. Create the repo on GitHub and push this folder.
2. Settings → Secrets and variables → Actions → **New repository secret** `ANTHROPIC_API_KEY`.
3. (Optional) Variables → `REVIEW_MODEL` = `claude-sonnet-5-5`.
4. Open a PR (see the demo below).

## Demo PR (for showing it live)
Create a branch that adds a bug, e.g. in `app/claims.py` change `amount <= 0` to `amount < 0`, and push it. Tests still pass, because no test covers amount = 0, so the AI review runs. It should flag the zero-amount edge case and suggest the missing test. That shows why both layers exist.

## Run locally
```bash
pip install -r requirements.txt
pytest -q
git diff main > pr.diff && python scripts/ai_review.py pr.diff review.md
```
