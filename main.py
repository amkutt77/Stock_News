import requests
import datetime as dt
import smtplib

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"
PCT_THRESHOLD = .1

## STEP 1: Use https://www.alphavantage.co

# get stock data
av_api_key = "XXX"
av_api_endpoint = "https://www.alphavantage.co/query"
av_parameters = {
    "symbol": STOCK,
    "apikey": av_api_key,
    "function": "TIME_SERIES_DAILY",

}

# calculate the time deltas. We want yesterday's and the day before yesterday's
# also handle weekends: if it's the weekend, there won't be a new stock price, so change to Friday and Thursday for our stock prices.
current_time = dt.datetime.now()
# sunday
if current_time.weekday() == 6:
    t_minus_1 = current_time - dt.timedelta(days = 2)
    t_minus_2 = current_time - dt.timedelta(days = 3)
# Saturday
elif current_time.weekday() == 5:
    t_minus_1 = current_time - dt.timedelta(days = 1)
    t_minus_2 = current_time - dt.timedelta(days = 2)
# any weekday
else:
    t_minus_1 = current_time
    t_minus_2 = current_time - dt.timedelta(days = 1)

t_minus_1 = str(t_minus_1.date())
t_minus_2 = str(t_minus_2.date())

def get_stock_data():
    response = requests.get(url=av_api_endpoint, params=av_parameters)
    response.raise_for_status()
    stock_data = response.json()
    t_minus_1_price = float(stock_data["Time Series (Daily)"][t_minus_1]["4. close"])
    t_minus_2_price = float(stock_data["Time Series (Daily)"][t_minus_2]["4. close"])

    print(t_minus_1_price)
    print(t_minus_2_price)
    return [t_minus_1_price, t_minus_2_price]
    
# calculate percent different
stock_data = get_stock_data()
pct_diff = (stock_data[0]/stock_data[1]) - 1


## STEP 2: Use https://newsapi.org
# Get the first 3 news articles

def get_news_data():
    news_api_key = "XXX"
    news_api_endpoint = "https://newsapi.org/v2/everything"
    news_api_parameters = {
        "q": COMPANY_NAME,
        "from": t_minus_1,
        "sortBy": "popularity", # we will want the first 3 most popular ones
        "apiKey": news_api_key

    }
    response = requests.get(url=news_api_endpoint, params=news_api_parameters)
    response.raise_for_status()
    news_data = response.json()
    news = []
    for i in range(3): # 3 articles
        headline = str(news_data["articles"][i]["title"])
        description = str(news_data["articles"][i]["description"])
        news.append((headline,description))

    return news
    

    

## STEP 3: Use https://www.twilio.com. Originally was using Twilio, but now sending email instead. Don't want to waste free trial balance
# Send a seperate message with the percentage change and each article's title and description to your phone number. 

def send_email(headline, description):
    my_email = "amkutt77@gmail.com"
    password = "XXX"
    with smtplib.SMTP('smtp.gmail.com', 587) as connection:
        connection.starttls() 
        connection.login(user = my_email, password= password)
        message = f'''Subject: {COMPANY_NAME} CHANGED BY MORE THAN {PCT_THRESHOLD* 100}%!
        \n\n{headline}\n\n{description}
          
        '''.encode('utf-8')
        

        connection.sendmail(from_addr= my_email, to_addrs="amkutt77@gmail.com", msg = message)

# if the pct change is bigger than our threshold,
if abs(pct_diff) > PCT_THRESHOLD:
    print("getting news....") 
    news_data = get_news_data() # collect the news data
    for i in range(3):
        send_email(news_data[i][0], news_data[i][1]) # news_data is a list of tuples of: (headline, description)



