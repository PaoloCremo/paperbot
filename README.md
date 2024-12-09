# PepFindBot: ArXiv Paper Finder and Telegram Notifier

`Paperbot` is a Python package that helps you find and track new papers on ArXiv based on specified keywords and authors. It automatically sends notifications about the found papers to your Telegram account.

## Features

- Search for papers on ArXiv by keywords
- Find papers by specific authors
- Support for multiple ArXiv fields (e.g., 'gr-qc', 'astro-ph')
- Automatic Telegram notifications for new papers
- Customizable search parameters

## Project Structure
```
.  
├── setup.py  
├── paper_finder.py
├── README.md  
└── findpaper/  
    ├── __init__.py
    └── find_paper.pt
```

## Installation

To install `paperbot`, run the following command:  
```bash
pip install git+https://github.com/PaoloCremo/paperbot.git
```

Or clone the repo, go into the folder and then run  
```bash
pip install .
```

## Automated Daily Search

The package includes a `paper_finder.py` script that can be used for automated daily searches. Here's how it works:

- **Weekday Check**: It checks if it's a weekday (Monday to Friday).
- **Search Papers**: If it's a weekday, it searches for papers in specified fields using given keywords and authors.
- **Telegram Notifications**: It sends the results via Telegram.

---

## Setting up Telegram Notifications

1. **Create a Telegram bot**:
   - Use [BotFather](https://core.telegram.org/bots#botfather) to create a new bot and obtain its token.

2. **Install the `telegram-send` package**:
   ```bash
   pip install telegram-send
   ```
3. **Configure telegram-send**:  
    Run the following command and provide your bot token during setup:
    ```bash
    telegram-send --configure
    ```
    The configuration file will be saved in the .telconfigs folder in your Git repository.

## Requirements

- **Python**: 3.6+
- **Dependencies**:
  - `numpy`
  - `pandas`
  - `telegram-send`
  - `beautifulsoup4`
  - `matplotlib`

---

## License

This project is licensed under the MIT License. See the [license](LICENSE.md) file for details.

---

## Usage Instructions

1. **Set up your Telegram bot and configuration** (see above).
2. **Customize the script**:
   - Modify the `wrds`, `fields`, and `author_list` variables in `paper_finder.py` to suit your needs.
3. **Run the script daily**:
   - Use a scheduler like `cron` or another task automation tool to execute the script on weekdays.

---

## Contact

Paolo Cremonese | [@PaoloCremo](https://github.com/PaoloCremo)

---