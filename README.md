# Introduction

This script checks if there is available dates on Italy's Embassy website. Note that the script doesn't check 
which dates are actually available (which should be checked manually). 

If the script identifies that it might have available dates, the script will send an email and a website screenshot 
to the email used to authenticate to Embassy (environment variable `EMBASSY_USERNAME`). We recommend to configure this
script to run in a cron job regularly. 

# How to Install

Install all requirements

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

# Running

```bash
python check_availability.py
```
