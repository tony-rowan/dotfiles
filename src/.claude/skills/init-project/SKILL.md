---
name: init-project
description: Scaffold a new project from scratch. Interactively gathers the project name, intent, requirements, stack, and all information needed to start building unassisted. Creates a directory with git init, REQUIREMENTS.md, README.md, and CLAUDE.md. Use when the user wants to start a new project, initialize a project skeleton, or capture project requirements before writing any code.
---

# Init Project

Scaffold a new project by gathering requirements interactively, then writing the foundational files
that allow construction to begin without further clarification.

## Default Technology Stack

Unless the user requests otherwise or the project requirements make this stack clearly inappropriate,
the following stack is used without asking the user about it. This decision is invisible to the user
unless a deviation is needed.

**Default stack:**
- Language/runtime: Ruby (MRI)
- Framework: Rails 8
- Frontend: Hotwire (Turbo + Stimulus), TailwindCSS, Importmaps
- Database: SQLite in development, test, and production
- Testing: RSpec + Capybara
- Components: ViewComponent

**Why this stack (include verbatim in REQUIREMENTS.md when used):**
- Ruby is exceptionally readable, which makes it an excellent choice for LLM-assisted development — the code is easy to reason about at a glance.
- Rails is highly opinionated and takes a strong convention-over-configuration stance, which dramatically reduces the number of architectural decisions that need to be made and makes it an excellent choice for LLM-assisted development.
- Hotwire (Turbo + Stimulus) with Importmaps enables modern, interactive UIs without a JavaScript build pipeline. This means no Node.js, no webpack, no bundler — the app deploys without additional build steps.
- TailwindCSS via the importmap-compatible CDN build requires no Node toolchain, keeping the deployment footprint minimal.
- SQLite runs reliably in production on single-instance deployments, eliminating the need for a separate database server process. This is the smallest possible path to production.
- ViewComponent is more performant than ERB partials and its use encourages consistent, reusable UI components across the product.
- RSpec and Capybara allow the application to be tested at both the unit level and through full browser-driven integration tests. Both levels of testing are necessary for high coverage and deployment confidence.

**Node.js is actively discouraged** across all projects due to the frequency and severity of supply-chain security vulnerabilities in the npm ecosystem.

### When to deviate from the default stack

Deviate **only** when:
1. The user explicitly requests a different stack, **or**
2. The project requirements make this stack clearly unsuitable (e.g. a documentation site built from plain Markdown files — a static site generator like Bridgetown is more appropriate; a data-science or ML pipeline).

Deviations should be rare. A web application with a database, user accounts, and a UI is almost always well served by the default stack.

### If deviation is user-requested

Ask the user to justify each choice that differs from the default. The justification must describe
a concrete technical or functional reason — something about what the technology does or enables.

**Rejected justifications** (do not accept these; ask the user to try again):
- "It's what I know" / "I'm familiar with it"
- "It's the most popular" / "everyone uses it"
- "It's the default" / "it comes with X"
- "It's the best"
- "I like it" / "I prefer it"
- "It's easier"

**Accepted justifications** (examples of the bar to meet):
- "We need real-time bidirectional communication; Action Cable adds complexity we want to avoid, so we'll use Go for the WebSocket service."
- "The output is a purely static site built from Markdown; a Rails app adds unnecessary runtime overhead."
- "The client's existing infrastructure is Python-only and we cannot introduce another runtime."

Once a justification is accepted, record it faithfully in the REQUIREMENTS.md stack section.

### If deviation is requirement-driven

Determine the appropriate stack yourself based on the requirements. Explain to the user why the
default stack was not appropriate and what you have chosen instead. You do not need their approval
on the stack choice, but you must explain the reasoning clearly and give them the chance to redirect.

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
output files completely and accurately. Focus entirely on what the user wants to build, who will
use it, and why — **not** on how it will be built. Stack and technology choices are handled
separately and should not be raised with the user unless a deviation is needed.

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

