from flask import Flask, render_template, request, url_for
import requests
import bs4
import urlparse
import random

app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('application.cfg', silent=True)


font_effects = ('anaglyph', 'brick-sign', 'canvas-print', 'crackle', 'decaying', 'destruction', 
    'distressed', 'distressed-wood', 'emboss', 'fire', 'fire-animation', 'fragile', 'grass',
    'font-effect-ice', 'font-effect-mitosis', 'font-effect-neon', 'font-effect-outline',
    'putting-green', 'scuffed-steel', 'shadow-multiple', 'font-effect-splintered',
    'font-effect-static', 'stonewash', '3d', '3d-float', 'vintage')


def get_all_fonts():
    url = r'https://www.googleapis.com/webfonts/v1/webfonts?fields=items(family%2Csubsets)&key='
    url += app.config['GOOGLE_KEY']
    r = requests.get(url)
    return [ f['family'] for f in r.json()['items'] if 'cyrillic' in f['subsets'] ]


def get_random_style(fonts):
    result = ''
    result += '; font-family: ' + random.choice(fonts)
    #result += '; font-weight: ' + random.choice(('normal', 'bold', 'bolder', 'lighter'))
    #result += '; font-style: ' + random.choice(('normal', 'italic'))
    #result += '; font-size: ' + random.choice(('small', 'medium', 'large'))
    # result += '; text-shadow: 4px 4px 4px #aaa;'
    return result


def explore_tree(soup, root, fonts):
    for child in root.children:
        if type(child) == bs4.Tag:
            explore_tree(soup, child, fonts)
        elif type(child) == bs4.NavigableString:
            new_tag = soup.new_tag('span', style=get_random_style(fonts))
            #new_tag['class'] = 'font-effect-' + random.choice(font_effects)
            new_tag.append(child.string[:])
            child.replace_with(new_tag)


@app.route('/')
def index():
    url = request.args.get('url', '')
    if url:
        if url[:5] != 'http:' and url[:6] != 'https:':
            url = 'http://' + url

    return render_template('index.html', url=url)


@app.route('/render')
def render():
    fonts = get_all_fonts()

    url = request.args.get('url', None)
    if url != None:
        try:
            r = requests.get(url)
        except requests.ConnectionError:
            return render_template('error.html')
        else:
            soup = bs4.BeautifulSoup(r.content)
            
            def true_url(attr, render_url=False):
                def change_el(el):
                    try:
                        el[attr] = urlparse.urljoin(url, el[attr])
                        if render_url:
                            el[attr] = url_for('.index', url=el[attr])
                    except KeyError: pass
                return change_el

            map(true_url('href'), soup.find_all('link'))
            map(true_url('href', render_url=True), soup.find_all('a'))
            map(true_url('src'), soup.find_all('img'))
            map(true_url('src'), soup.find_all('script'))

            body = soup.find('body')
            if not body:
                body = soup

            explore_tree(soup, body, fonts)
            
            base_tag = soup.new_tag('base', target='_parent')
            font_link = soup.new_tag('link', rel='stylesheet', type='text/css',
                href='http://fonts.googleapis.com/css?family={0}&effect={1}'.format('|'.join(fonts), '|'.join(font_effects)))

            head = soup.find('head')
            if not head:
                head = soup
            head.append(base_tag)
            head.append(font_link)
            
            return soup.prettify()
    else:
        return render_template('error.html')


if __name__ == '__main__':
    app.config['DEBUG'] = True
    app.run()