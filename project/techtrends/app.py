import sqlite3

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort
import logging
import sys

connection_count = 0
logger = logging.getLogger('techtrends')
log_level=logging.DEBUG
log_format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
log_stdout_handler=logging.StreamHandler(sys.stdout)
log_stderr_handler=logging.StreamHandler(sys.stderr)
log_handlers= [log_stdout_handler, log_stderr_handler]
logging.basicConfig(level=log_level, format=log_format, handlers=log_handlers)
# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    global connection_count
    connection_count += 1
    connection.row_factory = sqlite3.Row
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'
#app.logger.propagate=False
#logger.propagate=False

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define the healthz endpoint 
@app.route('/healthz')
def healthcheck():
    response = app.response_class(
            response=json.dumps({"result":"OK - healthy"}),
            status=200,
            mimetype='application/json'
    )
    return response

# Define the metrics endpoint
@app.route('/metrics')
def metrics():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT COUNT(*) FROM posts')
    results = cursor.fetchone()
    posts = results[0]
    response = app.response_class(
            response=json.dumps({"db_connection_count":connection_count, "post_count":posts}),
            status=200,
            mimetype='application/json'
    )
    return response

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      logger.info('Non-existing article retrive attempted')
      return render_template('404.html'), 404
    else:
      logger.info('Article retrieved: %s', post['title'])
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    logger.info('About Us page retrieved')
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            logger.info('New article created: %s', title)
            return redirect(url_for('index'))

    return render_template('create.html')

# start the application on port 3111
if __name__ == "__main__":
   app.run(host='0.0.0.0', port='3111')
