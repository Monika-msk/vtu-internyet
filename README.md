# 🎯 VTU Internship Watcher

A Python script that automatically monitors the VTU Internyet website for new internship postings and sends instant email notifications so you never miss an opportunity!

## 🚀 Features

- **Automated Monitoring**: Checks for new internships every 30 minutes (configurable)
- **Smart Duplicate Detection**: Tracks seen internships to avoid spam notifications
- **Beautiful Email Notifications**: Rich HTML emails with internship details
- **GitHub Actions Integration**: Runs automatically in the cloud 24/7
- **Robust Error Handling**: Comprehensive logging and error recovery
- **Selenium Web Scraping**: Handles JavaScript-rendered content

## 📋 Prerequisites

- Python 3.8+
- Gmail account with App Password enabled
- GitHub account (for automated deployment)

## 🛠️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/vtu-internship-watcher.git
cd vtu-internship-watcher
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Email Settings

#### Generate Gmail App Password

1. Go to [Google Account Settings](https://myaccount.google.com/)
2. Navigate to **Security** → **2-Step Verification**
3. Scroll down to **App passwords**
4. Generate a new app password for "Mail"
5. Copy the 16-character password

#### Set Up Environment Variables

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your details:
   ```env
   SENDER_EMAIL=your-email@gmail.com
   SENDER_PASSWORD=your-16-char-app-password
   RECIPIENT_EMAIL=recipient@example.com
   ```

### 4. Test Locally

```bash
python internship_watcher.py
```

### 5. Deploy to GitHub Actions

#### Set GitHub Secrets

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Add the following secrets:
   - `SENDER_EMAIL`: Your Gmail address
   - `SENDER_PASSWORD`: Your Gmail app password
   - `RECIPIENT_EMAIL`: Email to receive notifications

#### Configure Schedule

Edit `.github/workflows/internship-watcher.yml` to adjust the monitoring frequency:

```yaml
schedule:
  # Every 30 minutes
  - cron: '*/30 * * * *'
  
  # Every hour
  - cron: '0 * * * *'
  
  # Every 2 hours
  - cron: '0 */2 * * *'
```

## 📧 Email Notification Example

When new internships are found, you'll receive a beautifully formatted email like this:

```
🎉 New VTU Internships Available!
Found 2 new internship(s) that match your criteria

🏢 Software Development Intern
📍 Bangalore, Karnataka
💼 TechCorp Solutions
📝 Exciting opportunity to work on cutting-edge projects...
[View Details]

🏢 Data Science Intern  
📍 Mumbai, Maharashtra
💼 DataTech Industries
📝 Join our team to work on machine learning projects...
[View Details]
```

## 🔧 Configuration Options

### Monitoring Frequency

Adjust the cron schedule in the GitHub Actions workflow:

- `*/15 * * * *` - Every 15 minutes
- `*/30 * * * *` - Every 30 minutes (default)
- `0 * * * *` - Every hour
- `0 */2 * * *` - Every 2 hours

### Scraping Selectors

If the website structure changes, update the CSS selectors in `internship_watcher.py`:

```python
selectors = [
    "[data-testid='internship-card']",
    ".internship-card",
    ".card",
    # Add new selectors here
]
```

## 📁 Project Structure

```
vtu-internship-watcher/
├── internship_watcher.py      # Main script
├── requirements.txt           # Python dependencies
├── .env.example              # Environment template
├── .gitignore               # Git ignore rules
├── README.md                # This file
└── .github/
    └── workflows/
        └── internship-watcher.yml  # GitHub Actions workflow
```

## 🐛 Troubleshooting

### Common Issues

1. **No internships found**
   - The website structure may have changed
   - Check the logs for CSS selector issues
   - Update selectors in the script

2. **Email not sending**
   - Verify Gmail app password is correct
   - Check if 2-factor authentication is enabled
   - Ensure environment variables are set correctly

3. **Chrome driver issues**
   - The script automatically manages ChromeDriver
   - If issues persist, check Chrome installation

### Debugging

Enable debug logging by modifying the logging level:

```python
logging.basicConfig(level=logging.DEBUG)
```

Check the logs:
- Local: `internship_watcher.log`
- GitHub Actions: Download artifacts from the workflow run

## 🔒 Security Notes

- Never commit your `.env` file to version control
- Use GitHub Secrets for sensitive information
- Gmail App Passwords are safer than regular passwords
- The script runs in a secure GitHub Actions environment

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is for educational purposes. Please respect the website's terms of service and implement appropriate rate limiting. The authors are not responsible for any misuse of this tool.

## 🙏 Acknowledgments

- VTU Internyet for providing internship opportunities
- Selenium and BeautifulSoup communities
- GitHub Actions for free automation

---

**Happy Internship Hunting! 🎉**

If you find this tool helpful, please ⭐ star the repository and share it with fellow students!
