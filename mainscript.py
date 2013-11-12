import psycopg2
from flask import Flask, url_for, render_template, request, redirect, flash, g
from string import Template
import vivarium_queries as vq

viv = Flask(__name__)

# postgres connection
# move this to a separate configuration file
conn_string = "host = 'localhost' dbname = 'vivarium' user='mtoth'"
conn = psycopg2.connect(conn_string)
cursor = conn.cursor()

# takes form input, returns a list of SQL insert statements
def addPageSQL(d):
	#
	# Step 1: convert form input into Template-ready dictionary
	# ---------------------------------------------------------
	clean = vq.cleanFormInput(d)
	element_title = clean.pop('title')	# get title of element
	element_title = "'" + element_title + "'"
	# to do: change hardcoded space_id
	# to do: change hardcoded element_type
	element_sql = 'INSERT INTO elements (space_id, element_type, title) VALUES (1, 1, {0})'.format(element_title)
	cursor.execute(element_sql)
	conn.commit()
	#
	# Step 2: fetch id from the newly created element, for use in toc insert SQL
	# ---------------------------------------------------------
	get_element_id = 'SELECT id FROM elements WHERE title = {0}'.format(element_title)
	cursor.execute(get_element_id)
	# can we tighten this up at all? 
	element_id = cursor.fetchall()
	element_id = [i[0] for i in element_id]
	element_id = element_id[0]
	# now we create the main toc element; it can be edited later
	toc_sql = "INSERT INTO toc (element_id, ordinal, name) VALUES ({0}, 0, 'main')".format(element_id)
	cursor.execute(toc_sql)
	conn.commit()
	#
	# Step 3: create all context elements tied to the main toc element
	# ---------------------------------------------------------
	get_toc_id = 'SELECT id FROM toc WHERE element_id = {0}'.format(element_id)
	cursor.execute(get_toc_id)
	toc_id = cursor.fetchall()
	toc_id = [i[0] for i in toc_id]
	toc_id = toc_id[0]
	context_sql = "INSERT INTO contexts (toc_id, context_type, content) VALUES "
	c = ''
	for item in clean.keys():
		context_loop = toc_id, int(item), clean[item]
		c = c + str(context_loop) + ', '
	c = c[:-2]
	context_sql = context_sql + c
	cursor.execute(context_sql)
	conn.commit()


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
	all_pages_sql = vq.cleanSQL(vq.all_pages)
	cursor.execute(all_pages_sql)
	summaries = []
	records = cursor.fetchall()
	for entry in records:
		timestamp, title, content = entry
		summary = [timestamp, title, content]
		summaries.append(summary)
	return render_template('all_pages.html', summaries=summaries)

@viv.route('/new_page')
def newpage():
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
		f = request.form
		form_id = str(f['form_id'])
		if form_id == 'add_page':
			addPageSQL(f)
			return redirect(url_for('all_pages'))
		else:
			return('You cannot yet POST a form that is not add_page')
		# new_page = vq.cleanSQL(vq.new_page)
		# new_page_sql = new_page.substitute
		# cursor.execute(new_page_sql)
		# db.commit()
		# return redirect(url_for('show_page', title=request.form['title']))

if __name__ == "__main__":
	viv.run(debug = True)