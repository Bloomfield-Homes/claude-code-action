import { runClaudeWithSdk } from "./run-claude-sdk";
import type { ClaudeRunResult } from "./run-claude-sdk";
import { parseSdkOptions } from "./parse-sdk-options";
import { moveMcpConfigToFile } from "./mcp-config-file";

export type ClaudeOptions = {
  claudeArgs?: string;
  model?: string;
  pathToClaudeCodeExecutable?: string;
  allowedTools?: string;
  disallowedTools?: string;
  maxTurns?: string;
  mcpConfig?: string;
  systemPrompt?: string;
  appendSystemPrompt?: string;
  fallbackModel?: string;
  showFullOutput?: string;
};

export async function runClaude(
  promptPath: string,
  options: ClaudeOptions,
): Promise<ClaudeRunResult> {
  const { parsed, cleanup } = moveMcpConfigToFile(parseSdkOptions(options));
  try {
    return await runClaudeWithSdk(promptPath, parsed);
  } finally {
    cleanup();
  }
}