**Deployment & environment** _(ask only if relevant — skip for purely local tools)_
- Where will this run — local only, a single server, a cloud platform?
- Is there an existing hosting environment or infrastructure constraint?

### What NOT to ask about in Phase 2

Do not ask the user about programming languages, frameworks, databases, testing tools, build
systems, or any other technical implementation detail unless:
- They have already raised it themselves, or
- A deviation from the default stack is clearly required and you need their input to resolve it.

Users of this skill may have little or no technical expertise. Their time in Phase 2 is best spent
on what the product does and who it serves.

### Handling gaps and conflicts

- If the user's answers contain a conflict (e.g. two incompatible feature requirements), flag it
  explicitly and ask for a decision before continuing.
- If the user has made an assumption that may not hold, surface it as a risk and get confirmation.
- If a question is not yet relevant for this type of project, skip it — but note any area you
  skipped and why, so the user can bring it up later.

### Ambiguity and assumption policy

This phase must produce zero ambiguities and zero assumptions in the output files. Apply these
rules strictly throughout the conversation:

- **Never assume.** If a decision has not been stated by the user, it is not made.
- **Name every assumption you catch yourself about to make.** If you find yourself thinking
  "they probably mean X", stop and ask instead.
- **Surface all conflicts before moving on.**
- **Distinguish must-haves from maybes.** If the user uses uncertain language ("might", "maybe",
  "we could"), ask whether it is a requirement or a future consideration.
- **Pin down vague terms.** Words like "fast", "simple", "modern", "scalable", or "standard"
  mean different things in different contexts. Ask what the user means concretely.
- **Do not carry forward unresolved items.** If a decision is deferred, record it as a TODO with
  the exact information needed to resolve it.

### Readiness check

After each batch of answers, assess whether you can write every section of every output file with
no placeholder, no assumption, and no ambiguity remaining. If any gap exists, ask targeted
follow-up questions before continuing. Do not move to Phase 3 with unresolved items.

When you believe you are ready, present the user with a concise summary of everything captured —
key decisions, requirements, and any outstanding TODOs — and ask for explicit confirmation before
proceeding.

## Phase 3 — Determine the stack

After Phase 2 is complete and confirmed, determine which stack to use. This step is not
conversational unless a deviation is required.

1. **Check for explicit deviation requests.** If the user raised any technology preferences during
   Phase 2, note them now. If they require deviation, follow the deviation process described in the
   Default Technology Stack section above.

2. **Check for requirement-driven deviation.** Review the confirmed requirements. If the default
   stack is clearly unsuitable (see examples above), determine the appropriate stack and briefly
   explain the choice to the user before proceeding.

3. **Otherwise, use the default stack silently.** Do not mention it; simply use it when writing
   the output files.

## Phase 4 — Write the output files

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
- Include a **Technology Stack** section (see template) written as one or two short paragraphs —
  no sub-headings, no bullet lists. Cover development, test, and production inline. Follow with a
  brief explanation of why the stack was chosen. For the default stack, use the rationale from the
  Default Technology Stack section above. For deviated choices, use the justification the user
  provided or your own reasoning if requirement-driven. Keep it concise — this section carries no
  more weight than Motivation or Guiding Principles.
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

## Phase 5 — Handoff

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

- Do not create the directory or any files until Phase 4.
- Do not leave template placeholders in the output files. Every section must contain real content
  or be omitted entirely if not applicable.
- Do not invent requirements, stack choices, or constraints. If something is unknown, ask.
- Do not create a `docs/` directory or any files beyond the three listed above.
- Do not run `git add` or `git commit` until the user explicitly confirms they are ready.
- If the user wants to skip a question or defer a decision, note it as a TODO in the relevant
  file section and explain what information is needed to resolve it.
- Do not raise the topic of technology stack with the user unless a deviation from the default
  is being considered or the user raises it themselves.
