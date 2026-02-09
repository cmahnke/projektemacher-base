import globals from "globals";
import jsParser from "eslint-plugin-json-es";
import tomlParser from "toml-eslint-parser";
import path from "node:path";
import { fileURLToPath } from "node:url";
import js from "@eslint/js";
import { FlatCompat } from "@eslint/eslintrc";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const compat = new FlatCompat({
    baseDirectory: __dirname,
    recommendedConfig: js.configs.recommended,
    allConfig: js.configs.all
});

export default [{
    ignores: ["layouts/_default/*", "node_modules/*", "scripts/**/*.toml"],
}, ...compat.extends("eslint:recommended", "plugin:toml/standard"), {
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
}, {
    files: ["**/*.toml"],
    languageOptions: {
        parser: tomlParser
    },
}, ...compat.extends("plugin:eslint-plugin-json-es/recommended").map(config => ({
    ...config,
    files: ["**/*.gjson", "**/*.geojson", "**/*.json"],
})), {
    files: ["**/*.gjson", "**/*.geojson", "**/*.json"],

    languageOptions: {
        parser: jsParser,
    },
}, {
    files: ["scripts/*.cjs", "scripts/*.mjs"],
}];
