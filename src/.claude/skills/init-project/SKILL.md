---
name: init-project
description: Scaffold a new project from scratch. Interactively gathers the project name, intent, requirements, stack, and all information needed to start building unassisted. Creates a directory with git init, REQUIREMENTS.md, README.md, and CLAUDE.md. Use when the user wants to start a new project, initialize a project skeleton, or capture project requirements before writing any code.
---

# Init Project

Scaffold a new project by gathering requirements interactively, then writing the foundational files
that allow construction to begin without further clarification.

## Phase 1 — Establish the project name

If the user invoked the skill with a project name argument, use it as the working title. If no
name was given, ask for one before continuing.

Once you have a name, derive the `kebab-case` directory name. Then apply this rule:

**If the derivation is unambiguous** — the name is already a single clean word or a phrase that
maps trivially to kebab-case with no surprising transformations (e.g. "my cool app" → `my-cool-app`,
"TaskTracker" → `task-tracker`) — state what you're going to use and move straight to Phase 2.
Example: _"Starting **My Cool App** in `./my-cool-app`."_

**Only ask if there's a real question** — the name contains characters, abbreviations, numbers, or
casing that could reasonably be read more than one way (e.g. "GPT2Wrapper", "my.app", "v2 api"),
or the user might expect a different directory name than the obvious derivation. In that case, show
the display name and the derived directory name side-by-side and confirm before continuing.

If the user wants a different directory name, accept it — but it must still be `kebab-case`.

## Phase 2 — Requirements discovery

This phase is the core of the skill. Its goal is to gather enough information to write all three
output files completely and accurately, without assumptions. Be thorough but purposeful — every
question should unlock something concrete in the output files.

Work through the areas below. You do not need to ask about every area in a single message; instead
ask in focused, conversational batches. Adapt the order and depth to what the user has already
told you.

### Areas to cover

**Project intent & motivation**
- What is this project? What problem does it solve, or what opportunity does it address?
- Who are the primary users or audience?
- What is the guiding motivation — what would make this a success?
- Are there anti-goals or things explicitly out of scope?

**Requirements**
- What are the must-have features or behaviours for a first working version?
- What are the nice-to-haves or future-phase items?
- Are there known constraints — performance, compliance, accessibility, scale, budget, timeline?
- Are there integrations with external systems, APIs, or data sources?

**Stack & technology choices**
- What language(s) and runtime(s) will be used? If undecided, suggest options and ask the user
  to choose — do not assume.
- What frameworks, libraries, or platforms are intended or preferred?
- What is the target environment — local CLI, web browser, mobile, server, embedded, etc.?
- Is there a preferred database or data-persistence approach?
- What is the deployment target — local only, cloud, self-hosted, etc.?

**Development & tooling**
- What package manager, build tool, or task runner should be used?
- Are there specific linting, formatting, or code-style requirements?
- Is there a preferred testing framework or approach?
- Will there be CI/CD? If so, on what platform?

**Project structure**
- Are there conventions for how the source tree should be laid out?
- Are there specific configuration files that should exist from day one (e.g. `.env.example`,
  `docker-compose.yml`, `.editorconfig`)?

### Handling gaps and conflicts

- If the user's answers contain a conflict (e.g. two incompatible framework choices), flag it
  explicitly and ask for a decision before continuing.
- If the user has made an assumption that may not hold (e.g. choosing a framework that doesn't
  support the target environment), surface this as a risk and get confirmation.
- If a question is not yet relevant for this type of project, skip it — but note any area you
  skipped and why, so the user can bring it up later.

### Ambiguity and assumption policy

This phase must produce zero ambiguities and zero assumptions in the output files. Apply these
rules strictly throughout the conversation:

- **Never assume.** If a decision has not been stated by the user, it is not made. Do not infer
  a stack choice, requirement, or constraint from context clues — ask.
- **Name every assumption you catch yourself about to make.** If you find yourself thinking
  "they probably mean X" or "this type of project usually uses Y", stop and ask instead.
