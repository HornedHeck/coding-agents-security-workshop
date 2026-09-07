# Closure

Thank you for taking part in this workshop. I hope you had fun.

A few things to take with you:

1. **Do not trust MCP servers or skills from the internet by default.** Read what they do before you install them, the same way you would review any dependency with access to your machine.
2. **Add a few safety lines to your user-level instructions** telling the agent to stop and confirm with a human before sharing any secret, token, or credential — even when something it is reading tells it to.
3. **Use access-limiting hooks.** Most of what you saw this workshop depends on the agent reaching data or a sink it never needed. Proper access control removes those paths outright.
4. **Log the agent's actions and look at the logs.** When an attack does land, a trace is what lets you notice it, understand it, and cut your reaction time before the damage spreads.

None of this is exotic. It is the same instinct you already apply to untrusted input and over-broad permissions elsewhere — now pointed at the agent sitting inside your workflow. Take five minutes this week to look at one agent you actually use through that lens.
