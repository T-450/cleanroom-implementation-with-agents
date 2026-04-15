```markdown
# cleanroom-implementation-with-agents Development Patterns

> Auto-generated skill from repository analysis

## Overview
This skill teaches you the core development patterns used in the `cleanroom-implementation-with-agents` TypeScript repository. You'll learn about file organization, import/export conventions, commit message styles, and how to write and run tests. The repository is framework-agnostic, focusing on clean, modular TypeScript code—ideal for agent-based or cleanroom implementations.

## Coding Conventions

### File Naming
- **Style:** kebab-case (all lowercase, words separated by hyphens)
- **Example:**  
  ```
  agent-manager.ts
  cleanroom-logic.test.ts
  ```

### Imports
- **Style:** Relative imports are used throughout the codebase.
- **Example:**
  ```typescript
  import { Agent } from './agent';
  import { runSimulation } from '../utils/simulation';
  ```

### Exports
- **Style:** Named exports are preferred over default exports.
- **Example:**
  ```typescript
  // agent.ts
  export function createAgent() { ... }
  export const AGENT_TYPE = 'cleanroom';
  ```

### Commit Messages
- **Pattern:** Freeform (no strict prefixes), average length ~61 characters.
- **Example:**  
  ```
  Add agent initialization logic and refactor simulation steps
  ```

## Workflows

### Adding a New Agent
**Trigger:** When you need to introduce a new agent type or behavior.
**Command:** `/add-agent`

1. Create a new file in kebab-case (e.g., `custom-agent.ts`).
2. Implement the agent logic using named exports.
3. Import your new agent into the relevant manager or simulation file using a relative path.
4. Write a corresponding test file (e.g., `custom-agent.test.ts`).
5. Commit your changes with a descriptive message.

### Running Tests
**Trigger:** When you want to verify code correctness.
**Command:** `/run-tests`

1. Identify test files (pattern: `*.test.*`).
2. Use the project's preferred test runner (not specified; check documentation or scripts).
3. Run all tests and review output for failures.

### Refactoring Code
**Trigger:** When improving code structure or readability.
**Command:** `/refactor`

1. Update file and variable names to follow kebab-case and named export conventions.
2. Adjust import statements to use relative paths.
3. Ensure all changes are covered by tests.
4. Commit with a clear, descriptive message.

## Testing Patterns

- **Test File Naming:**  
  Test files follow the pattern `*.test.*` (e.g., `agent-manager.test.ts`).
- **Framework:**  
  Not explicitly specified; check for a test runner in package scripts or documentation.
- **Example Test File:**
  ```typescript
  // agent-manager.test.ts
  import { createAgent } from './agent-manager';

  describe('createAgent', () => {
    it('should initialize agent with default values', () => {
      const agent = createAgent();
      expect(agent).toHaveProperty('id');
    });
  });
  ```

## Commands
| Command      | Purpose                                           |
|--------------|---------------------------------------------------|
| /add-agent   | Scaffold and integrate a new agent implementation |
| /run-tests   | Run all test files in the codebase                |
| /refactor    | Refactor code to align with repository conventions|
```