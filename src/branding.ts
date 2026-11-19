// Display name and PR signature in tracking comments. Defaults match upstream.

export const AGENT_NAME = process.env.AGENT_DISPLAY_NAME || "Claude";

export const AGENT_SIGNATURE =
  process.env.AGENT_SIGNATURE ||
  "Generated with [Claude Code](https://claude.ai/code)";

export const WORKING_TEXT =
  AGENT_NAME === "Claude" ? "Claude Code is working" : `${AGENT_NAME} is working`;
