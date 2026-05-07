---
name: implement-jira-ticket
description: Implement a Jira ticket end to end from a Jira issue key or Jira URL. Use when the task is to fetch a specific Jira ticket through the Jira MCP server, understand the requested behaviour and technical clues in the ticket, make the corresponding code changes, run the most relevant verification, commit the work, and open a GitHub pull request.
---

# Implement Jira Ticket

Follow this workflow when the user asks to work on a Jira ticket such as `TECH-1010` or a full Jira
issue URL such as `https://chargy.atlassian.net/browse/TECH-816`.

## Workflow

1. Normalize the ticket reference.
- Accept either a Jira URL or an issue key.
- If a URL is provided, extract the issue key and the Jira site hostname from it.
- Use the Jira MCP server to identify the correct `cloudId`. Prefer the site hostname
  when it is enough; otherwise use accessible-resource lookup.

2. Fetch the ticket before doing any other work.
- Use the Jira MCP server to fetch the issue details directly.
- Load the description and any other immediately relevant issue fields needed to
  understand the request.
- If the ticket has a status of "Done" or some other terminal state, state this clearly and stop.
  Don't work on finished tickets.
- If the ticket has an assignee that doesn't match the currently authenticated user, state
  this clearly and stop. Don't work on tickets that are already being worked on by someone else.
- If the ticket cannot be fetched for any reason, state that clearly with the exact failure you
  observed and stop. Do not inspect the codebase, edit files, commit, or open a pull request
  after a fetch failure.
  - Inform the user how to install and activate the Jira MCP server:

```sh
$ codex mcp add jira https://mcp.atlassian.com/v1/mcp
$ codex mcp login jira
```

3. Derive implementation hints from the ticket text.
- Read the summary, description, acceptance criteria, comments if needed, and any linked
  technical details that are necessary to execute the work.
- Treat fenced code blocks, inline code, file paths, constants, SQL, JSON keys, `snake_case`,
  `CamelCase`, and namespaced identifiers as strong hints for where to look in the codebase.
- Use those hints to search for the nearest implementation and test patterns before
  editing anything.
- Distinguish requirements from assumptions.
- If the ticket is too vague to establish a reasonable change, inform the user and stop. Do not
  make up requirements or assumptions. Report the error clearly to the user.

4. Implement the change.
- Follow repository instructions already in effect, especially local agent guidance,
  testing expectations, and commit/PR conventions.
- Mirror the nearest existing code and spec style.
- Make the smallest change that satisfies the ticket.
- Update or add the narrowest relevant spec when behaviour changes.

5. Verify the work.
- Run the most relevant targeted checks for the files or behaviour you changed.
- Prefer the smallest useful spec or command over broad test runs.
- If verification cannot be completed, report what blocked it and include that in the final handoff.

6. Commit the change.
- Review the diff and avoid including unrelated workspace changes.
- Commit only the files relevant to the ticket.
- Use a concise imperative commit message on a new branch with a relevant name.

7. Open a pull request.
- Prefer the GitHub MCP server when it is available and usable.
- If GitHub MCP is unavailable, use the `gh` CLI.
- Do not use raw network requests for GitHub operations.
- When using `gh pr create`, always pass `--repo char-gy/chargy-server --draft`; the CLI resolves the wrong repo without `--repo`, and PRs must be drafts by default.
- Use the repository's PR title and body conventions.
- Reference the Jira ticket in the PR title so the relationship is explicit.
  - e.g. [TECH-8080] Fix a rendering bug in the account area
- If PR creation fails, report the failure clearly instead of claiming success.

## Guardrails

- Do not proceed past ticket fetch if the ticket is done or assigned to someone else.
- Do not proceed past ticket fetch if Jira access fails.
- Do not broaden scope beyond what the ticket and local patterns support.
- Do not ignore technical clues embedded in code-looking text inside the ticket.
- Do not skip verification, commit creation, or PR creation unless a failure blocks the step.

## Required Completion Output

Provide:

1. The normalized ticket reference you used.
2. A concise summary of the requested change and the ticket clues that guided file discovery.
3. The files changed and the verification you ran.
4. The commit SHA and commit message.
5. The pull request URL, or the exact reason PR creation did not complete.
