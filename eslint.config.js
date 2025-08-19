// eslint.config.js
export default [
  {
    ignores: [
      "**/node_modules/**",
      "**/dist/**",
      "**/build/**",
      "**/.next/**",
      "**/coverage/**",
      "**/.git/**",
      "**/*.min.js",
      "**/*.ts",
      "**/*.tsx", // Skip TypeScript files since we don't have parser
      "**/frontend/**/*.js", // Skip React frontend files (JSX without extension)
      "**/lyra-ai/frontend/**/*.js", // Skip React frontend files
    ],
  },
  {
    files: ["**/*.js", "**/*.mjs"],
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: "module",
      globals: {
        // Node.js globals
        process: "readonly",
        console: "readonly",
        Buffer: "readonly",
        __dirname: "readonly",
        __filename: "readonly",
        module: "readonly",
        require: "readonly",
        // Browser globals
        window: "readonly",
        document: "readonly",
        navigator: "readonly",
        fetch: "readonly",
        URL: "readonly",
        Audio: "readonly",
        alert: "readonly",
        IntersectionObserver: "readonly",
        PerformanceObserver: "readonly",
        LYRA_API_URL: "readonly", // Application specific global
      },
    },
    rules: {
      // Error prevention - more lenient for unused vars
      "no-unused-vars": [
        "error",
        {
          argsIgnorePattern: "^_",
          varsIgnorePattern:
            "^_|^(triggerLearning|fetchPrivateReport|runTerminalCommand|lyraListen|setMood|err)$",
        },
      ],
      "no-undef": "error",
      "no-console": "off", // Allow console in this project

      // Code style (let Prettier handle formatting)
      semi: ["error", "always"],
      quotes: ["error", "double", { avoidEscape: true }],

      // Best practices
      eqeqeq: ["error", "always", { null: "ignore" }],
      curly: ["error", "all"],
      "no-eval": "error",
      "no-implied-eval": "error",
    },
  },
];
