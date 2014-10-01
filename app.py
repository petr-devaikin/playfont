from flask import Flask, render_template, request, url_for
import requests
import bs4
import urlparse
import random

app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('application.cfg', silent=True)

def get_all_fonts():
    url = r'https://www.googleapis.com/webfonts/v1/webfonts?fields=items(family%2Csubsets)&key=' + \
        app.config['GOOGLE_KEY']
    r = requests.get(url)
    return [ f['family'] for f in r.json()['items'] if 'cyrillic' in f['subsets'] ]

@app.route('/')
def index():
    url = request.args.get('url', '')
    if url:
        if url[:5] != 'http:' and url[:6] != 'https:':
            url = 'http://' + url

    return render_template('index.html', url=url, fonts=get_all_fonts())

def get_random_style(fonts):
    result = ''
    result += '; font-family: ' + random.choice(fonts)
    result += '; font-weight: ' + random.choice(('normal', 'bold', 'bolder', 'lighter'))
    result += '; font-style: ' + random.choice(('normal', 'italic'))
    result += '; font-style: ' + random.choice(('normal', 'italic'))
    result += '; font-size: ' + random.choice(('small', 'medium', 'large'))
    result += '; text-shadow: 4px 4px 4px #aaa;'
    return result

@app.route('/render')
def render():
    fonts = get_all_fonts()

    url = request.args.get('url', None)
    if url != None:
        print url
        r = requests.get(url)
        print r.status_code

        soup = bs4.BeautifulSoup(r.content)
        
        def true_url(attr, render_url=False):
            def change_el(el):
                try:
                    el[attr] = urlparse.urljoin(url, el[attr])
                    if render_url:
                        el[attr] = url_for('.index', url=el[attr])
                        el['style'] = el.get('style', '') + get_random_style(fonts)
                except KeyError: pass
            return change_el

        map(true_url('href'), soup.find_all('link'))
        map(true_url('href', render_url=True), soup.find_all('a'))
        map(true_url('src'), soup.find_all('img'))
        map(true_url('src'), soup.find_all('script'))

        base_tag = soup.new_tag('base', target='_parent')
        head = soup.find('head')
        if head:
            head.append(base_tag)
        else:
            soup.append(base_tag)

        return soup.prettify()
    else:
        return "hello world!"


if __name__ == '__main__':
    app.config['DEBUG'] = True
    app.run()