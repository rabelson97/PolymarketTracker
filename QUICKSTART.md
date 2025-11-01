# Quick Start Guide

## What This Project Does

Tracks fresh wallets on Polymarket that:
- Have balance ≥ $50,000
- Placed their first bet with ≥ $5,000 margin

## Getting Started with Spec-Kit

This project uses **Spec-Driven Development (SDD)** from GitHub Spec Kit.

### 1. Read the Specification

```bash
cat spec/SPEC.md
```

The spec contains all requirements, technical design, and success criteria.

### 2. Implement Using Amazon Q

In Amazon Q Developer CLI, use:

```
/implement-spec
```

This will guide you through implementing the specification.

### 3. Project Structure

```
spec/SPEC.md              # Main specification - READ THIS FIRST
.amazonq/prompts/         # Amazon Q prompts
  implement-spec.md       # Implementation guide
  spec-kit-rules.md       # Development rules
memory/                   # Project context
  constitution.md         # Project principles
templates/                # Spec-kit templates
scripts/                  # Utility scripts
```

## Development Workflow

1. **Spec First**: All features start in `spec/SPEC.md`
2. **Implement**: Follow the spec exactly
3. **Test**: Verify against success criteria
4. **Update**: Modify spec if requirements change

## Key Files

- `spec/SPEC.md` - The source of truth for all requirements
- `memory/constitution.md` - Project principles and guidelines
- `spec-driven.md` - Full explanation of Spec-Driven Development
- `AGENTS.md` - Guide for adding new AI agent support

## Next Steps

1. Review `spec/SPEC.md`
2. Set up Python environment
3. Use `/implement-spec` to start coding
4. Follow the technical design in the spec

## Questions?

- Check `spec/SPEC.md` for requirements
- See "Open Questions" section in spec for clarifications needed
- Refer to `spec-driven.md` for methodology details
