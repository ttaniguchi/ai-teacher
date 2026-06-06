---
name: qa-html-note
description: Create or update Japanese Q&A-style HTML knowledge notes in this repository. Use when the user message starts with "質問" or asks to record a technical question as an HTML article.
---

# Q&A HTML Note

## Overview

Turn Japanese technical questions into static HTML notes in this repository. Preserve the established pattern: articles in `articles/`, a generated root `index.html`, shared CSS, optional diagrams in `images/`, and article pages that begin with concise Q&A before systematic explanation.

## Repository Target

- Treat the current repository root as the target site root unless the user explicitly says otherwise.
- If invoked from a different working directory, switch context to the repository root before reading or editing.
- Keep content in Japanese unless the user requests another language.
- Prefer static HTML/CSS/SVG. Do not add a build system unless the user explicitly asks.
- This is a public repository. Do not write personal information, credentials, private URLs, unpublished business information, or local-environment-specific details into articles, comments, commits, or generated files.

## Decision Flow

1. Inspect existing files first:
   - `index.html`
   - `docs/homepage.md`
   - `scripts/sync-article-dates.py`
   - `styles/site.css`
   - relevant files in `articles/`
   - `images/`
2. If the user asks a new question or a group of questions, create one HTML page per distinct question.
3. If the question is about an existing HTML page, update that page by adding, correcting, or appending sections instead of creating a duplicate.
4. If a new page is created, add it to `ARTICLE_CLUSTER` in `scripts/sync-article-dates.py`.
5. Run `scripts/sync-article-dates.py` so `index.html` and article creation dates stay synchronized.
6. If diagrams help, create SVG files in `images/` and reference them with relative paths.

## Page Structure

For a new article page, use this order:

1. Standard HTML document with `lang="ja"` and viewport meta.
2. Link to the shared stylesheet using the correct relative path.
3. Site header with links back to the index and related pages.
4. Hero:
   - topic eyebrow
   - question-based `h1`
   - one-paragraph lead
5. A `section.qa` near the top:
   - heading `簡潔なQ&A`
   - `dl` with the user's question and concise answer
   - include multiple Q&As when the page covers subquestions
6. Optional `figure.figure` with an image from `images/`.
7. Systematic explanation with clear `h2` and `h3` sections.
8. A `.note` section headed `要点`.
9. A `.related` section headed `参考資料` with first-party sources only, such as official docs, specifications, standards, original papers, vendor announcements, or public repositories.
10. `.related` navigation back to the index and adjacent relevant pages.
11. Site footer.

## Writing Standard

- Start with the answer, then explain the structure.
- Keep the first Q&A short enough to scan.
- Use accurate but approachable technical Japanese.
- Prefer concrete mental models and implementation implications over vague definitions.
- Mention limitations, trade-offs, and common misunderstandings when useful.
- Avoid overclaiming about fast-changing technologies; when current facts matter, verify with an appropriate primary source before writing.
- Keep headings reusable and consistent: `簡潔なQ&A`, `要点`, and topic-specific `h2` sections.
- First-party sources are mandatory for every article update or creation. Include at least one verifiable primary source URL relevant to the key claims.
- If reliable first-party sources are not available, explicitly state uncertainty and avoid asserting the claim as fact.

## Directory And Naming

- Put article HTML in `articles/` at the site root. Do not create topic subdirectories; categorize only in `index.html`.
- Follow `docs/homepage.md` for home layout, recent cards, category rows, sort order, and add/update workflow.
- Prefer regenerating `index.html` with `scripts/sync-article-dates.py` over hand-editing.
- After adding a page, register it in `scripts/sync-article-dates.py` (`ARTICLE_CLUSTER`) and run the script so article dates and index entries are synchronized.
- Use lowercase hyphenated filenames, such as `mcp-server.html` or `rag.html`.
- Put all diagrams and article images in root `images/`.
- Put shared styles in `styles/site.css`.
- Use relative links that work from static hosting.

## Updating Existing HTML

When the user asks a question about an existing page:

- Identify the likely page by title, filename, topic, or index entry.
- Add a new Q&A entry to the existing `section.qa` if it clarifies the same topic.
- Add a new explanatory section if the answer needs more than a short correction.
- Add a small `補足` or `よくある誤解` section when the page is mostly complete.
- Update the index summary only if the page's scope changed.
- Do not rewrite unrelated sections for style only.

## Visuals

- Use SVG diagrams for conceptual flows unless the user requests raster images.
- Keep diagrams readable on mobile: large labels, simple arrows, no dense text.
- Add meaningful `alt` text and `figcaption`.
- Do not create decorative-only images.

## Verification

After edits:

- Check created files with `rg --files`.
- Check links and image paths with `rg "href=|src="`.
- Run `scripts/sync-article-dates.py` after adding or changing article metadata.
- For substantial frontend changes, open the site in a local browser or run a temporary local server and verify titles, images, and no obvious horizontal overflow.
- Stop any temporary server before finishing unless the user asked to keep it running.

## Git And Publishing

- Do not commit or push unless the user explicitly asks.
- When the user asks to commit or publish, review `git status --short` first and stage only the files changed for the note.
- Use concise, public-safe commit messages, such as `Add useActionState note` or `Update MCP server note`.
- Do not push unrelated user changes.
- If asked for a published URL, derive it from the repository's public hosting configuration or existing `index.html` links instead of embedding a local user-specific URL in this skill.

## Example Trigger

User:

```text
質問
MCPはなぜサーバーを立ち上げる必要があるのか？
```

Response behavior: create or update an HTML article in `articles/`, update `ARTICLE_CLUSTER`, regenerate `index.html`, include a concise Q&A at the top, verify paths, and return the local article path.
