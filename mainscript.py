import psycopg2, re
from flask import Flask, url_for, render_template, request, redirect
from string import Template
import vivarium_queries as vq

viv = Flask(__name__)
viv.jinja_options = viv.jinja_options.copy()
# the 'with' extension creates a nested scope for context editing
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
	oldContentSQL = "SELECT content FROM contexts WHERE id = %s"
	cursor.execute(oldContentSQL, [context_id])
	oldContent = cursor.fetchone()[0].strip()	# don't count trailing space as an edit
	if oldContent == newContent:
		return False
	else:
		return True

# Page rendering functions:
#
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
	return render_template('jscript.html')
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

def process_links(match):
	word = match.group(1)
	# get list of existing titles
	cursor.execute("SELECT title FROM elements")
	titles = cursor.fetchall()
	title_list = [x[0] for x in titles]
	if word in title_list:
		# link to existing page
		url_stem = 'http://localhost:5000'
		return "<a href=\"" + url_stem + "/page/" + word + "\">" + word + "</a>"
	else:
		# change text color as a warning
		return "<span style='color: #b58900;'}>[[" + word + "]]</span>"

def process_text(s):
	decoded = s.decode('utf-8')
	# convert [[links]] into real links
	match = r"\[\[(.+?)\]\]"
	linked = re.sub(match, process_links, decoded)
	return [linked, decoded]

def context_data(title):
	cursor.execute(vq.context_info, [title])
	records = cursor.fetchall()
	c = {}
	for entry in records:
		id, ordinal, created, title, rawcontent = entry
		# data processing/formatting
		created = created.strftime('%m/%d/%Y, %I:%M:%S %p')
		content = process_text(rawcontent)
		c[ordinal] = [created, title, content[0], content[1], id]
	return c

def element_data(title):
	cursor.execute(vq.element_info, [title])
	records = cursor.fetchone()
	element_ts = records[0].strftime('%m/%d/%Y, %I:%M:%S %p')
	element_title = records[1]
	return {'timestamp': element_ts, 'title': element_title}

@viv.route('/page/<title>', methods=['GET','POST'])
def show_page(title):
	if request.method == 'GET':
		e = element_data(title)
		c = context_data(title)
		return render_template('one_page.html', e = e, summaries=c)
	else:
		return('POST method!')

@viv.route('/page/<title>/add')
def add_context(title):
	return(title)

@viv.route('/success', methods=['GET','POST'])
def success():
	if request.method == 'GET':
		render_template('nope.html')
	else:
		input = request.form
		clean = vq.cleanFormInput(input)
		e_title = clean.pop('e_title', None)
		r = hasContentChanged(clean)
		if r == True:
			c_id = clean.pop('id', None)
			if clean.keys() == ['content']:	
				# this is a content-only update
				updateSQL = '''UPDATE contexts SET content = %(content)s WHERE id = {0}'''.format(c_id)
				cursor.execute(updateSQL, clean)
				conn.commit()
				return redirect(url_for('show_page', title=e_title))
			elif 'title' in clean.keys():
				# this is a content + title update
				updateSQL = '''UPDATE contexts SET (content, title) = (%(content)s, %(title)s) WHERE id = {0}'''.format(c_id)
				cursor.execute(updateSQL, clean)
				conn.commit()
				return redirect(url_for('show_page', title=e_title))
		else:
			if 'title' in clean.keys():
				# this is a title-only update
				updateSQL = '''UPDATE contexts SET title = %(title)s WHERE id = {0}'''.format(c_id)
				cursor.execute(updateSQL, clean)
				conn.commit()
				return redirect(url_for('show_page', title=e_title))
			else:
				# nothing has changed; redirect back to page
				return redirect(url_for('show_page', title=e_title))


if __name__ == "__main__":
	viv.run(debug = True)