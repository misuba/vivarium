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
	    	if str(value) in ['', ' ']:		# in case of no input
	    		pass
	    	else:
	    		form_dict[key] = str(value)
	form_dict.pop('form_id', None)			# remove form_id from dict
	return form_dict

all_pages = '''
	SELECT e.created, e.title
		FROM elements e
		INNER JOIN pages_to_contexts p ON p.page_id = e.id
		INNER JOIN contexts c ON c.id = p.context_id
	'''

one_page = '''
	SELECT e.created AS e_ts, e.title AS e_title, c.created AS c_ts, 
			c.title AS c_title, c.ordinal, c.content
		FROM elements e
		INNER JOIN pages_to_contexts p ON p.page_id = e.id
		INNER JOIN contexts c ON c.id = p.context_id
		WHERE e.title = '$what' 
		ORDER BY c.ordinal ASC 
	'''

context_insert = '''
	INSERT INTO contexts (toc_id, context_type, content) VALUES
	'''