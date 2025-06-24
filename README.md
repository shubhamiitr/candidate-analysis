# 🔍 Enhanced GitHub Candidate Analysis Tool

A comprehensive candidate analysis system that leverages GitHub data and browser automation to provide detailed insights about software engineering candidates for hiring decisions.

## ✨ Features

### Core Capabilities
- **Comprehensive GitHub Analysis**: Deep dive into repositories, code quality, and contribution patterns
- **Browser Automation for LinkedIn**: Reliable LinkedIn profile extraction using LangChain and browser automation
- **Code Quality Assessment**: Analyzes documentation, testing practices, CI/CD usage, and architecture patterns
- **Professional Background Research**: Finds employment history, achievements, and industry recognition
- **Technical Stack Analysis**: Identifies programming languages, frameworks, and technology expertise
- **Automated Scoring**: Rates candidates on technical capability, product development, and professional experience

### Enhanced Repository Analysis
- **Code Structure Analysis**: Examines project organization and architecture
- **Testing & Documentation**: Checks for test coverage and README quality  
- **Technology Stack Detection**: Identifies languages, frameworks, and tools used
- **Recent Activity Tracking**: Monitors commit patterns and project maintenance
- **Collaboration Indicators**: Assesses team contribution and community engagement

### Browser Automation Capabilities
- **LinkedIn Profile Extraction**: Automated browser-based LinkedIn profile scraping
- **Employment Verification**: Finds current and previous work experience
- **Skills and Education**: Extracts technical skills and educational background
- **Professional Summary**: Captures professional summaries and career context
- **Reliable Data Extraction**: Uses LangChain agents for intelligent data parsing

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API key
- GitHub Personal Access Token
- Google Chrome browser

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd hiring
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
Create a `.env` file in the project root:
```env
OPENAI_API_KEY=your_openai_api_key_here
GITHUB_TOKEN=your_github_token_here
BROWSER_DEBUG_URL=http://127.0.0.1:9222  # Optional: URL for browser automation
```

4. **Start browser for profile scraping**

The tool uses browser automation to extract profile data reliably. Run this command in a separate terminal and keep it running:

```bash
# macOS
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir="$HOME/.browser-use"

# Windows
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="%USERPROFILE%\.browser-use"

# Linux
google-chrome --remote-debugging-port=9222 --user-data-dir="$HOME/.browser-use"
```

5. **Log into LinkedIn**
- Open LinkedIn in the Chrome browser you just started
- Log in with your credentials
- Keep this browser window open during analysis

6. **Run the analysis**
```bash
python analyze_candidate.py --github-username example --linkedin-url https://linkedin.com/in/example
```

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For questions or issues:
1. Check the existing documentation
2. Run the setup verification script
3. Search for similar issues
4. Create a detailed issue report
5. Include error messages and environment details

---

**Note**: This tool is designed to supplement human judgment in hiring decisions, not replace it. Always combine automated analysis with personal interviews and reference checks.