from flask import Flask, render_template, request, url_for
import requests
import bs4
import urlparse

app = Flask(__name__)

@app.route('/')
def index():
    url = request.args.get('url', None)
    return render_template('index.html', url=url)

@app.route('/render')
def render():
    url = request.args.get('url', None)
    print url
    if url != None:
        r = requests.get(url)
        print r.status_code

        soup = bs4.BeautifulSoup(r.content)
        
        def true_url(attr, render_url=False):
            def change_el(el):
                try:
                    el[attr] = urlparse.urljoin(url, el[attr])
                    if render_url:
                        el[attr] = url_for('.index', url=el[attr])
                        el['style'] = "font-size: 60px"
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
        return "hello"


if __name__ == '__main__':
    app.config['DEBUG'] = True
    app.run()