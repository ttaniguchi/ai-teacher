---
name: claim-context-review
description: Use when the user provides a URL, article, interview, speech, podcast transcript, social post, or quoted excerpt and asks to summarize, interpret, fact-check, contextualize, or collect reactions to a named person's or organization's claim.
---

# Claim Context Review

## Overview

Turn a URL or excerpt about a public claim into a context-preserving summary. The goal is not to make the claim look good or bad; it is to recover what the speaker actually meant, identify likely distortions, and map credible supportive and critical reactions.

Use this skill especially when an article or social post may be used as rhetorical ammunition, when a public figure's words are being clipped for effect, or when the user asks for both the claim and the surrounding internet reaction.

## Core Rules

- Treat the linked article as evidence, not as the final truth.
- Prefer primary sources for the claim: full interview, talk video, transcript, original paper, official blog, court filing, release note, mailing-list post, or the claimant's own post.
- Separate four layers: what was said, what the author says it means, what online amplifiers claim it means, and what can be independently supported.
- Do not flatten nuance into "pro vs con" if the real split is about scope, evidence quality, incentives, or implementation details.
- Avoid repeating noisy framings as fact. Label them as interpretations, reactions, or rhetorical uses.
- For fast-moving public discourse, browse and use dated sources. Mention exact dates when recency matters.
- If the user asks to save the result as an HTML note, combine this skill with the repository's note-writing skill and follow that repository's article workflow.
- Do not include private information, credentials, private URLs, unpublished business information, or local-environment-specific details in repository files.

## Workflow

### 1. Capture The Claim

Read the user-provided URL or excerpt first. Identify:

- Claimant: who is being summarized or quoted.
- Venue: interview, keynote, podcast, article, social post, paper, mailing list, etc.
- Date of claim and date of article.
- Central claim in one sentence.
- Supporting subclaims.
- Conditions, caveats, uncertainty, or jokes that change the meaning.
- What the article headline emphasizes versus what the body supports.

If direct access fails, search for the title, URL slug, quoted text, or named event. Say when the article was inaccessible and explain what alternate source was used.

### 2. Find Primary Context

Look for the highest-context source available:

- Full video or official event page.
- Transcript or original interview.
- Original publication by the claimant.
- Official documentation or mailing-list thread.
- Dataset, paper, benchmark, or legal filing being discussed.

Use primary context to correct or qualify the article's framing. If no primary source is available, state that limitation and avoid overconfident reconstruction.

### 3. Build The Claim Map

Structure the interpretation as:

- **Actually said:** concrete claims supported by the article or primary source.
- **Likely intended meaning:** cautious synthesis from context.
- **Not said / overread:** claims that online discussion may imply but the source does not support.
- **Practical implication:** what a reasonable reader should take away.
- **Open uncertainty:** missing context, ambiguous wording, or areas where evidence is weak.

This section is the antidote to quote-mining. Keep it precise and boring in the best way.

### 4. Collect Third-Party Reactions

Search for reactions across multiple source types when available:

- Reputable tech or domain media.
- Expert blogs, newsletters, or public posts by relevant practitioners.
- Forums such as Hacker News, Reddit, GitHub issues, mailing lists, Stack Exchange, or Lobsters.
- Social platforms only when needed; treat virality as a signal of attention, not reliability.
- Research or benchmark reports that bear on empirical claims.

For each reaction source, record:

- Position: supportive, critical, mixed, or meta-commentary.
- Argument: the actual reason, not just sentiment.
- Evidence: whether it cites data, direct experience, primary sources, or only vibes.
- Bias/incentive: vendor, ideological, community norm, professional role, or platform dynamics if relevant.

### 5. Filter Noise

Downweight reactions that:

- Quote only a headline or short clip.
- Attack the person instead of the claim.
- Treat a caveated claim as absolute.
- Use the claim only to validate an unrelated prior belief.
- Are duplicate rewrites of the same article.
- Confuse descriptive claims, such as "this is happening", with normative claims, such as "this should happen".
- Lack any evidence beyond engagement metrics.

Do not hide noisy reactions if they are influential. Summarize them as noise patterns, not as balanced evidence.

### 6. Write The Output

For a direct answer, use this shape:

1. Short answer: what the claim really is.
2. Context: who said it, where, and when.
3. Claim map: actually said / likely meant / not supported.
4. Supportive reactions: 2-5 themes with source examples.
5. Critical reactions: 2-5 themes with source examples.
6. Noise check: common distortions or quote-mined readings.
7. Bottom line: the fairest interpretation.
8. Sources: links used, with primary sources first.

For an HTML note, preserve the same analytical sections but adapt to the target repository's article structure. Include a concise Q&A near the top and reference links at the bottom.

## Quality Bar

Before finalizing, check:

- Did you verify the primary context when it reasonably exists?
- Did you distinguish the speaker's claim from the article author's framing?
- Did you include both support and criticism without pretending all reactions are equally credible?
- Did you identify quote-mining risks explicitly?
- Did you avoid private, sensitive, or non-public information?
- Did you cite sources used, especially primary sources?
- Did you state uncertainty instead of filling gaps with speculation?

## Response Tone

Write in the user's language unless they request otherwise. Be firm about misreadings but avoid scolding. The useful voice is: "Here is the clean read, here is what people are doing with it, and here is what the evidence actually supports."
