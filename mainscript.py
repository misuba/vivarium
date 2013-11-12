import psycopg2
from flask import Flask, url_for, render_template, request, flash, g
from string import Template
import vivarium_queries as vq

viv = Flask(__name__)

# postgres connection
# move this to a separate configuration file
conn_string = "host = 'localhost' dbname = 'vivarium' user='mtoth'"
conn = psycopg2.connect(conn_string)
cursor = conn.cursor()

@viv.route('/')
def welcome():
	all_pages_sql = vq.cleanSQL(vq.all_pages)
	cursor.execute(all_pages_sql)
	summaries = []
	# all_pages: SELECT e.created, e.title, c.content [. . .]
	records = cursor.fetchall()
	for entry in records:
		timestamp, title, content = entry
		summary = [timestamp, title, content]
		summaries.append(summary)
	return render_template('welcome.html', summaries=summaries)

@viv.route('/all')
def all_pages():
	cursor.execute(all_pages)

@viv.route('/new_page', methods=['GET','POST'])
def newpage():
	if request.method == 'GET':
		return render_template('newpage.html')

@viv.route('/page/<title>', methods=['GET','POST'])
def show_page(title):
	if request.method == 'GET':
		one_page = vq.cleanSQL(vq.one_page)
		one_page = Template(one_page)
		one_page_sql = one_page.substitute(what=title)
		cursor.execute(one_page_sql)
		summaries = []
		records = cursor.fetchall()
		for entry in records:
			timestamp, title, content = entry
			summary = [timestamp, title, content]
			summaries.append(summary)
		return render_template('one_page.html', summaries=summaries)
	else:
		return('POST method!')

@viv.route('/success', methods=['POST'])
def success():
	if request.method == 'POST':
		new_page = vq.cleanSQL(vq.new_page)
		new_page_sql = new_page.substitute
		cursor.execute(new_page_sql)
		db.commit()
		return redirect(url_for('show_page', id=request.form['id']))

if __name__ == "__main__":
	viv.run(debug = True)