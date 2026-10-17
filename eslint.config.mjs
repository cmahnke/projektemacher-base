import globals from "globals";
import js from "@eslint/js";
import eslintPluginToml from 'eslint-plugin-toml';
import eslintPluginJsonc from 'eslint-plugin-jsonc';
import tseslint from 'typescript-eslint';

export default tseslint.config(
  {
    ignores: ["layouts/_default/*", "node_modules/*", "scripts/**/*.toml"],
  },
  js.configs.recommended,
  ...eslintPluginToml.configs["flat/standard"],
  {
    languageOptions: {
        globals: {
            ...globals.browser,
            ...globals.node,
        },

        ecmaVersion: 12,
        sourceType: "module",
    },
    rules: {
        "no-unused-vars": 1,
        "no-useless-assignment": 1,
        "toml/padding-line-between-tables": 0,
        "no-prototype-builtins": 0,
    },
  },
  // TypeScript files: parser, plugin and the recommended rule set. The base
  // `no-unused-vars` rule is disabled for them by the eslint-recommended
  // overrides, `@typescript-eslint/no-unused-vars` takes over. Severities
  // match the JS configuration's warn-based philosophy for the rules that
  // fire on intentionally preserved legacy patterns.
  ...tseslint.configs.recommended,
  {
    files: ["**/*.js", "**/*.mjs", "**/*.cjs"],
    rules: {
        "@typescript-eslint/no-unused-vars": 1,
        "@typescript-eslint/no-explicit-any": 1,
        "@typescript-eslint/no-this-alias": 1,
    },
  },
  {
    files: ["**/*.ts"],
    languageOptions: {
        globals: {
            ...globals.browser,
            ...globals.node,
        },
    },
    rules: {
        "@typescript-eslint/no-unused-vars": [1, {
            "argsIgnorePattern": "^_",
            "varsIgnorePattern": "^_",
        }],
        "@typescript-eslint/no-explicit-any": 1,
        "@typescript-eslint/no-this-alias": 1,
        "no-unassigned-vars": 1,
    },
  },
  ...eslintPluginJsonc.configs["flat/recommended-with-jsonc"].map(config => ({
    ...config,
    files: ["**/*.gjson", "**/*.geojson", "**/*.json"],
  })), {
    files: ["scripts/*.cjs", "scripts/*.mjs"],
  }
);
