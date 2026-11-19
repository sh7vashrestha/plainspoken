# Plainspoken: clear, natural writing for AI assistants

An agent skill for Claude Code, Devin, Codex, Cursor and any tool that reads `SKILL.md` files or plain instruction files.

The skill tells the model to write the way a careful person explains something to a friend. It starts with substance: every sentence has to carry a fact, an example, a reason or a decision. Then it removes the words and sentence shapes that make text sound machine-made, such as `delve`, `leverage`, `not only X but also Y`, piles of em dashes, question headings and closing summaries. It cleans out leftovers from templates and chat tools, such as `[Your Name]`, `As an AI language model`, citation tokens and hidden characters. It also asks the model to check every number against a source, to keep the writer's own voice, and to change as little as possible when editing someone else's text.

## An example

Before:

> Our cutting-edge platform empowers teams to seamlessly collaborate, unlocking unprecedented productivity in today's fast-paced digital landscape.

After:

> Teams use the app to share files and comment on them in one place. Most teams set it up in under an hour.

More examples are in `skills/plainspoken/references/examples.md`.

## What is in this repo

`skills/plainspoken/SKILL.md` holds the main rules: how to work, substance, words, sentences, voice, layout, facts, editing, cleaning out leftovers, final checks and how to reply.

`skills/plainspoken/references/formats.md` has short notes for emails, cover letters, essays, reports, social posts, slides and documentation.

`skills/plainspoken/references/examples.md` has before and after rewrites.

`skills/plainspoken/references/academic.md` has extra rules for research papers.

`skills/plainspoken/scripts/check.py` lists lines worth a second look. It needs Python 3 and nothing else.

`.claude-plugin/` holds the two small files that let Claude Code install the skill from this repo.

`tests/` holds the tests for the checker. They also confirm that every "After" example in this repo passes the checker and every "Before" example fails it.

## Install

### Claude Code

Install it straight from GitHub. In your terminal:

```bash
claude plugin marketplace add sh7vashrestha/plainspoken
claude plugin install plainspoken@plainspoken
```

Or inside a Claude Code session:

```
/plugin marketplace add sh7vashrestha/plainspoken
/plugin install plainspoken@plainspoken
```

Claude then uses the skill on its own when you ask for writing or editing. You can also call it by name with `/plainspoken:plainspoken`. To get later changes, run `claude plugin update plainspoken@plainspoken`.

If you prefer plain files, copy the skill folder into your personal skills folder:

```bash
git clone https://github.com/sh7vashrestha/plainspoken.git
mkdir -p ~/.claude/skills
cp -r plainspoken/skills/plainspoken ~/.claude/skills/
```

To use it in one project only, copy it to `.claude/skills/` inside that project.

### Devin

Upload `skills/plainspoken/SKILL.md` as a skill in your Devin plugins, or commit the folder to a repo under `.devin/skills/plainspoken/`.

### Codex, Cursor and other tools

Copy `skills/plainspoken/` into your project (for example `.agents/skills/plainspoken/`) and point to it from `AGENTS.md`, or paste the body of `SKILL.md` into your rules file.

### Chat apps

Paste the body of `SKILL.md` (everything after the second `---` line) into custom instructions or the start of a chat.

## Use the checker

```bash
python3 skills/plainspoken/scripts/check.py draft.md
```

It prints the file, the line, the rule and the matched words for each hit, and exits with code 1 if it finds any:

```
draft.md:3: inflated verb: "leverage" (use a plain verb)
draft.md:7: question lead-in: "The result?" (make it a statement)
```

Treat each hit as a question. Some are fine in context, such as a technical term or a quotation. A single em dash is allowed, and the checker lists lines with several and files with many. It skips code blocks, inline code and YAML front matter. It finds stock phrases only, so text can pass it and still say nothing.

## Run the tests

```bash
python3 -m unittest discover -s tests
```

## A note on AI detectors

This skill aims at writing people find clear and pleasant to read. It does not promise to beat any AI detection tool, and it should not be used to pass off work as your own where that breaks the rules of a school, journal or employer.

## Contributing

Pull requests are welcome. Good additions are new patterns that clearly read as machine-made, with a plain replacement and a real before and after example. Add a test case for any new checker rule.

## Author

Shiva Shrestha ([@sh7vashrestha](https://github.com/sh7vashrestha)).

## License

MIT. See `LICENSE`.
