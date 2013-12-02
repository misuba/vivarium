# gets rid of newlines and tabs in SQL queries
def cleanSQL(q):
	mapping = [('\n', ' '), ('\t', '')]
	for k, v in mapping:
		step1 = q.replace(k, v)
		step2 = step1.strip()
	return step2

# takes form input, returns a clean dictionary for Template substitutions
def cleanFormInput(d):
	form_dict = {}
	for key in d.keys():
	    for value in d.getlist(key):
	    	# in all fields except content, no input means no change;
	    	# in case of content, it may mean everything has been deleted 
	    	if value.encode('utf-8') in ['', ' '] and key != 'content':
	    		pass
	    	else:
	    		form_dict[key] = value.encode('utf-8')
	return form_dict

def updateContext(clean):
	if len(clean) < 2:
		return clean
	elif len(clean) == 2:	
	# this is a content-only update
		c_id = clean.pop('id', None)
		SQLstring = 'UPDATE contexts SET {0} = "{1}" WHERE id = {2}'
		updateSQL = SQLstring.format(clean.keys()[0], clean.values()[0], c_id)
		return updateSQL
	else:
	# this is a content + title update
		c_id = clean.pop('id', None)
		d_keys = tuple(clean.keys())
		keylist = reduce(lambda x, y: x + ', ' + y, d_keys)
		vals = []
		for item in d_keys:
			vals.append(clean[item])
		vals = tuple(vals)
		updateSQL = "UPDATE contexts SET ({0}) = {1} WHERE id = {2}".format(keylist, vals, c_id)
		return updateSQL

all_pages = '''
	SELECT e.created, e.title
		FROM elements e
	'''

all_subtitles = '''
	SELECT e.title, c.content
		FROM elements e
		INNER JOIN pages_to_contexts p ON p.page_id = e.id
		INNER JOIN contexts c ON c.id = p.context_id
		WHERE c.title = 'subtitle'
	'''

one_page = '''
	SELECT e.created AS e_ts, e.title AS e_title, c.created AS c_ts, 
			c.title AS c_title, c.ordinal, c.content, c.id
		FROM elements e
		INNER JOIN pages_to_contexts p ON p.page_id = e.id
		INNER JOIN contexts c ON c.id = p.context_id
		WHERE e.title = '$what' 
		ORDER BY c.ordinal ASC 
	'''

context_insert = '''
	INSERT INTO contexts (toc_id, context_type, content) VALUES
	'''
