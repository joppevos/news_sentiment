import requests
from bs4 import BeautifulSoup
import pprint
import json
from datetime import date, timedelta
import sqlite3


MY_API_KEY= 'b6803cd9-9551-4046-a095-4bafc52c77cd'

API_ENDPOINT = 'http://content.guardianapis.com/search'
my_params = {
    'from-date': "",
    'to-date': "",
    'order-by': "newest",
    'show-fields': 'all',
    'page-size': 50,
    'api-key': MY_API_KEY
}

def get_articles():
    """
    scrapes num pages of given time span
    """

    conn, c = db_connect()

    start_date = date(2018, 2, 24)
    end_date = date(2019,2, 24)
    dayrange = range((end_date - start_date).days + 1)

    for day in dayrange:
        end_date = end_date + timedelta(days= - 1)
        my_params['from-date'] = start_date
        my_params['to-date'] = end_date

        resp = requests.get(API_ENDPOINT, my_params)
        data = resp.json()

        all_results = []
        all_results.extend(data['response']['results'])
        columns = ['bodyText', 'byline', 'headline', 'publication' ]

        for result in all_results:
            try:
                page = {col: result['fields'][col] for col in columns}
            except KeyError:
                continue
            page['id'] = result['id']
            page['end_date'] = start_date.strftime('%d-%m-%Y')
            db_commit(conn, c, page)


def db_connect():
    conn = sqlite3.connect('news_table.db')
    c = conn.cursor()
    # c.execute("""DROP TABLE articles""")
    try:
        c.execute("""CREATE TABLE articles(
                ID PRIMARY KEY,
                TITLE text,
                TEXT text,
                AUTHOR text,
                TIME,
                SOURCE text
                );
                """)
    except sqlite3.OperationalError:
        print('table already exists')
    return conn, c


def db_commit(conn, c, page):

    try:
        c.execute("INSERT INTO articles VALUES (:ID, :TITLE, :TEXT, :AUTHOR, :TIME, :SOURCE)",
                  {'ID': page['id'], 'TITLE': page['headline'], 'TEXT': page['bodyText'],
                   'AUTHOR': page['byline'], 'TIME': page['start_date'], 'SOURCE': page['publication']})

        conn.commit()
        print('new page added')
    except sqlite3.IntegrityError:
        print('UNIQUE constraint failed')
        pass


get_articles()


