# Stocks-Scraper
# Project Description
A Python Flask web application, using multithreaded queues to web scrape and return stock ticker information.

# How Does it Work?

## Setup

### Create a virtual environment
```bash
python -m venv .venv
```

### Activate the virtual environment 
For Windows, run the following command:
```
.venv/Scripts/Activate.ps1
```

For Linux, run the following command:
```bash
source .venv/bin/activate
```

## Running Stocks-Scraper locally
> Remember to activate the virtual environment created above before running the Flask application.  

### Flask
You need to start the Flask server locally to host the application.

- For Windows:
  ```bash
  flask run
  ```
- For Unix:
  ```bash
  make develop
  ```

### Web Application
In the input form, a user can enter as many comma-seperated stock symbols as they would like, and press the "submit" button. 
> For example, a user may enter `goog, msft, amzn, dis, amc, aapl, amd, rblx, nvda, f, fb, snap, aal, uber, znga`

The user will then be redirected to a page containing a table displaying the appropriate ticker information.
The user may click the "go back" button to retrieve information for different stock symbols.
