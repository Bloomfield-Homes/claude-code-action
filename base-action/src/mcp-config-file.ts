import { mkdtempSync, writeFileSync } from "fs";
import { tmpdir } from "os";
import { join } from "path";
import type { ParsedSdkOptions } from "./parse-sdk-options";

/**
 * Inline MCP JSON carries GitHub tokens in its server env blocks, and a process's argv is readable by every
 * user through /proc. Moves inline JSON into a 0600 file in a 0700 directory and passes its path instead,
 * so a check that runs as another user on the runner cannot read the tokens. A path is left as it is.
 */
export function moveMcpConfigToFile(
  parsed: ParsedSdkOptions,
  baseDir: string = process.env.RUNNER_TEMP || tmpdir(),
): ParsedSdkOptions {
  const extraArgs = parsed.sdkOptions.extraArgs;
  const config = extraArgs?.["mcp-config"];
  if (
    !extraArgs ||
    typeof config !== "string" ||
    !config.trim().startsWith("{")
  ) {
    return parsed;
  }
  const dir = mkdtempSync(join(baseDir, "claude-mcp-"));
  const path = join(dir, "mcp-config.json");
  writeFileSync(path, config, { mode: 0o600 });
  return {
    ...parsed,
    sdkOptions: {
      ...parsed.sdkOptions,
      extraArgs: { ...extraArgs, "mcp-config": path },
    },
  };
}
