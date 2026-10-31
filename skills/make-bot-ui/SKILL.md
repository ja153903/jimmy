---
name: make-bot-ui
description: >-
  Use when building a custom UI (page, dashboard, buttons) that should wake a
  bot over a webhook, when the user must provide a webhook sender key, or
  when exposing that UI on a private network.
disable-model-invocation: true
---

Read [efficiency](../../docs/efficiency.md) once per workflow context for task-wide budgets and available capabilities.

# Make a bot UI

Build a page whose actions reach a bot through a server-side webhook. First identify the user's actual automation service, supported webhook API, authentication scheme, and hosting requirements. Use its available connector or documented API. If the service or endpoint is missing, prepare the local UI and ask for the missing configuration; do not invent a routine-creation tool.

Treat incoming JSON as untrusted data. Define the fields the UI sends and the permitted actions the bot takes. Create or modify an external routine only within the user's authorization. Obtain its actual webhook URL from the service.

Keep credentials on the server in the project's existing secret configuration or a supported secure input mechanism. Do not expose them in client code, chat, logs, or skill files. If no secure input is available, tell the user how to configure the server locally without sharing the secret.

Have the browser call a local application endpoint; the application validates the request and calls the bot webhook using the service's documented authentication. Apply a bounded timeout and avoid retries unless the action is idempotent. Use the requested network exposure and authentication; a private-network deployment may need a non-loopback bind.

Verify a representative action and inspect its actual result, including error handling and absence of credentials in client output. Report the working URL, required configuration, and any untested external integration.
