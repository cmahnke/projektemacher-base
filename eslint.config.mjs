import globals from "globals";
import js from "@eslint/js";
import eslintPluginToml from 'eslint-plugin-toml';
import eslintPluginJsonc from 'eslint-plugin-jsonc';

export default [
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
  ...eslintPluginJsonc.configs["flat/recommended-with-jsonc"].map(config => ({
    ...config,
    files: ["**/*.gjson", "**/*.geojson", "**/*.json"],
  })), {
    files: ["scripts/*.cjs", "scripts/*.mjs"],
  }
];
