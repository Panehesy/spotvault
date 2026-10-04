# Contributing to SpotVault

Thank you for your interest in contributing to SpotVault! We welcome bug reports, feature requests, and pull requests.

## 🐛 Reporting Bugs

When reporting an issue, please ensure you include:

- Your Operating System (Windows 11, Ubuntu 24.04, etc.)
- Python version (`python --version`)
- Exact command or action performed
- Any relevant logs or error stack traces
- **Important**: Do not include account credentials, access tokens, or personal identifiers in your reports.

## 🛠️ Submitting Pull Requests

1. **Fork the repository** and create a new branch (`git checkout -b feature/your-feature-name`).
2. **Write tests** for your changes. The test suite uses Python's built-in `unittest` framework.
   - Run tests using: `python -m unittest discover tests -v`
3. **Follow the code style**. Keep the code clean, use type hinting where appropriate, and ensure compatibility with Python 3.10+.
4. **Commit your changes**. Use clear and descriptive commit messages.
5. **Push to the branch** and submit a Pull Request.

## 🌍 Translations / Internationalization

If you'd like to improve the existing translations or add a new language, modify the `core/i18n.py` file. SpotVault is designed to be easily extensible for new languages.

Thank you for making SpotVault better!
