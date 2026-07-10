---
name: development-pipeline
description: Run the design → implementation → review → ship pipeline for a piece of work, using named subagents Sam (implementer) and Oscar (reviewer). Stack-agnostic — reads the current repo's `.claude/pipeline.md` for testing methodology, verify commands, ticket tooling, and PR flow. Use when the user asks to run "the pipeline" or "development-pipeline" for a feature, bug fix, or refactor.
---

# Development Pipeline

Four phases: design and implementation plan (you, interactively), implementation loop (Sam,
sequential), review (Oscar), then triage/verify/commit/PR (you, directly). Phases 1 and 2 run inside
one `Workflow` call; phases 0 and 3 are always your own direct work — never delegate them.

This command is shared across repos. Everything stack-specific — testing methodology, verify/build
commands, the tool used to fetch tickets, and the PR flow — lives in this repo's own
`.claude/pipeline.md`, not in this file. Read that file before Phase 0 begins; if it's missing, stop
and tell the user this repo has no `.claude/pipeline.md` yet rather than guessing at conventions.

## Phase 0 — Design & implementation plan (you, interactively — do not delegate)

Interview the user relentlessly about every aspect of the design until you reach a shared
understanding — walk down each branch of the design tree, resolving dependencies between decisions
one by one, rather than dumping every open question at once. Don't re-ask what this conversation
already established — reuse existing context (files already read, decisions already made, a ticket
already mentioned) rather than re-deriving it from scratch.

Draw a hard line between facts and decisions. If something can be settled by reading the codebase,
the ticket, or existing docs, go look it up yourself — don't outsource that legwork to the user. But
the actual decisions, anything with more than one reasonable answer, are the user's to make: put each
one to them explicitly and wait for their answer, even where you have a clear recommendation. Don't
let a plausible-sounding default stand in for a decision they never actually made.

1. Read `.claude/pipeline.md` in full. It defines this repo's stack, testing methodology (whether to
   apply strict red-green-refactor everywhere, or judge each step for a real testable seam), verify
   commands, ticket tool, and PR flow — everything below refers back to it.
2. Establish the work item.
   - Check whether a ticket is already evident from the conversation or the current branch name (e.g.
     a `TECH-1234`-style token in the branch, or a ticket referenced earlier in this session).
   - If none is evident, ask the user directly: is this tied to a ticket, or is it explicitly
     ticket-less work (generic refactor, tooling, chore)? Do not proceed until you have an explicit
     answer one way or the other — do not assume "no ticket" just because none was mentioned.
   - If a ticket is given, fetch it in full using the ticket tool named in `.claude/pipeline.md` and
     read the description, acceptance criteria, and any linked technical detail before continuing.
3. Explore the codebase context relevant to the request: the nearest existing implementation pattern,
   the nearest existing test pattern, related components/features for this stack, and any conventions
   in this repo's `AGENTS.md`/`CLAUDE.md`/`.claude/rules/` and `.claude/pipeline.md` that bear on this
   change.
4. Ask clarifying questions one at a time, multiple-choice where possible — never bundle several open
   decisions into one message; asking multiple things at once is bewildering to answer. For each
   question, give your recommended answer, then wait for the user's actual response before moving to
   the next one. Keep asking until every open design decision is resolved — err on the side of one
   more question rather than assuming.
5. When more than one reasonable approach exists, propose them with trade-offs and a recommendation.
6. Present a design summary and an ordered implementation plan: a numbered list of individual steps,
   each narrow enough to implement and verify in one pass, in the order they should be implemented.
   Apply `.claude/pipeline.md`'s testing methodology per step: where it calls for red-green-refactor,
   plan that cycle explicitly; where a step has no real testable seam, say so in the plan and note
   it'll be verified per the repo's non-test verification approach instead.
7. Get explicit approval of both the design and the implementation plan before proceeding. Do not
   start Phase 1 on an assumed yes. A tool timeout (e.g. `AskUserQuestion` returning no response) is
   not consent — pause and wait for the user to actually respond; never fall back to "best judgment"
   at this gate.

## Phase 1 & 2 — Implementation loop + review (one `Workflow` call)

Once the implementation plan is approved, call the `Workflow` tool with a script along these lines
(adapt prompts/shape to the actual work, but keep the structure: a strictly sequential implementation
loop using `sam-the-implementer` at `effort: 'medium'`, followed by one `oscar-the-reviewer` call at
`effort: 'high'`):

```js
export const meta = {
  name: 'development-pipeline-run',
  description: 'Sequential implementation loop followed by a diff-scoped review',
  phases: [{ title: 'Implement' }, { title: 'Review' }],
}

// The harness delivers `args` as a raw JSON string in this environment, not a parsed
// object, even when the Workflow tool call passes a real JSON object — confirmed by a
// minimal repro where `args` arrived as `"{\"foo\": \"bar\"}"` (a string). Always parse
// defensively so the script works whether or not that's fixed upstream.
const input = typeof args === 'string' ? JSON.parse(args) : args

let priorSummary = ''
const implementationLog = []

for (const item of input.implementationPlan) {
  const report = await agent(
    `Design summary:\n${input.designSummary}\n\n` +
    `Ticket: ${input.ticket ?? 'none — explicitly ticket-less work'}\n\n` +
    `Prior steps implemented so far:\n${priorSummary || '(none yet)'}\n\n` +
    `Implement this plan item now, and only this one: ${item.description}`,
    { agentType: 'sam-the-implementer', effort: 'medium', phase: 'Implement', label: `implement:${item.id}` }
  )
  implementationLog.push({ item, report })
  priorSummary += `\n- ${item.description}: ${report}`
}

const reviewFindings = await agent(
  `Design summary:\n${input.designSummary}\n\n` +
  `Review the full diff for this branch's new work (git diff against the base branch). ` +
  `Implementation log for context:\n${priorSummary}`,
  { agentType: 'oscar-the-reviewer', effort: 'high', phase: 'Review', label: 'review' }
)

