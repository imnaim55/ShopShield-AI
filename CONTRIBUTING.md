# Contributing to ShopShield AI

Thank you for your interest in contributing to ShopShield AI! 🎉

## How to Contribute

### 1. Report Issues
- Check if the issue already exists
- Provide clear steps to reproduce
- Include screenshots if applicable

### 2. Suggest Features
- Describe the feature clearly
- Explain why it would be useful
- Provide examples if possible

### 3. Submit Code Changes
1. Fork the repository
2. Create a feature branch
3. Write clean, documented code
4. Test your changes
5. Submit a pull request

## Development Setup

```bash
# Clone the repository
git clone https://github.com/imnaim55/ShopShield-AI.git
cd ShopShield-AI

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

Code Style

· Follow PEP 8 guidelines
· Use meaningful variable names
· Add comments for complex logic
· Write docstrings for functions

Testing

Before submitting a pull request, run:

```bash
python -c "from url_analyzer import predict_url_risk; print('✅ Tests passed')"
```

License

By contributing, you agree that your contributions will be licensed under the MIT License.

```

---

## 📁 Save These Files

Save `README.md` and `CONTRIBUTING.md` in your project root. Then:

```bash
git add README.md CONTRIBUTING.md
git commit -m "Add README and CONTRIBUTING files"
git push origin main
```

Your repository is now ready for contributors! 🚀
