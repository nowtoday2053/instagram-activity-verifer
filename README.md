# Instagram Activity Checker

A web application that helps you track the activity status of multiple Instagram accounts efficiently. This tool analyzes Instagram profiles to determine if they are active based on recent posts and stories.

## Features

- **Bulk Account Analysis**: Upload an Excel file containing Instagram usernames to check multiple accounts at once
- **Activity Indicators**:
  - Story presence check
  - Last post timestamp
  - Recent activity status (within 7 days)
- **Results Export**: Download results in CSV format (all accounts, active only, or inactive only)
- **User-Friendly Interface**: Clean and modern web interface with real-time progress tracking
- **Privacy-Focused**: Instagram credentials are used only for authentication and are never stored

## Prerequisites

- Python 3.7 or higher
- Chrome browser installed
- Internet connection

## Installation

1. Clone this repository:
```bash
git clone [repository-url]
cd insta-activity-checker
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
# On Windows
.\venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the application:
```bash
python main.py
```

2. Open your web browser and navigate to `http://127.0.0.1:8080`

3. Prepare your Excel file with Instagram usernames (supported column names: userName, Username, username, user_name, User Name, Instagram Username)

4. Enter your Instagram credentials and upload the Excel file

5. Wait for the analysis to complete

6. View results and download reports as needed

## Security Note

This application requires your Instagram credentials to access profile information. Your credentials:
- Are used only for Instagram authentication
- Are never stored or logged
- Are only kept in memory during the analysis process
- Are handled securely using Instagram's official login flow

## Technical Details

Built with:
- Flask (Web Framework)
- Selenium with undetected-chromedriver (Instagram Automation)
- Pandas (Excel File Processing)
- Bootstrap (Frontend Styling)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 
