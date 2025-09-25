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
  - [Translation System](#translation-system)
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
- Optional: Ghostscript for Wand backend support

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

1. **Install development tools**:

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
- Use type hints consistently for better code maintainability
- Optimize for readability over premature optimization
- Write modular code, using separate files for models, data loading, training, and evaluation

### Type Hints

- Use type hints consistently throughout the codebase
- Import necessary types from the `typing` module
- Use Union types where appropriate for multiple possible types
- Add return type hints to all functions and methods
- Use Optional for parameters that can be None
- Follow the format: `def function_name(param: type) -> return_type:`

### Documentation

- Document all public APIs with comprehensive docstrings
- Include examples for complex functionality
- Update README.md, CHANGELOG.md, and other documentation when adding new features
- Keep documentation up-to-date with code changes
- Use clear, concise language in documentation

### Translation System

PDF Duplicate Finder uses a Python module-based translation system (as of v3.0.0):

- **Translation Files**: Located in `script/lang/`
- **Language Manager**: `script/lang/lang_manager.py` contains the SimpleLanguageManager class
- **Adding New Languages**:
  1. Add new language entries to `script/lang/`
  2. Update the available languages list in `SimpleLanguageManager`
  3. Ensure all translation keys have fallbacks to English
- **Translation Keys**: Use descriptive keys without prefixes (e.g., "Files" instead of "ui.files")
- **Testing**: Test language switching thoroughly to ensure all UI elements update correctly
- **Help Dialog**: The help dialog supports 12 languages with dynamically generated language buttons
- **Language Support**: Currently supports English, Italian, Russian, Ukrainian, German, French, Portuguese, Spanish, Japanese, Chinese, Arabic, and Hebrew

## Testing

### Running Tests

The project uses pytest for testing:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=script --cov-report=html

# Run specific test file
pytest tests/test_specific_module.py

# Run tests with verbose output
pytest -v
```

### Test Structure

- Place test files in the `tests/` directory
- Name test files as `test_*.py`
- Use descriptive test function names starting with `test_`
- Group related tests in classes
- Use fixtures for common test setup

### Test Coverage

- Aim for high test coverage for new features
- Write tests for bug fixes to prevent regressions
- Include edge cases and error conditions in tests
- Test both success and failure scenarios

## Submitting Changes

### Pull Request Process

1. **Ensure your code follows all coding standards**
2. **All tests pass** (run `pytest` locally)
3. **Update documentation** if applicable
4. **Add tests** for new functionality or bug fixes
5. **Update CHANGELOG.md** for significant changes
6. **Create a clear PR description** that includes:
   - What changes were made and why
   - Any breaking changes
   - How to test the changes
   - Related issues (if any)

### Code Review Process

- Address all review comments promptly
- Be responsive to feedback and suggestions
- Keep PRs focused and manageable in size
- Ensure continuous integration passes before merging

### Commit Message Guidelines

Use the following format for commit messages:

```text
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

#### Types

- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc)
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `perf`: A code change that improves performance
- `test`: Adding missing tests or correcting existing tests
- `chore`: Changes to the build process or auxiliary tools and libraries
- `i18n`: Translation and internationalization changes

#### Examples

```text
feat(ui): add dark mode support

Add dark mode theme toggle to the settings dialog.
Implements #123

feat(pdf): implement text-based comparison

Add text extraction and comparison for PDF files.
This allows finding duplicates with minor visual differences.
Fixes #456

fix(ui): resolve duplicate signal connections

Remove duplicate itemDoubleClicked connections that were
causing multiple PDF viewers to open on double-click.
Fixes #789

i18n: add Italian translations

Add complete Italian translation for all UI elements.
Update translation system to support new language.
```

## Reporting Issues

When reporting issues, please include:

- **Clear description** of the problem
- **Steps to reproduce** the issue
- **Expected behavior** vs. **actual behavior**
- **Environment information**:
  - Operating system and version
  - Python version
  - Application version
  - Relevant dependencies versions
- **Error messages** and stack traces (if applicable)
- **Screenshots** (for UI issues)

Use the GitHub issue template when available.

## Feature Requests

For feature requests, please provide:

- **Clear description** of the proposed feature
- **Use case** and why it would be valuable
- **Potential implementation approach** (if you have ideas)
- **Alternative solutions** considered
- **How it fits** with the existing application architecture

## Project Structure

```text
├── script/                      # Core application code
│   ├── UI/                      # User interface components
│   │   ├── main_window.py       # Main application window
│   │   ├── ui.py                # UI components and layout
│   │   ├── menu.py              # Menu system
│   │   ├── toolbar.py           # Toolbar components
│   │   ├── settings_dialog.py   # Settings dialog
│   │   ├── help.py              # Help dialog
│   │   ├── about.py             # About dialog
│   │   ├── sponsor.py           # Sponsor dialog
│   │   └── PDF_viewer.py        # PDF viewer component
│   ├── utils/                   # Utility modules
│   │   ├── scanner.py           # PDF scanning and comparison
│   │   ├── settings.py          # Application settings
│   │   ├── recents.py           # Recent files management
│   │   ├── delete.py            # File deletion utilities
│   │   └── drag_drop.py         # Drag and drop functionality
│   ├── lang/                    # Language and translation system
│   │   └── lang_manager.py      # Language management system
│   ├── logger.py                # Logging system
│   ├── update.py                # Update system
│   └── __init__.py              # Package initialization
├── tests/                       # Test files
├── assets/                      # Images and resources
├── config/                      # Configuration files
├── docs/                        # Documentation
├── main.py                      # Application entry point
├── requirements.txt             # Python dependencies
└── README.md                    # Project documentation
```

## License

By contributing to PDF Duplicate Finder, you agree that your contributions will be licensed under the [GPL-3.0 License](LICENSE).

## Getting Help

- Check the [documentation](docs/) for detailed information
- Review existing [issues](https://github.com/Nsfr750/PDF_finder/issues) for similar problems
- Join our [Discord community](https://discord.gg/ryqNeuRYjD) for discussions
- Contact the maintainer at [nsfr750@yandex.com](mailto:nsfr750@yandex.com)

Thank you for contributing to PDF Duplicate Finder! 🎉