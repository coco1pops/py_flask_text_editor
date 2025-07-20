from flask import Flask

from editor import pages

def create_app():
    app = Flask(__name__)

    app.register_blueprint(pages.bp)
    return app
"""
from flask import Flask, render_template, request, jsonify
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    data = request.get_json() # retrieve the data sent from JavaScript
    # process the data using Python code
    result = data['value'] * 2
    return jsonify(result=result) # return the result to JavaScript

@app.route('/story_list')
def story_list():
    return render_template('story_list.html')

if __name__ == '__main__':
    app.run(debug=True)

"""