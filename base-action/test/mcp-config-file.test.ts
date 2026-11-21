#!/usr/bin/env bun

import { afterEach, describe, expect, test } from "bun:test";
import { existsSync, mkdtempSync, readFileSync, rmSync, statSync } from "fs";
import { tmpdir } from "os";
import { dirname, join } from "path";
import { moveMcpConfigToFile } from "../src/mcp-config-file";
import type { ParsedSdkOptions } from "../src/parse-sdk-options";

const parsed = (mcpConfig?: string): ParsedSdkOptions => ({
  sdkOptions: {
    model: "claude",
    extraArgs:
      mcpConfig === undefined
        ? {}
        : { "mcp-config": mcpConfig, model: "claude" },
  },
  showFullOutput: false,
  hasJsonSchema: false,
});

describe("moveMcpConfigToFile", () => {
  let base: string | undefined;
  afterEach(() => {
    if (base) rmSync(base, { recursive: true, force: true });
    base = undefined;
  });

  test("inline JSON moves to a private file and argv gets only its path", () => {
    base = mkdtempSync(join(tmpdir(), "mcp-test-"));
    const json =
      '{"mcpServers":{"github_comment":{"env":{"GITHUB_TOKEN":"ghs_example"}}}}';
    const { parsed: result, cleanup } = moveMcpConfigToFile(parsed(json), base);
    const path = result.sdkOptions.extraArgs?.["mcp-config"] as string;

    expect(path.startsWith(base)).toBe(true);
    expect(path).not.toContain("ghs_example");
    expect(readFileSync(path, "utf8")).toBe(json);
    expect(statSync(path).mode & 0o777).toBe(0o600);
    expect(statSync(dirname(path)).mode & 0o777).toBe(0o700);
    expect(result.sdkOptions.extraArgs?.model).toBe("claude");

    cleanup();
    expect(existsSync(dirname(path))).toBe(false);
  });

  test("a file path or a missing config is left as it is", () => {
    const withPath = parsed("/tmp/user-mcp.json");
    expect(moveMcpConfigToFile(withPath, "/nonexistent").parsed).toBe(withPath);
    const without = parsed();
    expect(moveMcpConfigToFile(without, "/nonexistent").parsed).toBe(without);
  });
});
