# Contributing to Stock Analyzer

Thank you for your interest in contributing to Stock Analyzer! This document provides guidelines and instructions for contributing.

## 🎯 How to Contribute

### Reporting Bugs

**Before submitting a bug report:**
- Check the [Issues](https://github.com/HelloHyman/Automated-Stock-and-Crypto-Analyzer/issues) page to avoid duplicates
- Ensure you're using the latest version
- Collect relevant information (OS version, Python version, error messages)

**When submitting a bug report, include:**
- Clear, descriptive title
- Steps to reproduce the issue
- Expected vs actual behavior
- Screenshots (if applicable)
- Error messages and logs
- System information

**Bug Report Template:**
```markdown
**Description**
A clear description of the bug

**Steps to Reproduce**
1. Go to '...'
2. Click on '....'
3. See error

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Screenshots**
If applicable

**Environment**
- OS: [e.g., Windows 11]
- Python Version: [e.g., 3.10]
- Stock Analyzer Version: [e.g., 1.0.0]
```

### Suggesting Features

We welcome feature suggestions! Please:

1. Check existing feature requests in Issues
2. Provide a clear use case
3. Explain why this feature would be useful
4. Include examples or mockups if possible

**Feature Request Template:**
```markdown
**Feature Description**
Clear description of the feature

**Use Case**
Why is this feature needed?

**Proposed Solution**
How would this work?

**Alternatives Considered**
Other approaches you've thought about
```

### Pull Requests

**Before submitting a PR:**
1. Fork the repository
2. Create a new branch from `main`
3. Make your changes
4. Test thoroughly
5. Update documentation if needed
6. Ensure code follows our style guide

**PR Guidelines:**
- Clear, descriptive title
- Reference related issues
- Describe changes made
- Include screenshots for UI changes
- Ensure all tests pass
- Keep PRs focused (one feature/fix per PR)

**PR Template:**
```markdown
## Description
What changes does this PR introduce?

## Related Issues
Fixes #(issue number)

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactoring

## Testing
How was this tested?

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests added/updated
```

## 💻 Development Setup

### Prerequisites
- Python 3.8 or higher
- Git
- (Optional) Inno Setup for installer building

### Setup Instructions

1. **Fork and Clone**
   ```bash
   git clone https://github.com/YOUR_USERNAME/Automated-Stock-and-Crypto-Analyzer.git
   cd Automated-Stock-and-Crypto-Analyzer
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**
   ```bash
   python manual_stock_analyzer.py
   ```

### Development Workflow

1. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/bug-description
   ```

2. **Make changes**
   - Write clean, documented code
   - Follow PEP 8 style guide
   - Add type hints where appropriate
   - Write meaningful commit messages

3. **Test your changes**
   ```bash
   python manual_stock_analyzer.py
   # Test all features thoroughly
   ```

4. **Commit changes**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   # or
   git commit -m "fix: resolve issue with..."
   ```

5. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create Pull Request**
   - Go to GitHub
   - Click "New Pull Request"
   - Fill out the PR template
   - Submit for review

## 📝 Code Style Guidelines

### Python Code

**Follow PEP 8:**
- Use 4 spaces for indentation
- Maximum line length: 100 characters
- Use meaningful variable names
- Add docstrings to functions/classes

**Type Hints:**
```python
def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate technical indicators.
    
    Args:
        df: DataFrame with OHLCV data
        
    Returns:
        DataFrame with added indicators
    """
    pass
```

**Error Handling:**
```python
try:
    # risky operation
    result = fetch_data()
except SpecificException as e:
    # handle specific error
    logger.error(f"Error: {e}")
    return None
```

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting)
- `refactor:` Code refactoring
- `perf:` Performance improvements
- `test:` Adding tests
- `chore:` Maintenance tasks

**Examples:**
```
feat: add Bitcoin support for crypto analysis
fix: resolve chart rendering issue on Windows 11
docs: update installation instructions
refactor: improve data caching mechanism
```

### Documentation

**When adding features:**
- Update relevant .md files
- Add inline code comments
- Include docstrings
- Update CHANGELOG.md

**Documentation standards:**
- Clear, concise language
- Examples where helpful
- Screenshots for UI features
- Keep README.md updated

## 🧪 Testing

### Manual Testing Checklist

Before submitting:
- [ ] Application launches without errors
- [ ] Can analyze stock symbols (e.g., AAPL)
- [ ] Can analyze crypto symbols (e.g., BTC-USD)
- [ ] Charts render correctly
- [ ] All timeframes work
- [ ] Moving averages display properly
- [ ] Support/Resistance lines appear
- [ ] RSI calculation is correct
- [ ] No console errors
- [ ] UI is responsive

### Test Different Scenarios

- Various stock symbols
- Crypto symbols
- Different timeframes (1d to max)
- Multiple moving averages
- Edge cases (invalid symbols, no internet)
- Long-running sessions

## 🏗️ Project Structure

```
Stock_Analyzer/
├── manual_stock_analyzer.py    # Main application
├── requirements.txt             # Dependencies
├── VERSION                      # Version number
├── LICENSE                      # MIT License
├── README.md                    # Main documentation
├── CHANGELOG.md                 # Version history
├── CONTRIBUTING.md             # This file
│
├── Build Scripts/
│   ├── build_exe.bat
│   ├── build_installer.bat
│   ├── build_simple_installer.bat
│   └── build_all_packages.bat
│
├── Setup Scripts/
│   ├── install_dependencies.bat
│   ├── check_dependencies.bat
│   └── sign_exe.bat
│
├── Installer Configs/
│   ├── installer.iss
│   ├── installer_simple.iss
│   └── stock_analyzer.spec
│
├── User Tools/
│   └── StockAnalyzer_OneClick.bat
│
└── Documentation/
    ├── USER_GUIDE.md
    ├── INSTALLER_GUIDE.md
    ├── SIGNING_GUIDE.md
    ├── ONE_CLICK_GUIDE.md
    ├── QUICK_START.md
    └── INSTALL_FOR_USERS.md
```

## 🔄 Release Process

**For Maintainers:**

1. **Update VERSION file**
   ```
   1.0.0 → 1.1.0
   ```

2. **Update CHANGELOG.md**
   - Document all changes
   - Credit contributors

3. **Update version in files**
   - installer.iss
   - installer_simple.iss
   - README.md

4. **Build packages**
   ```bash
   build_all_packages.bat
   ```

5. **Test thoroughly**

6. **Create Git tag**
   ```bash
   git tag -a v1.1.0 -m "Release version 1.1.0"
   git push origin v1.1.0
   ```

7. **Create GitHub Release**
   - Upload built packages
   - Add release notes
   - Publish

## 🤝 Code of Conduct

### Our Pledge

We pledge to make participation in our project a harassment-free experience for everyone.

### Our Standards

**Positive behavior:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what's best for the community

**Unacceptable behavior:**
- Harassment or discriminatory language
- Trolling or insulting comments
- Public or private harassment
- Publishing others' private information

### Enforcement

Project maintainers are responsible for clarifying standards and will take appropriate action in response to unacceptable behavior.

## 📞 Getting Help

- **Questions?** Open a [Discussion](https://github.com/HelloHyman/Automated-Stock-and-Crypto-Analyzer/discussions)
- **Bug?** Open an [Issue](https://github.com/HelloHyman/Automated-Stock-and-Crypto-Analyzer/issues)
- **Feature idea?** Open an [Issue](https://github.com/HelloHyman/Automated-Stock-and-Crypto-Analyzer/issues)

## 🎖️ Recognition

Contributors will be:
- Listed in CHANGELOG.md
- Mentioned in release notes
- Added to contributors section

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to Stock Analyzer!** 🚀

Every contribution, no matter how small, helps make this project better for everyone.

