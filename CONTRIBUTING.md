# Contributing to ShopShield AI

Thank you for your interest in contributing to ShopShield AI.

---

## How to Contribute

### 1. Report Issues

- Check if the issue already exists in the repository
- Provide clear steps to reproduce the issue
- Include screenshots if applicable
- Describe expected behavior versus actual behavior
- Specify environment details (OS, Python version, dependencies)

### 2. Suggest Features

- Describe the feature clearly with use cases
- Explain why it would be useful for the project
- Provide examples if possible
- Consider the project scope and objectives

### 3. Submit Code Changes

1. Fork the repository
2. Create a feature branch
3. Write clean, documented code
4. Test your changes thoroughly
5. Submit a pull request with clear description

---

## Development Setup

```bash
# Clone the repository
git clone https://github.com/imnaim55/ShopShield-AI.git
cd ShopShield-AI

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
Code Style Guidelines
Follow PEP 8 guidelines for Python code

Use meaningful variable and function names

Add comments for complex logic

Write docstrings for all functions and classes

Maintain consistent indentation (4 spaces)

Keep lines under 100 characters where possible

Use type hints for function parameters and return values

Testing Requirements
Before submitting a pull request, ensure:

All existing tests pass

New features include appropriate tests

No new warnings or errors are introduced

The application runs without exceptions

bash
# Quick validation test
python -c "from url_analyzer import predict_url_risk; print('Tests passed')"

# Run comprehensive model test
python test_model.py
Pull Request Process
Ensure your code follows the style guidelines

Update documentation for any changed features

Add tests for new functionality

Ensure all tests pass

Submit the pull request with a clear description of changes

Respond to review feedback promptly

Development Workflow
Branch Naming Convention
Feature branches: feature/feature-name

Bug fixes: fix/bug-description

Documentation: docs/documentation-update

Hotfixes: hotfix/issue-description

Commit Messages
Use clear, descriptive commit messages

Start with a verb in present tense

Keep the first line under 50 characters

Provide additional context in the body if needed

Example:

text
Add dark pattern detection for urgency patterns

- Implement keyword matching for urgency phrases
- Add severity scoring for detected patterns
- Update UI to display pattern breakdown
Commit Message Types
Type	Description
feat	New feature implementation
fix	Bug fix
docs	Documentation only changes
style	Code style changes (formatting, etc.)
refactor	Code refactoring without functional changes
test	Adding or modifying tests
chore	Maintenance tasks
Areas for Contribution
High Priority
Improve Heuristic Rules – Add more detection patterns

Enhance ML Model – Experiment with different algorithms

Add New Features – Domain age, SSL certificate, WHOIS data integration

Medium Priority
Improve UI/UX – Better visual design and user experience

Dark Pattern Detection – Expand pattern library

Performance Optimization – Improve response times

Low Priority
Multi-language Support – Add support for additional languages

Documentation – Improve existing documentation

Testing – Add more comprehensive test coverage

Code Review Guidelines
Review for correctness, performance, and maintainability

Check adherence to style guidelines

Verify test coverage and quality

Ensure documentation is updated

Provide constructive and actionable feedback

Reporting Security Issues
If you discover a security vulnerability:

Do not create a public issue

Contact the maintainer directly via email

Provide detailed information about the vulnerability

Allow time for the issue to be addressed before disclosure

License
By contributing, you agree that your contributions will be licensed under the MIT License.

Contact
For questions, suggestions, or contributions:

Naim Shaikh

Email: naimshaikh14012001@gmail.com

GitHub: @imnaim55
