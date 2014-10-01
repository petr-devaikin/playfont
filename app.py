from flask import Flask, render_template

app = Flask()

@app.route('/')
def index():
    get_logger().info('Hello!')
    return render_template('index')

if __name__ == '__main__':
    app.config['DEBUG'] = True
    app.run()