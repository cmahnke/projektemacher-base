/*
 * Type declarations for the WebMCP API (https://webmachinelearning.github.io/webmcp/,
 * W3C Web Machine Learning CG draft). Used by 'assets/ts/webmcp-search.ts'. Remove
 * these declarations once lib.dom ships the API.
 */

declare global {
  interface ModelContext extends EventTarget {
    registerTool(
      tool: ModelContextTool,
      options?: ModelContextRegisterToolOptions,
    ): Promise<undefined>;
  }

  interface ModelContextTool {
    name: string;
    title?: string;
    description: string;
    inputSchema?: object;
    annotations?: ToolAnnotations;
    execute(inputObject: object, options: ToolExecuteCallbackOptions): Promise<unknown>;
  }

  interface ToolAnnotations {
    readOnlyHint?: boolean;
    untrustedContentHint?: boolean;
    consequentialHint?: boolean;
    debugging?: boolean;
  }

  interface ToolExecuteCallbackOptions {
    signal: AbortSignal;
  }

  interface ModelContextRegisterToolOptions {
    exposedTo?: string[];
    signal?: AbortSignal;
  }

  interface Document {
    readonly modelContext: ModelContext | undefined;
  }
}

export {};
