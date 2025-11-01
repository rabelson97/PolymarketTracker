---
description: "Spec-Kit development rules and context"
---

# Spec-Kit Development Rules

This project follows **Spec-Driven Development (SDD)** using GitHub Spec Kit.

## Core Principles

1. **Specification First**: All features start with a spec in `spec/SPEC.md`
2. **Minimal Implementation**: Write only code that directly addresses requirements
3. **Clear Documentation**: Keep specs concise and actionable

## Project Structure

```
spec/
  SPEC.md           # Main specification
.amazonq/prompts/   # Amazon Q Developer prompts
memory/             # Project memory and context
templates/          # Spec-kit templates
```

## Development Workflow

1. **Read the spec** in `spec/SPEC.md`
2. **Implement requirements** exactly as specified
3. **Test against success criteria**
4. **Update spec** if requirements change

## When Implementing

- Reference `spec/SPEC.md` for all requirements
- Follow the technical design in the spec
- Use specified data models and algorithms
- Meet all success criteria
- Ask for clarification on open questions

## Memory System

The `memory/` directory contains:
- `constitution.md` - Project principles and guidelines

Refer to memory files for project context and decisions.

## Commands

Use `/implement-spec` to start implementing the specification.

---

For more on Spec-Driven Development, see `spec-driven.md`.
