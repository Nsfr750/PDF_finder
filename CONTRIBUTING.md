# Contributing to PDF Duplicate Finder

Thank you for your interest in contributing to PDF Duplicate Finder! We welcome all contributions, whether they are bug reports, feature requests, documentation improvements, or code contributions.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Setting Up the Development Environment](#setting-up-the-development-environment)
- [Making Changes](#making-changes)
  - [Coding Standards](#coding-standards)
  - [Type Hints](#type-hints)
  - [Documentation](#documentation)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
  - [Pull Request Process](#pull-request-process)
  - [Commit Message Guidelines](#commit-message-guidelines)
- [Reporting Issues](#reporting-issues)
- [Feature Requests](#feature-requests)
- [License](#license)

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git

### Setting Up the Development Environment

1. **Fork the repository** on GitHub
1. **Clone your fork** locally:

   ```bash
   git clone https://github.com/Nsfr750/PDF_finder.git
   cd PDF_finder
   ```

1. **Set up a virtual environment** (recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

1. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

1. (Optional) **Install development tools**:

   ```bash
   pip install black flake8 mypy pytest pytest-cov
   ```

1. **Set up pre-commit hooks** (optional but recommended):

   ```bash
   pre-commit install
   ```

## Making Changes

1. **Create a new branch** for your changes:

   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/issue-number-description
   ```

1. **Make your changes** following the coding standards below.
1. **Test your changes** (see [Testing](#testing)).
1. **Commit your changes** following the [commit message guidelines](#commit-message-guidelines).
1. **Push your changes** to your fork:

   ```bash
   git push origin your-branch-name
   ```

1. **Open a Pull Request** from your fork to the main repository.

### Coding Standards

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guidelines
- Use 4 spaces for indentation (no tabs)
- Keep lines under 100 characters
- Use docstrings for all public modules, functions, classes, and methods
- Write meaningful variable and function names
- Keep functions small and focused on a single task
- For text comparison features, ensure proper encoding handling
- When working with file filters, maintain backward compatibility

### Type Hints

1. Use Python type hints for all function signatures and variables where the type is not obvious.
1. Run mypy to check type consistency:

  ```bash
  mypy .
  ```

### Documentation

- Update documentation when adding new features or changing behavior.
- Keep docstrings up-to-date.
- Document all public APIs.
- Update README.md if necessary.

## Testing

- Write unit tests for all new functionality
- Ensure all tests pass before submitting a pull request
- Include test data with your tests when appropriate
- Test on multiple platforms when possible
- For text comparison features, include tests for different encodings
- Test filtering with various combinations of file sizes and dates

1. **Run the tests**:

   ```bash
   pytest
   ```

1. **Generate a coverage report**:

   ```bash
   pytest --cov=.
   ```

1. **Run UI tests** (if applicable):

   ```bash
   # Add UI test commands here
   ```

## Submitting Changes

### Pull Request Process

1. Ensure any install or build dependencies are removed before the end of the layer when doing a build.
2. Update the README.md with details of changes to the interface, this includes new environment variables, exposed ports, useful file locations, and container parameters.
3. Update the version in `script/version.py` following [SemVer](http://semver.org/). Update README.md/examples as needed.
4. You may merge the Pull Request in once you have the sign-off of two other developers, or if you do not have permission to do that, you may request the second reviewer to merge it for you.

### Commit Message Guidelines

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification for commit messages:

```text
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types**:

- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc)
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `perf`: A code change that improves performance
- `test`: Adding missing tests or correcting existing tests
- `chore`: Changes to the build process or auxiliary tools and libraries

### Example Commit Message

```text
feat: add dark mode support

Add a new dark theme option that can be toggled in the settings menu.
This improves accessibility and user experience in low-light conditions.

Closes #123
```

## Reporting Issues

When reporting issues, please include:

1. A clear, descriptive title
2. A description of the problem
3. Steps to reproduce the issue
4. Expected vs. actual behavior
5. Screenshots (if applicable)
6. Your operating system and Python version
7. Any error messages or logs

## Feature Requests

We welcome feature requests! Please open an issue with:

1. A clear, descriptive title
2. A detailed description of the feature
3. The problem it solves
4. Any examples or mockups (if applicable)

## License

By contributing to PDF Duplicate Finder, you agree that your contributions will be licensed under its [GPLv3 License](LICENSE).

---

Note: When changing PDF backend logic or settings, ensure documentation is updated:

- README: PDF Backends and Fallback section
- PREREQUISITES.md: Poppler/Ghostscript install instructions
- Add/update tests in `tests/` accordingly

Last Update: September 2025