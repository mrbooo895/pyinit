<div align="center">

# 🚀 PyInit

### *Your All-in-One Python Project Manager*

[![Version](https://img.shields.io/badge/version-1.0.14-blue.svg)](https://github.com/mrbooo895/pyinit)
[![Python](https://img.shields.io/badge/python-3.10+-brightgreen.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/mrbooo895/pyinit/pulls)

**PyInit** is a powerful, all-in-one command-line tool for managing Python projects professionally. From project creation to deployment, PyInit provides everything you need! 🎯

[Installation](#-installation) • [Features](#-features) • [Quick Start](#-quick-start) • [Commands](#-commands) • [Documentation](#-documentation)

</div>

---

## ✨ Features

<table>
<tr>
<td width="50%">

### 🎨 **Project Management**
- ✅ Initialize existing directories
- ✅ Clean temporary & build files
- ✅ Comprehensive project health checks

</td>
<td width="50%">

### 📦 **Dependency Management**
- ✅ Add & update packages effortlessly
- ✅ Visualize dependency graphs
- ✅ Auto-sync dependencies

</td>
</tr>
<tr>
<td width="50%">

### 🔧 **Development Tools**
- ✅ Format code with Black & isort
- ✅ Lint code with Ruff
- ✅ Run tests with Pytest
- ✅ Virtual environment management

</td>
<td width="50%">

### 🚢 **Build & Deployment**
- ✅ Build wheels & source distributions
- ✅ Semantic version management
</td>
</tr>
</table>

---

## 📥 Installation

## Install From PIP

```bash
pip install pyinit-tool
```

## Install From AUR (Arch Users Repository) using yay/paru

```bash
yay -S python-pyinit
paru -S python-pyinit
```

### Install from source

```bash
git clone https://github.com/mrbooo895/pyinit.git
cd pyinit
pip install -e .
```

### Requirements

- Python 3.10+
- pip
- Git (optional, for version control)

---

## 🚀 Quick Start

### Create a New Project

```bash
# Create Your Project
pyinit create my_project

```

### Initialize an Existing Directory

```bash
cd my_existing_code
pyinit init
```

### Run Your Project

```bash
pyinit run
```

### Add Dependencies

```bash
pyinit install requests
pyinit install flask numpy pandas
```

---

### Remove Modules

```bash
pyinit uninstall requests
pyinit uninstall flask numpy pandas
```

---

## 📚 Commands

### 🆕 Project Creation & Initialization

| Command | Description |
|---------|-------------|
| `pyinit create <name>` | Create a new Python project |
| `pyinit init` | Initialize PyInit structure in existing directory |
| `pyinit info` | Display comprehensive project information |

### ▶️ Running & Testing

| Command | Description |
|---------|-------------|
| `pyinit run [args]` | Run your project's main file |
| `pyinit test [pytest-args]` | Run tests with pytest |

### 📦 Dependency Management

| Command | Description |
|---------|-------------|
| `pyinit install <package>` | Install a package to your project |
| `pyinit uninstall <package>` | uninstall a package from your project |
| `pyinit update` | Check for outdated modules |
| `pyinit update --upgrade` | Upgrade project dependencies |
| `pyinit graph` | Display dependency tree |

### 🔧 Code Quality

| Command | Description |
|---------|-------------|
| `pyinit format` | Format code with Black & isort |
| `pyinit check [ruff-args]` | Lint code with Ruff |
| `pyinit clean` | Remove temporary files |

### 🏗️ Building & Releasing

| Command | Description |
|---------|-------------|
| `pyinit build` | Build distributable packages |
| `pyinit release <major\|minor\|patch>` | Increment version number |

### 🌐 Environment & Deployment

| Command | Description |
|---------|-------------|
| `pyinit venv create` | Create virtual environment |
| `pyinit venv remove` | Remove virtual environment |

---

## 🎯 Usage Examples

### Complete Workflow Example

```bash
# 1. Create a new project
pyinit create awesome_project

# 2. Navigate to the project
cd awesome_project

# 3. Add dependencies
pyinit install requests beautifulsoup4 pandas

# 4. Write your code in src/awesome_project/

# 5. Run the project
pyinit run

# 6. Add tests in tests/

# 7. Run tests
pyinit test

# 8. Format and check code
pyinit format
pyinit check

# 9. Build the package
pyinit build

# 10. Increment version
pyinit release patch

```
## 📁 Project Structure

PyInit creates a clean, standardized project structure:

```
my_project/
├── src/
│   └── my_project/
│       ├── __init__.py
│       └── main.py
├── tests/
│   └── __init__.py
├── docs/
├── venv/
├── .gitignore
├── pyproject.toml
├── README.md
└── LICENSE
```

---

**Checks include:**
- ✅ `pyproject.toml` validity
- ✅ Source directory structure
- ✅ Virtual environment existence
- ✅ Dependency synchronization
- ✅ Git repository initialization
- ✅ `.gitignore` presence
- ✅ Tests directory existence

---

## 🛠️ Advanced Features

### Semantic Versioning

```bash
# Increment patch version (1.0.0 → 1.0.1)
pyinit release patch

# Increment minor version (1.0.0 → 1.1.0)
pyinit release minor

# Increment major version (1.0.0 → 2.0.0)
pyinit release major
```

### Dependency Graph Visualization

```bash
pyinit graph
```

View your project's complete dependency tree with `pipdeptree`.

---

## 📖 Documentation

Full HTML documentation is available in the `docs/html/` directory. Open `index.html` in your browser to explore:

- API Reference
- Module Documentation
- Function Signatures
- Class Diagrams
- Dependency Graphs

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

---

## 📝 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

```
Copyright (c) 2025 mrbooo895

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files...
```

---

## 🙏 Acknowledgments

- **Rich** - Beautiful terminal formatting
- **Black** & **isort** - Code formatting
- **Ruff** - Fast Python linter
- **Pytest** - Testing framework
- **Build** - PEP 517 build backend

---

## 📞 Support

- 🐛 **Issues**: [GitHub Issues](https://github.com/mrbooo895/pyinit/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/mrbooo895/pyinit/discussions)
- 📧 **Email**: kwkkna3@gmail.com

---

<div align="center">

### ⭐ If you find PyInit useful, please consider giving it a star!

**Made with ❤️ by mrbooo895**

[⬆ Back to Top](#-pyinit)

</div>
