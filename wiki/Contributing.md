# Contributing Guide

Thank you for your interest in contributing to Healthcare Auditor! This document provides guidelines for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Development Workflow](#development-workflow)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Requirements](#testing-requirements)
- [Documentation](#documentation)

---

## Code of Conduct

### Our Pledge

In the interest of fostering an open and welcoming environment, we pledge to:

- Respect differing viewpoints and experiences
- Gracefully accept constructive criticism
- Focus on what is best for the community
- Show empathy towards other community members

### Standards

Examples of behavior that contributes to a positive environment:

- Using welcoming and inclusive language
- Being respectful of differing viewpoints and experiences
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

Examples of unacceptable behavior:

- Harassment or inappropriate language
- Personal attacks or trolling
- Public or private harassment
- Publishing others' private information
- Other unethical or unprofessional conduct

### Enforcement

Project maintainers have the right and responsibility to remove, edit, or reject comments, commits, code, wiki edits, issues, and other contributions that are not aligned to this Code of Conduct.

---

## Getting Started

### Prerequisites

Before contributing, ensure you have:

- Python 3.11+ installed
- Poetry for dependency management
- Git configured
- Familiarity with FastAPI, SQLAlchemy, and testing

### Initial Setup

```bash
# Fork the repository
# Click "Fork" on GitHub

# Clone your fork
git clone https://github.com/YOUR_USERNAME/healthcare-auditor.git
cd healthcare-auditor

# Add upstream remote
git remote add upstream https://github.com/calebrosario/healthcare-auditor.git

# Install dependencies
cd backend
poetry install

# Run tests
poetry run pytest tests/ -v
```

---

## How to Contribute

### Types of Contributions

We welcome contributions in many forms:

- 🐛 **Bug Reports** - Found a bug? Let us know!
- ✨ **New Features** - Have a great idea? Propose it!
- 📝 **Documentation** - Improve our docs
- 🧪 **Testing** - Add more test coverage
- 🎨 **Design** - Improve UI/UX
- 🌍 **Translations** - Add language support
- 💡 **Ideas** - Share your thoughts

### Reporting Bugs

Before reporting bugs, please:

1. **Search existing issues** - Avoid duplicates
2. **Check recent commits** - May already be fixed
3. **Create minimal reproduction** - Minimal code example
4. **Include environment details** - OS, Python version, etc.

**Bug Report Template**:

```markdown
## Bug Report

### Description
[Clear description of the bug]

### Reproduction Steps
1. [First step]
2. [Second step]
3. [And so on...]

### Expected Behavior
[What should happen]

### Actual Behavior
[What actually happens]

### Environment
- OS: [e.g., Ubuntu 22.04]
- Python: [e.g., 3.11.5]
- Version: [e.g., 1.0.0]

### Logs/Error Messages
```
[Paste relevant logs]
```

---

### Suggesting Enhancements

**Feature Request Template**:

```markdown
## Feature Request

### Problem Statement
[What problem does this solve?]

### Proposed Solution
[How do you propose solving it?]

### Alternatives Considered
[What alternatives did you consider?]

### Additional Context
[Any other context, mockups, etc.]
```

---

## Development Workflow

### 1. Create Branch

```bash
# Sync with upstream
git fetch upstream
git checkout master
git merge upstream/master

# Create feature branch
git checkout -b feature/your-feature-name

# Or bugfix branch
git checkout -b bugfix/your-bugfix-name
```

### 2. Make Changes

```bash
# Write code
nano backend/app/new_feature.py

# Format code
black backend/app/

# Run tests
poetry run pytest tests/ -v

# Commit changes
git add backend/app/new_feature.py
git commit -m "feat: add new feature"
```

### 3. Push and Create PR

```bash
# Push to your fork
git push origin feature/your-feature-name

# Create Pull Request on GitHub
# https://github.com/YOUR_USERNAME/healthcare-auditor/compare
```

---

## Pull Request Process

### Before Submitting

Check these boxes before opening a PR:

- [ ] Code follows style guidelines (Black, Ruff)
- [ ] Tests added for new functionality
- [ ] All tests pass locally
- [ ] No new linting errors
- [ ] Documentation updated (README, Wiki)
- [ ] Commit messages follow conventional format
- [ ] PR description is clear and comprehensive

### Pull Request Template

```markdown
## Description
[Brief description of changes]

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
### Manual Testing
- [ ] Tested locally
- [ ] Tested on staging
### Automated Testing
- [ ] All tests pass
- [ ] Coverage maintained or improved
- [ ] No flaky tests

## Checklist
- [ ] My code follows the style guidelines of this project
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] Any dependent changes have been merged and published

## Related Issues
Closes #(issue number)
Fixes #(issue number)
Related to #(issue number)
```

### Review Process

1. **Automated Checks** - CI runs tests, linting, type checking
2. **Code Review** - Maintainers review for:
   - Code quality and style
   - Logic correctness
   - Security implications
   - Performance considerations
   - Test coverage
3. **Feedback** - Reviewers may request changes
4. **Approval** - Requires at least one maintainer approval
5. **Merge** - Maintainers squash and merge to master

### During Review

- Respond to review comments promptly
- Make requested changes
- Push to same branch (don't create new PR)
- Be patient - maintainers are volunteers

---

## Coding Standards

### Style Guidelines

```python
# Follow PEP 8 with Black
# Line length: 120 characters
# Indentation: 4 spaces
# Quotes: Double quotes

# Use type hints
def validate_bill(bill: Bill) -> ValidationResult:
    """Validate a bill."""
    pass

# Use async/await
async def get_bills() -> List[Bill]:
    async with get_db() as session:
        result = await session.execute(select(Bill))
        return result.scalars().all()
```

### Naming Conventions

- **Variables**: `snake_case` - `billed_amount`, `provider_id`
- **Functions**: `snake_case` - `validate_bill()`, `calculate_score()`
- **Classes**: `PascalCase` - `BillValidator`, `MLModelEngine`
- **Constants**: `UPPER_SNAKE_CASE` - `FRAUD_THRESHOLD`, `MAX_RETRIES`

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance

**Examples**:
```
feat(rules): add provider frequency limit validation

Add new rule to validate provider procedure frequency
within 30-day window to prevent excessive billing.

Closes #123
```

---

## Testing Requirements

### Test Coverage

| Component | Minimum Coverage |
|-----------|-----------------|
| Rules Engine | 90% |
| ML Models | 85% |
| API Endpoints | 95% |
| Core Logic | 90% |
| **Overall** | **80%** |

### Writing Tests

```python
# Unit test example
import pytest
from app.rules.coding_rules import ICD10ValidationRule

@pytest.mark.asyncio
async def test_valid_icd10_code():
    """Test valid ICD-10 code."""
    rule = ICD10ValidationRule()
    result = await rule.validate(valid_bill, {})
    assert result.is_valid is True

@pytest.mark.asyncio
async def test_invalid_icd10_code():
    """Test invalid ICD-10 code."""
    rule = ICD10ValidationRule()
    result = await rule.validate(invalid_bill, {})
    assert result.is_valid is False
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=backend/app --cov-report=html

# Run specific test file
pytest tests/unit/test_rules_engine.py -v
```

---

## Documentation

### Inline Documentation

```python
def calculate_fraud_score(
    rule_results: List[ValidationResult],
    weights: dict
) -> float:
    """Calculate composite fraud score from rule results.

    Weighted average of failed rule scores.

    Args:
        rule_results: List of validation results from all rules.
        weights: Dictionary mapping rule names to weights.

    Returns:
        Composite fraud score between 0.0 and 1.0.

    Raises:
        ValueError: If weights don't sum to 1.0.
    """
    # Implementation
    pass
```

### README Updates

When adding features:

1. Update feature list
2. Add usage examples
3. Update configuration documentation
4. Add relevant links

### Wiki Updates

For significant changes:

1. Update relevant wiki pages
2. Add new pages if needed
3. Update diagrams and examples
4. Link from Home.md

---

## Release Process

Maintainers follow this process for releases:

1. **Version Bump** - Update version in `pyproject.toml`
2. **Changelog** - Update `CHANGELOG.md`
3. **Tag** - Create git tag: `git tag v1.0.0`
4. **Push** - Push tag: `git push origin v1.0.0`
5. **Release** - Create GitHub release with notes

### Semantic Versioning

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

Examples:
- `1.0.0` → `1.1.0` - New features
- `1.1.0` → `1.1.1` - Bug fix
- `1.1.1` → `2.0.0` - Breaking changes

---

## Recognition

### Contributors

All contributors are recognized in:

- **README.md** - Contributor list
- **GitHub Contributors** - Automatic recognition
- **Release Notes** - Mention significant contributions

### Becoming a Maintainer

Regular contributors may be invited to become maintainers. Criteria:

- Consistent contributions over time
- High-quality code reviews
- Active participation in discussions
- Understanding of codebase

---

## Community

### Communication Channels

- **GitHub Discussions**: Feature requests, questions
- **GitHub Issues**: Bug reports, technical issues
- **Email**: For security issues only (security@healthcare-auditor.com)

### Code of Conduct Violations

Report violations to:

- **Email**: conduct@healthcare-auditor.com
- **GitHub**: @mention maintainers in issue

All reports will be kept confidential.

---

## License

By contributing, you agree that your contributions will be licensed under the project's license (MIT).

---

## Questions?

- Check [FAQ](Home.md#faq)
- Search [GitHub Issues](https://github.com/calebrosario/healthcare-auditor/issues)
- Ask in [GitHub Discussions](https://github.com/calebrosario/healthcare-auditor/discussions)

---

## Thank You! 🎉

We appreciate your contribution to Healthcare Auditor!

**Resources**:
- **[Development Guide](Development-Guide.md)** - Coding standards
- **[Testing Guide](Testing-Guide.md)** - Testing practices
- **[Architecture Guide](Architecture.md)** - System design
