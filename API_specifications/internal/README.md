# Internal / code API documentation

This folder is for documenting *non-HTTP* APIs: important modules/classes/functions inside the codebase.

## What belongs here
- Scheduling + selection engine public functions
- Mastery/cooldown update rules interfaces
- YAML storage layer interfaces
- Ollama client interfaces
- Evaluator interfaces

## What does NOT belong here
- Small private helpers that are obvious from code.

## Format
- Keep docs short and focused.
- Link to the code module path once it exists.
- Include inputs/outputs, invariants, side effects, and examples.
