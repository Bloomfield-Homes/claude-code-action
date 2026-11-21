// Display name and PR signature in tracking comments. Defaults match upstream.

export const AGENT_NAME = process.env.AGENT_DISPLAY_NAME || "Claude";

export const AGENT_SIGNATURE =
  process.env.AGENT_SIGNATURE ||
  "Generated with [Claude Code](https://claude.ai/code)";

export const SPINNER_URL =
  process.env.AGENT_SPINNER_URL ||
  "https://github.com/user-attachments/assets/5ac382c7-e004-429b-8e35-7feb3e8f9c6f";

export const SPINNER_SIZE = process.env.AGENT_SPINNER_SIZE || "14px";

export const WORKING_TEXT =
  AGENT_NAME === "Claude" ? "Claude Code is working" : `${AGENT_NAME} is working`;
