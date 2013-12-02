import psycopg2
from flask import Flask, url_for, render_template, request, redirect, flash, g
from string import Template
import vivarium_queries as vq

viv = Flask(__name__)
viv.jinja_options = viv.jinja_options.copy()
viv.jinja_options['extensions'].append('jinja2.ext.with_')

# postgres connection
# move this to a separate configuration file
conn_string = "host = 'localhost' dbname = 'vivarium' user='mtoth'"
conn = psycopg2.connect(conn_string)
cursor = conn.cursor()

# Housekeeping functions with database queries:
#
def hasContentChanged(clean):
	''' returns True if new content differs from old content, and False otherwise'''
	context_id = clean['id']
	newContent = clean['content'].strip()
	oldContentSQL = "SELECT content FROM contexts WHERE id = {0}".format(context_id)
	cursor.execute(oldContentSQL)
	oldContent = cursor.fetchone()[0].strip()	# don't count trailing space as an edit
	if oldContent == newContent:
		return False
	else:
		return True

@viv.route('/')
def welcome():
	all_pages_sql = vq.cleanSQL(vq.all_pages)
	cursor.execute(all_pages_sql)
	page_records = cursor.fetchall()
	all_subtitles_sql = vq.cleanSQL(vq.all_subtitles)
	cursor.execute(all_subtitles_sql)
	subtitle_records = cursor.fetchall()
	subtitles = {}
	summaries = []
	for entry in subtitle_records:
		e_title, subtitle = entry
		subtitles[e_title] = subtitle
	for entry in page_records:
		created, title = entry
		if title in subtitles.keys():
			sub = subtitles[title]
			summary = [created.strftime('%m/%d/%Y, %I:%M:%S %p'), title, sub]
			summaries.append(summary)
		else:
			summary = [created.strftime('%m/%d/%Y, %I:%M:%S %p'), title]
			summaries.append(summary)
	return render_template('welcome.html', summaries=summaries)

@viv.route('/jscript')
def java():
	# return url_for('static', filename='data.tsv')
	return("This isn't ready for prime time yet. Sorry!")

@viv.route('/all')
def all_pages():
	all_pages_sql = vq.cleanSQL(vq.all_pages)
	cursor.execute(all_pages_sql)
	summaries = []
	records = cursor.fetchall()
	for entry in records:
		timestamp, title = entry
		summary = [timestamp, title]
		summaries.append(summary)
	return render_template('all_pages.html', summaries=summaries)

@viv.route('/new_page')
def newpage():
	return render_template('newpage.html')

@viv.route('/new_list')
def newlist():
	return render_template('newlist.html')

@viv.route('/edit/<title>', methods=['GET','POST'])
def edit_context(title):
	return render_template('nope.html')

@viv.route('/page/<title>', methods=['GET','POST'])
def show_page(title):
	if request.method == 'GET':
		one_page = vq.cleanSQL(vq.one_page)
		one_page = Template(one_page)
		one_page_sql = one_page.substitute(what=title)
		cursor.execute(one_page_sql)
		element = {}
		contexts = {}
		records = cursor.fetchall()
		for entry in records:
			e_ts, e_title, c_ts, c_title, ordinal, content, id = entry
			content = content.decode('utf-8')
			element['title'] = e_title
			element['timestamp'] = e_ts.strftime('%m/%d/%Y, %I:%M:%S %p')
			contexts[ordinal] = [c_ts.strftime('%m/%d/%Y, %I:%M:%S %p'), c_title, content, id]
		return render_template('one_page.html', e = element, summaries=contexts)
	else:
		return('POST method!')

@viv.route('/success', methods=['GET','POST'])
def success():
	if request.method == 'GET':
		render_template('nope.html')
	else:
		input = request.form
		clean = vq.cleanFormInput(input)
		e_title = clean.pop('e_title', None)
		r = hasContentChanged(clean)
		if r == "yes":
			updateSQL = vq.updateContext(clean)
			cursor.execute(updateSQL)
			conn.commit()
			return redirect(url_for('show_page', title=e_title))
		else:
			if 'title' in clean.keys():
				sqlString = vq.updateContext(clean)
				cursor.execute(sqlString)
				conn.commit()
				return redirect(url_for('show_page', title=e_title))
			else:
				return redirect(url_for('show_page', title=e_title))


if __name__ == "__main__":
	viv.run(debug = True)