- **Surface all conflicts before moving on.** If two answers are incompatible, do not silently
  favour one. State the conflict clearly, explain why it matters, and ask the user to resolve it.
- **Distinguish must-haves from maybes.** If the user describes something in uncertain language
  ("might", "maybe", "we could"), ask whether it is a requirement or a future consideration.
- **Pin down vague terms.** Words like "fast", "simple", "modern", "scalable", or "standard"
  mean different things in different contexts. Ask what the user means concretely.
- **Do not carry forward unresolved items.** If a question is deferred ("we'll decide later"),
  record it explicitly as a TODO with the exact information needed to resolve it — do not treat
  the deferral as an implicit answer.

### Readiness check

After each batch of answers, assess whether you can write every section of every output file with
no placeholder, no assumption, and no ambiguity remaining. If any gap exists, ask targeted
follow-up questions before continuing. Do not move to Phase 3 with unresolved items.

When you believe you are ready, present the user with a concise summary of everything captured —
key decisions, requirements, stack choices, and any outstanding TODOs — and ask for explicit
confirmation before proceeding. If the user spots anything missing or wrong at this point, resolve
it before writing any files.

## Phase 3 — Write the output files

Create the project directory and initialise git, then write all three files. Use the templates in
the `templates/` directory alongside this skill file as a structural guide — they define the
sections each file should contain, not the exact wording.

### Directory and git

```
mkdir <kebab-case-name>
cd <kebab-case-name>
git init
```

### REQUIREMENTS.md

- Open with a short introduction: what the project is, why it exists, and what would make it a
  success.
- Follow with the guiding motivations and any principles that should govern trade-off decisions.
- List requirements in detail, grouped logically (e.g. by feature area, by user role, or by
  must-have vs. future phase). Use numbered lists within groups so requirements are referenceable.
- This file is the most important output — it must be complete and unambiguous.

### README.md

- Title and a short description of the project.
- A section describing the stack and key technology choices.
- Prerequisites needed to run the project locally.
- Getting started instructions (clone, install dependencies, run).
- Development workflow instructions relevant to this stack.
- Testing instructions.
- Deployment section if applicable; omit or mark as TODO if not yet determined.
- Omit sections that are genuinely not applicable to this project type.

### CLAUDE.md

- Open with the project name, a short description, and the intended audience.
- Project overview: what the agent needs to know to operate in this codebase.
- Stack summary: languages, frameworks, key libraries, environment.
- A skeleton repository structure (can be minimal at this stage).
- Setup instructions an agent would run from a clean checkout.
- Development and testing/debugging guidance.
- Agent guidance: conventions, important constraints, things to watch out for.
- An extended documentation section with commented-out examples showing how to link to `docs/`
  files as the project grows. Do not create `docs/` yet.

## Phase 4 — Handoff

After writing the files, close out warmly. You've just helped someone start something new — the
tone should reflect that. Be brief, be genuine, and leave them feeling set up for success.

Cover these points naturally, not as a numbered list:

- Where the project lives (the absolute path).
- A brief note on each file — what it contains and why it matters at this stage.
- Any TODOs left in the files, and what information would close them out.
- What to do next: take a moment to read through `REQUIREMENTS.md`. It's the foundation
  everything else will be built on, so it's worth making sure it feels right. They can edit it
  directly, or keep talking to refine anything that has shifted. When they're happy with it,
  just say the word and Claude will make the first commit. Then it's time to start building.

Wait for the user to confirm before making the first commit.

## Guardrails

- Do not create the directory or any files until Phase 3.
- Do not leave template placeholders in the output files. Every section must contain real content
  or be omitted entirely if not applicable.
- Do not invent requirements, stack choices, or constraints. If something is unknown, ask.
- Do not create a `docs/` directory or any files beyond the three listed above.
- Do not run `git add` or `git commit` until the user explicitly confirms they are ready.
- If the user wants to skip a question or defer a decision, note it as a TODO in the relevant
  file section and explain what information is needed to resolve it.
