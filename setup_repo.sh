#!/bin/bash

# Create necessary directories if they don't exist
mkdir -p backend/{api,config,models/{mongodb,postgresql},routes,services/payment,tests}

# Initialize git repository
git init

# Create .gitignore if it doesn't exist
cat > .gitignore << EOL
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
ENV/
env/
.venv/
.env

# IDE
.idea/
.vscode/
*.swp
*.swo

# Logs
*.log
logs/
app.log

# Local development
instance/
.webassets-cache

# Database
*.sqlite3
*.db

# Testing
.coverage
htmlcov/
.pytest_cache/
.tox/

# Railway
railway.toml

# OS
.DS_Store
Thumbs.db
EOL

# Add files to git
git add backend/
git add .github/
git add requirements.txt
git add .gitignore
git add README.md
git add app.py
git add config.py
git add Procfile
git add docker-compose.yml
git add Dockerfile

# Initial commit
git commit -m "Initial backend setup"

echo "Repository setup complete. Now run:"
echo "git remote add origin https://github.com/yourusername/your-repo.git"
echo "git push -u origin main" 