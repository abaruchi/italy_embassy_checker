[![License](https://img.shields.io/badge/python-3.8-blue)](https://www.python.org/downloads/release/python-380/)

# Introduction

This script checks if there is available dates on Italy's Embassy website. Note that the script doesn't check 
which dates are actually available (which should be checked manually). 

If the script identifies that it might have available dates, the script will send an email and a website screenshot 
to the email used to authenticate to Embassy (environment variable `EMBASSY_USERNAME`). We recommend to configure this
script to run in a cron job regularly. 

# How to Install

Please, make sure you are using **python 3.8** or greater before going further. To install all the requirements:

```bash
pip install -r requirements.txt
```

Create an `.env` file with the following content:

```
SMTP_SERVER="<your_smtp_server_address>"
SMTP_PORT=<your_smtp_server_port>
SMTP_USERNAME="<your_smtp_server_username>"
SMTP_PASSWORD="<your_smtp_server_password>"
SCREENSHOT_DIR="<dir_to_save_screenshots>"

EMBASSY_USERNAME="<embassy_username>"
EMBASSY_PASSWORD="<embassy_password>"
EMBASSY_HTTP_SERVER="https://prenotami.esteri.it/"
```

Download and install Chrome Driver from [here](https://chromedriver.chromium.org/downloads).

# Running

```bash
python check_availability.py
```
