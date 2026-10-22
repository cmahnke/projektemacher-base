interface PagefindSearchApi {
  search(
    query: string,
    options?: { filters?: Record<string, string[]> },
  ): Promise<{
    results: PagefindSearchFragment[];
    unfilteredResultCount: number;
  }>;
}

interface PagefindSearchFragment {
  data(): Promise<PagefindSearchResultData>;
}

interface PagefindSearchResultData {
  url: string;
  meta?: Record<string, string>;
  excerpt: string;
}

interface SearchToolInput {
  query: string;
  filters?: Record<string, string[]>;
  limit?: number;
}

interface SearchToolResult {
  url: string;
  title: string;
  excerpt: string;
  meta?: Record<string, string>;
}

const DEFAULT_BUNDLE_PATH = "/index/";
const DEFAULT_RESULT_LIMIT = 10;
const MAX_RESULT_LIMIT = 25;

let pagefindApi: Promise<PagefindSearchApi> | undefined;

function loadPagefind(bundlePath: string): Promise<PagefindSearchApi> {
  if (pagefindApi === undefined) {
    const bundleUrl = bundlePath + "pagefind.js";
    pagefindApi = import(bundleUrl) as Promise<PagefindSearchApi>;
  }
  return pagefindApi;
}

function sanitizeFilters(filters: Record<string, string[]>): Record<string, string[]> {
  const sanitized: Record<string, string[]> = {};
  for (const [name, values] of Object.entries(filters)) {
    if (Array.isArray(values)) {
      const valid = values.filter((value): value is string => typeof value === "string");
      if (valid.length > 0) {
        sanitized[name] = valid;
      }
    }
  }
  return sanitized;
}

function executeSearch(
  bundlePath: string,
): (inputObject: object, options: ToolExecuteCallbackOptions) => Promise<unknown> {
  return async (inputObject, options) => {
    const request = inputObject as SearchToolInput;
    if (typeof request.query !== "string") {
      return { error: "query must be a string" };
    }
    const query = request.query;
    const filters = request.filters === undefined ? {} : sanitizeFilters(request.filters);
    const rawLimit = typeof request.limit === "number" ? Math.floor(request.limit) : DEFAULT_RESULT_LIMIT;
    const limit = Math.min(Math.max(rawLimit, 1), MAX_RESULT_LIMIT);
    let api: PagefindSearchApi;
    try {
      api = await loadPagefind(bundlePath);
    } catch {
      return { error: "search index is not available" };
    }
    const response = await api.search(query, Object.keys(filters).length > 0 ? { filters } : undefined);
    if (options.signal.aborted) {
      return { query, cancelled: true };
    }
    const results: SearchToolResult[] = [];
    for (const fragment of response.results.slice(0, limit)) {
      const data = await fragment.data();
      results.push({
        url: data.url,
        title: data.meta?.title ?? "",
        meta: data.meta,
        excerpt: data.excerpt,
      });
    }
    return {
      query,
      resultCount: response.results.length,
      unfilteredResultCount: response.unfilteredResultCount,
      results,
    };
  };
}

window.addEventListener("DOMContentLoaded", () => {
  const modelContext = document.modelContext;
  if (modelContext === undefined || typeof modelContext.registerTool !== "function") {
    return;
  }
  const bundlePath =
    document.querySelector(".search-box-container")?.getAttribute("data-bundle-path") ??
    document.querySelector<HTMLMetaElement>('meta[name="webmcp-search-bundle-path"]')?.content ??
    DEFAULT_BUNDLE_PATH;
  const title =
    document.querySelector<HTMLMetaElement>('meta[name="webmcp-search-title"]')?.content || "Search";
  modelContext
    .registerTool({
      name: "search",
      title: title,
      description:
        "Search this website (full-text search over the site's Pagefind index). Returns matching pages with url, title, meta and a highlighted excerpt. Use filters to scope the search by indexed filter values (e.g. section, tag, type; pass string arrays per filter name) and limit (default 10, maximum 25) to cap the number of returned results.",
      inputSchema: {
        type: "object",
        properties: {
          query: { type: "string", description: "Full-text search query" },
          filters: {
            type: "object",
            description: "Optional filter values per indexed filter, e.g. {\"section\": [\"post\"]}",
            additionalProperties: { type: "array", items: { type: "string" } }
          },
          limit: {
            type: "integer",
            description: "Maximum number of results (default 10, maximum 25)",
            minimum: 1,
            maximum: 25
          }
        },
        required: ["query"]
      },
      annotations: {
        readOnlyHint: true,
        untrustedContentHint: true
      },
      execute: executeSearch(bundlePath)
    })
    .catch((error: unknown) => {
      console.warn("[webmcp-search] could not register search tool:", error);
    });
});