return { implementationLog, reviewFindings }
```

Pass `args` as `{ designSummary, ticket, implementationPlan: [{ id, description }, ...] }` built from
the approved Phase 0 output. Do not fan the implementation loop out with `pipeline`/`parallel` — each
step edits the same files and depends on the previous step's code, so it must run strictly one at a
time. Sam and Oscar each read `.claude/pipeline.md` themselves as part of their own job — you don't
need to inline stack specifics into their prompts here.

### Showing live progress as a todo list

The `Workflow` call above runs in the background and only notifies you when the whole thing finishes
— `/workflows` shows its live progress, but that's a separate view the user has to switch to. Mirror
that progress into the visible todo list as well, right after launching the workflow:

1. Immediately after the `Workflow` call returns (it returns right away with a task ID and a
   `journal.jsonl` path under the printed transcript dir), call `TaskCreate` once per
   `implementationPlan` item (same order, same wording as the plan) plus one final task for the
   review, e.g. `"9. Review (Oscar)"`. Note the task IDs the harness assigns — they'll match the
   plan order 1:1 if the todo list was empty before this. `TaskCreate`/`TaskUpdate`/`Monitor` are
   deferred tools — `ToolSearch` for `select:TaskCreate,TaskUpdate,Monitor` first if their schemas
   aren't already loaded. `TaskCreate` takes `subject`/`description`, not `prompt`.
2. Journal lines don't carry the step's label, only `{type: "started"|"result", key, agentId}` — but
   because the implementation loop is strictly sequential (never `pipeline`/`parallel`), the *N*th
   `started` line and the *N*th `result` line always correspond to the *N*th `agent()` call in the
   script, i.e. plan item *N* (and the final one, N = number of plan items + 1, is the review). Count
   positionally — don't try to match on `key`.
3. Start a `Monitor` with a poll loop reading that journal path, counting `started`/`result` lines and
   emitting one line per new occurrence (`STARTED k` / `RESULT k`), exiting once results reach
   `implementationPlan.length + 1`:

   ```bash
   journal="<path from the Workflow tool result>"
   last_started=0
   last_result=0
   target=<implementationPlan.length + 1>
   while [ "$last_result" -lt "$target" ]; do
     sleep 3
     [ -f "$journal" ] || continue
     started=$(grep -c '"type":"started"' "$journal" 2>/dev/null || echo 0)
     result=$(grep -c '"type":"result"' "$journal" 2>/dev/null || echo 0)
     while [ "$last_started" -lt "$started" ]; do
       last_started=$((last_started+1))
       echo "STARTED $last_started"
     done
     while [ "$last_result" -lt "$result" ]; do
       last_result=$((last_result+1))
       echo "RESULT $last_result"
     done
   done
   echo "ALL_DONE"
   ```

   If the workflow was launched partway through already (journal has existing lines), seed
   `last_started`/`last_result` from the current counts instead of 0 so you don't replay old steps.
4. On each `STARTED k` notification, `TaskUpdate` task *k* to `in_progress`. On each `RESULT k`,
   `TaskUpdate` task *k* to `completed`. Don't block or poll for these — they arrive as Monitor
   notifications; keep the conversation going in between.
5. When the workflow's own completion notification arrives, proceed to Phase 3 as normal — the todo
   list is a visual aid, not a substitute for reading `implementationLog`/`reviewFindings` from the
   actual workflow result.

## Phase 3 — Triage, verify, commit, PR (you, directly — outside the workflow)

- Read Oscar's findings. Apply clear no-brainer fixes yourself. Surface any genuine judgment calls to
  the user before acting on them.
- Independently re-verify yourself — do not rely solely on Sam's or Oscar's self-reported results. Run
  the verify commands from `.claude/pipeline.md` (targeted tests plus the full relevant suite/lint/
  static analysis), and for any step with no testable seam, actually build and check the change
  manually per `.claude/pipeline.md`'s non-test verification approach — not just a disclosed
  limitation.
- Review the complete diff end-to-end before committing; strip anything not required by the approved
  implementation plan.
- Commit and push.
- Use the `pull-request` skill to open or update the PR, per `.claude/pipeline.md`'s PR flow section.
  Reference the ticket in the title if one exists; if Phase 0 established this is ticket-less work,
  say so plainly and omit a ticket reference rather than inventing one.

## Guardrails

- Never skip Phase 0's ticket question — either a ticket is named, or the user has explicitly
  confirmed there isn't one.
- Never let Sam implement more than one implementation-plan item per agent call.
- Oscar must never execute code, run throwaway scripts, or otherwise probe behaviour empirically to
  verify a claim — that's enforced in his agent definition. If a finding from Oscar reads like it was
  reasoned from running something rather than reading it, disregard that reasoning and re-review the
  point yourself.
- Don't proceed to Phase 1 without explicit design + implementation-plan approval. A timed-out or
  unanswered question is not approval — wait for a real answer.
- Don't skip Phase 3's independent re-verification, whether that's re-running tests or manually
  checking the change — whichever `.claude/pipeline.md` calls for.
- Never invent stack specifics that belong in `.claude/pipeline.md` — if it's missing or silent on
  something you need (a verify command, the PR flow), ask the user rather than guessing.
