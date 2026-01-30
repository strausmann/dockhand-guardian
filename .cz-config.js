module.exports = {
  types: [
    { value: 'feat', name: 'feat:      A new feature' },
    { value: 'fix', name: 'fix:       A bug fix' },
    { value: 'docs', name: 'docs:      Documentation only changes' },
    { value: 'style', name: 'style:     Code style changes (formatting, etc.)' },
    { value: 'refactor', name: 'refactor:  Code refactoring' },
    { value: 'perf', name: 'perf:      Performance improvements' },
    { value: 'test', name: 'test:      Adding or updating tests' },
    { value: 'build', name: 'build:     Build system or dependency changes' },
    { value: 'ci', name: 'ci:        CI/CD configuration changes' },
    { value: 'chore', name: 'chore:     Other changes (maintenance, etc.)' },
    { value: 'revert', name: 'revert:    Revert a previous commit' },
  ],

  scopes: [
    { name: 'guardian' },
    { name: 'docker' },
    { name: 'compose' },
    { name: 'webhook' },
    { name: 'monitoring' },
    { name: 'recovery' },
    { name: 'ci' },
    { name: 'deps' },
    { name: 'docs' },
    { name: 'config' },
    { name: 'release' },
  ],

  scopeOverrides: {
    feat: [
      { name: 'guardian' },
      { name: 'webhook' },
      { name: 'monitoring' },
      { name: 'recovery' },
    ],
    fix: [
      { name: 'guardian' },
      { name: 'docker' },
      { name: 'compose' },
      { name: 'webhook' },
      { name: 'monitoring' },
      { name: 'recovery' },
    ],
  },

  allowCustomScopes: false,
  allowBreakingChanges: ['feat', 'fix', 'refactor', 'perf'],
  skipQuestions: [],

  // Subject settings
  subjectLimit: 100,
  subjectSeparator: ': ',
  
  // Messages
  messages: {
    type: "Select the type of change that you're committing:",
    scope: 'Select the scope of this change:',
    customScope: 'Denote the SCOPE of this change:',
    subject: 'Write a SHORT, IMPERATIVE tense description of the change:\n',
    body: 'Provide a LONGER description of the change (optional). Use "|" to break new line:\n',
    breaking: 'List any BREAKING CHANGES (optional):\n',
    footer: 'List any ISSUES CLOSED by this change (optional). E.g.: #31, #34:\n',
    confirmCommit: 'Are you sure you want to proceed with the commit above?',
  },
};
