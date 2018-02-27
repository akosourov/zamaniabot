from flask import Flask, request, render_template
from bs4 import BeautifulSoup
import urllib.request
import urllib.error
import urllib.parse

import config


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI


from bot import bot, process_update
from models import User, FeedBack


@app.route('/')
def index():
    return '<h1>Hello world</h2>'


@app.route('/set_webhook', methods=['GET', 'POST'])
def set_webhook():
    with open(config.cert_path, 'rb') as crt:
        s = bot.set_webhook(config.webhook_url, certificate=crt)
    if s:
        print(s)
        return 'Webhook setup ok'
    else:
        return 'Webhook setup failed'


@app.route('/delete_webhook', methods=['GET', 'POST'])
def delete_webhook():
    res = bot.delete_webhook()
    if res:
        return 'Webhook was deleted'
    else:
        return 'Fail'


@app.route('/{}'.format(config.bot_token), methods=['GET', 'POST'])
def hook():
    body = request.get_json(force=True)
    process_update(body)
    return 'ok'


@app.route('/news')
def fetch_news():
    try:
        resp = urllib.request.urlopen(config.news_page_url)
    except urllib.error.URLError as exc:
        # return error
        raise exc

    html_text = resp.read()
    resp.close()

    def get_news_item_data(news_div):
        title = news_div.find('h4')
        title = title.text if title else ''
        content = news_div.find('p', class_='zm-mcschedule-desc')
        content = content.text if content else ''
        img = news_div.find('img')
        img_url = ''
        if img:
            img_url = urllib.parse.urljoin(config.site_url, img['src'])
        details = news_div.find('a', class_='zm-btn-previous')
        details_url = ''
        if details:
            details_url = urllib.parse.urljoin(config.site_url, details['href'])

        return {'title': title, 'content': content, 'img_url': img_url,
                'details_url': details_url}

    html_doc = BeautifulSoup(html_text, 'html.parser')
    news_container = html_doc.find_all('div', class_='zm-row-box-news')
    news_data = [get_news_item_data(div) for div in news_container]
    return render_template('news.html', news_data=news_data)


@app.route('/users')
def users_list():
    users = User.query.all()
    return render_template('users.html', users=users)


@app.route('/feedback')
def feedback_list():
    feedbacks = FeedBack.query.all()
    return render_template('feedbacks.html', feedbacks=feedbacks)
