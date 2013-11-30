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
			e_ts, e_title, c_ts, c_title, ordinal, content = entry
			element['title'] = e_title
			element['timestamp'] = e_ts.strftime('%m/%d/%Y, %I:%M:%S %p')
			contexts[ordinal] = [c_ts.strftime('%m/%d/%Y, %I:%M:%S %p'), c_title, content]
		return render_template('one_page.html', e = element, summaries=contexts)
	else:
		return('POST method!')

@viv.route('/success', methods=['GET','POST'])
def success():
	render_template('nope.html')
	# if request.method == 'GET':
	# 	render_template('nope.html')
	# else:
	# 	d = request.form
	# 	form_dict = {}
	# 	for key in d.keys():
	# 	    for value in d.getlist(key):
	# 	    	form_dict[key] = str(value)
	# 	render_template('simple.html')
	# form_dict.pop('form_id', None)			# remove form_id from dict
	# return form_dict
	# if form_id == 'add_page':
	# 	cleand = addPageSQL(f)
	# 	# s = str(cleand)
	# 	# return(s)
	# 	return redirect(url_for('all_pages'))
	# elif form_id == 'add_list':
		# cleand = addListSQL(f)
		# return(f)

if __name__ == "__main__":
	viv.run(debug = True)