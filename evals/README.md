# Evals

Evaluation cases for each skill, kept here rather than inside `skills/<name>/` so they are never copied into an install.

- `<skill>/evals.json` — behavior cases in the skill-creator format (`prompt`, `expected_output`, `expectations`). Each expectation is a statement a grader can check against the transcript and the files produced.
- `<skill>/trigger-queries.json` — requests that should and should not load the skill, including near-misses between the two skills (a dictionary for one extract belongs to `data-liberation`; governance and deposits belong to `data-project`).

## Running them

Every run is a real model call, so evals run on demand, not in CI.

1. **Behavior cases.** With the skill-creator skill, ask it to run `evals/<skill>/evals.json` against `skills/<skill>/`, with the skill and without it (or against the previous release's zip when comparing versions). Grade each expectation with evidence from the transcript and the output files, and drop any expectation that passes in both arms, because it isn't measuring the skill.
2. **Trigger queries.** Install both skills, send each query in a fresh session, and record which skill (if any) loaded. A query in `should_not_trigger` that loads the skill, or one in `should_trigger` that loads the other skill, points at the description in that skill's frontmatter.
3. **Record the result** in the PR that changed the skill: which cases ran, on which model, and what changed.

Run the cases that touch the sections you changed before every release, and the whole set before a minor or major version.
