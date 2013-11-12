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
	SELECT e.created, e.title, c.content
		FROM elements e
		INNER JOIN toc t ON e.id = t.element_id
		INNER JOIN contexts c ON t.id = c.toc_id
		WHERE t.name = 'main' AND c.context_type = 1
	'''

one_page = '''
	SELECT e.created, e.title, c.content 
		FROM elements e
		INNER JOIN toc t ON e.id = t.element_id
		INNER JOIN contexts c ON t.id = c.toc_id
		WHERE t.name = 'main' AND e.title = '$what'
	'''

toc_insert = '''
	INSERT INTO toc (element_id, ordinal, name) VALUES
	'''

context_insert = '''
	INSERT INTO contexts (toc_id, context_type, content) VALUES
	'''