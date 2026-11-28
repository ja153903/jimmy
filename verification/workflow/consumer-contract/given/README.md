# Evaluation startup

Operators run npm run load to load src/suite.json through bin/run.mjs and src/loader.mjs. The CLI prints the cases that will be sent to the evaluator. A JSON-only smoke check does not run that path.

The unified loader reads shared judge: "rubric". A case cannot define judge itself. Per-case judging text belongs in injectedContents.criteria. Omitting it uses the generic default "Be useful", which loses these case-specific requirements.

Preserve both case IDs, prompts, and criteria:
- short: prompt "Summarize the plan", criterion "At most two sentences"
- accessible: prompt "Describe the chart", criterion "Describe labels and trends without color alone"

The loader and CLI are existing consumers, not part of this repair. Preserve src/loader.mjs and bin/run.mjs unchanged.
