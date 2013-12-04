import psycopg2, re, datetime
from flask import Flask, url_for, render_template, request, redirect
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
def hasContentChanged(clean, context_id):
	''' returns True if new content differs from old content, and False otherwise'''
	newContent = clean['content'].strip()
	oldContentSQL = "SELECT content FROM contexts WHERE id = %s"
	cursor.execute(oldContentSQL, [context_id])
	oldContent = cursor.fetchone()[0].strip()	# don't count trailing space as an edit
	if oldContent == newContent:
		return False
	else:
		return True

def process_links(match):
	''' used within a regex substitution to convert [[links]] to html '''
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

# called by context_data(title)
def process_text(s):
	''' decodes text and sends [[links]] through regex substitution '''
	decoded = s.decode('utf-8')
	# convert [[links]] into real links
	match = r"\[\[(.+?)\]\]"
	linked = re.sub(match, process_links, decoded)
	return [linked, decoded]

def context_data(title):
	''' returns a dictionary of context data by title '''
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

def get_element_id(title):
	SQLstring = '''SELECT id FROM elements WHERE title = %s'''
	cursor.execute(SQLstring, [title])
	element_id = cursor.fetchone()[0]
	return element_id

def element_data(title):
	''' returns a dictionary of element data by title '''
	cursor.execute(vq.element_info, [title])
	records = cursor.fetchone()
	element_ts = records[0].strftime('%m/%d/%Y, %I:%M:%S %p')
	element_title = records[1]
	return {'timestamp': element_ts, 'title': element_title}

def edit_context(clean):
	e_title = clean.pop('e_title', None)
	c_id = clean.pop('id', None)
	if 'title' in clean.keys():
		updateSQL = '''UPDATE contexts SET title = %(title)s WHERE id = {0}'''.format(c_id)
		cursor.execute(updateSQL, clean)
		conn.commit()
	# check to see if content has changed
	r = hasContentChanged(clean, c_id)
	if r == True:
		updateSQL = '''UPDATE contexts SET content = %(content)s WHERE id = {0}'''.format(c_id)
		cursor.execute(updateSQL, clean)
		conn.commit()
	else:
		# nothing has changed
		return e_title
	return e_title

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
	if request.method == 'GET':
		e = element_data(title)
		c = context_data(title)
		return render_template('add_context.html', e = e, summaries = c)

@viv.route('/track/<id>')
def track(id):
	now = datetime.datetime.now()
	new_id = int(id)
	SQLstring = '''select r.created from revisions r inner join pages_to_contexts p 
		ON p.context_id = r.context_id WHERE p.page_id = %s'''
	cursor.execute(SQLstring, [new_id])
	records = cursor.fetchall()
	comp = [(now - x[0]).days for x in records]
	result = process_weighted(comp)
	return str(id) + ": " + str(result)

def process_weighted(comp):
	comp2 = [1 if x == 0 else x for x in comp]
	comp3 = [((366.0-x)/365) for x in comp2]
	return sum(comp3)

@viv.route('/success', methods=['GET','POST'])
def success():
	if request.method == 'GET':
		render_template('nope.html')
	else:
		input = request.form
		clean = vq.cleanFormInput(input)
		form_name = clean.pop('form_name', None)
		if form_name == 'edit_context':
			# an existing context has been edited:
			e_title = edit_context(clean)
			return redirect(url_for('show_page', title=e_title))
		elif form_name == 'add_context':
			# a new context has been added to an existing page:
			e_title = clean['e_title']
			clean['ordinal'] = process_ordinals(clean)
			clean['content'] = clean['content'].decode('utf-8')
			# RETURNING ID is FUCKING BRILLIANT
			SQLstring = '''INSERT INTO contexts (ordinal, content, title) VALUES
				(%(ordinal)s, %(content)s, %(title)s) RETURNING id'''	# <--- HUZZAH
			cursor.execute(SQLstring, clean)
			conn.commit()
			# Now add a row in pages_to_contexts to connect the context and element
			context_id = cursor.fetchone()[0]
			element_id = get_element_id(e_title)
			connect_context(context_id, element_id)
			return redirect(url_for('show_page', title=e_title))

def connect_context(context_id, element_id):
	SQLstring = '''INSERT INTO pages_to_contexts (context_id, page_id) VALUES (%s, %s)'''
	cursor.execute(SQLstring, [context_id, element_id])
	conn.commit()

def process_ordinals(d):
	''' Evaluate a newly submitted ordinal and change other ordinals if necessary '''
	new_ordinal = int(d['ordinal']) + 2		# to account for subtitle and abstract
	e_title = d['e_title']
	# retrieve ordinals for all other contexts attached to this page
	cursor.execute(vq.element_ordinals, [e_title])
	records = cursor.fetchall()
	ords = [x[1] for x in records]
	# Return list of ordinals that will be affected
	if new_ordinal < max(ords):
		affected = [{'id': x[0], 'ordinal': x[1] + 1} for x in records if x[1] >= new_ordinal]
		for item in affected:
			increment = "UPDATE contexts SET ordinal = %(ordinal)s WHERE id = %(id)s"
			cursor.execute(increment, item)
			conn.commit()
		return new_ordinal
	else:
	# Else: the context gets added to the end
		new_ordinal = max(ords) + 1
		return new_ordinal


if __name__ == "__main__":
	viv.run(debug = True)