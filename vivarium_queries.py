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

element_info = '''
	SELECT e.created, e.title
		FROM elements e
		WHERE e.title = %s
	'''

context_info = '''
	SELECT c.id, c.ordinal, c.created, c.title, c.content
		FROM elements e
		INNER JOIN pages_to_contexts p ON p.page_id = e.id
		INNER JOIN contexts c ON c.id = p.context_id
		WHERE e.title = %s 
		ORDER BY c.ordinal ASC 
	'''

element_ordinals = '''
	SELECT c.id, c.ordinal
	FROM elements e
		INNER JOIN pages_to_contexts p ON p.page_id = e.id
		INNER JOIN contexts c ON c.id = p.context_id
		WHERE e.title = %s AND c.ordinal > 2
	'''

context_insert = '''
	INSERT INTO contexts (toc_id, context_type, content) VALUES
	'''
