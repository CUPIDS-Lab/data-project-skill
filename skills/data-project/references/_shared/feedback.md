<!-- Vendored from shared/references/feedback.md by tools/vendor.py. Edit shared/references/feedback.md, not this copy. -->

# Filing sprint feedback on these skills

Every sprint that used `data-liberation` or `data-project` should end by telling the skills what happened. Feedback goes to one place, the **sprint-feedback** issue form on [`CUPIDS-Lab/data-skills`](https://github.com/CUPIDS-Lab/data-skills/issues/new?template=sprint-feedback.yml), and is filed against the Outline's section numbers, so each lesson lands on the section, and the file, that owns it.

## When

At the end of each sprint, after a deposit or release, or whenever the skill's guidance was wrong, unclear or missing badly enough that you worked around it. A local fix you made in a project is the most valuable thing to report: it is evidence of what the skill should have said.

## How

1. **Run an after-action review** of the sprint: what was supposed to happen, what actually happened, why there was a gap, what to change and what to keep. Use the evidence (commits, PRs, issues, error logs) rather than memory.
2. **Find the section.** Map each gap to one or more Outline sections (1 Scope & gate … 10 Maintain & feedback). If the problem was finding your way at all, choose "The Outline or onboarding itself."
3. **Name the cause** if you can: *missing* (never addressed), *ambiguous* (mentioned but vague), *contradictory* (two pieces of guidance disagree), *buried* (correct but found too late), or *novel* (nothing could have anticipated it).
4. **File one issue per distinct gap** with the form. Describe the outcome you were attempting, the "done when" test that failed or was unclear, what happened (facts first), what you did instead, and the files or commands involved.
5. **Strip sensitive material first.** Private projects report process lessons only: no data values, no names, no record details, no screenshots of data. Say "private project" in the project field.

## What happens next

Maintainers label each issue by skill, section and cause, and fix accepted findings in the file the Outline says owns that section. A one-off ("novel") usually changes nothing, to avoid rules that help one project and burden every other. Release notes list the issues closed per section, so the project that filed a finding can see where it went.
