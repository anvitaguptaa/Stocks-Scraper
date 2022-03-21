from distutils.command.clean import clean
from flask import (
    request,
    Flask,
    render_template,
    redirect,
    flash,
    url_for,
    current_app
)
from bs4 import BeautifulSoup
import time
import sys, getopt
from queue import Queue
from threading import Thread
import logging
import requests


app = Flask(__name__)


# Logging
def setup_logging(level):
    debug_fmt = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
    if level == 'info':
        fmt = "%(message)s"
        logging.basicConfig(format=fmt, level=logging.INFO )
    elif level == 'debug':
        fmt = debug_fmt
        logging.basicConfig(format=fmt, level=logging.DEBUG )
    else:
        fmt = debug_fmt
        logging.basicConfig(format=fmt, level=logging.DEBUG )


logger = logging.getLogger(__name__)


# Request headers
headers = { 
    'User-Agent'      : ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36' 
                         '(KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'), 
    'Accept'          : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 
    'Accept-Language' : 'en-US,en;q=0.5',
    'DNT'             : '1', # Do Not Track Request Header 
    'Connection'      : 'close'
}


# Crawls webpage with ticker information
def crawler(symbol):
    url = 'https://finance.yahoo.com/quote/'+ symbol + '/key-statistics?p=' + symbol
    logger.info(url)
    try:
        page = requests.get(url,headers=headers,timeout=10)
        page.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("Oops: Something Else", err)
    
    return page


# Scrapes ticker name information from webpage
def scrape_name(symbol):
    page = crawler(symbol)
    soup = BeautifulSoup(page.content, 'html.parser')
    name = soup.find('h1', class_='D(ib) Fz(18px)')

    if name:
        return name.text


# Scrapes ticker price information from webpage
def scrape_price(symbol):
    page = crawler(symbol)
    soup = BeautifulSoup(page.content, 'html.parser')
    price = soup.find('fin-streamer', class_='Fw(b) Fz(36px) Mb(-4px) D(ib)')
    
    if price:
        return price.text


# Web scraper object
class Scraper:
    def __init__(self, stock_lst):
        self.stock_lst = stock_lst
        self.ticker_dict = {}
        self.price_que = Queue()
        self.name_que = Queue()


    # Populates object dictionary with ticker information
    def build_dict(self):
        time.sleep(2)
        price = self.price_que.get()
        name = self.name_que.get()
        if (len(self.ticker_dict) != len(self.stock_lst)) and (price != None and name != None):
            self.ticker_dict[name] = price


    # Runs multithreaded queues to web scrape and store ticker information
    def run(self):
        threads = []
        for symbol in self.stock_lst:
            tprice = Thread(target=lambda q, arg1: q.put(scrape_price(arg1)), 
                            args=(self.price_que, symbol))
            tname = Thread(target=lambda q, arg1: q.put(scrape_name(arg1)), 
                           args=(self.name_que, symbol))
            tprice.start()
            tname.start()
            threads.append(tprice)
            threads.append(tname)
            tque = Thread(target=self.build_dict)
            tque.start()
            threads.append(tque)
        for thread in threads:
            thread.join()


# Initial web app page
@app.route('/')
def index():
    return render_template('index.html',**locals())


# Loads page for submitted ticker symbols
@app.route('/', methods=['GET','POST'])
def form_post():
    if request.method == "POST":
        text = request.form['text']
        lst = text.split(",")
        scraper = Scraper(lst)
        scraper.run()
        data = scraper.ticker_dict
        print(data)

    return render_template('result.html', data=data)


if __name__ == '__main__':
    app.run(debug=True)