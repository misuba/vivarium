# gets rid of newlines and tabs in SQL queries
def cleanSQL(q):
	mapping = [('\n', ' '), ('\t', '')]
	for k, v in mapping:
		step1 = q.replace(k, v)
		step2 = step1.strip()
	return step2

all_pages = '''
	SELECT e.created, e.title, c.content 
		FROM elements e
		INNER JOIN toc t ON e.id = t.element_id
		INNER JOIN contexts c ON t.id = c.toc_id
		WHERE t.name = 'main'
	'''

one_page = '''
	SELECT e.created, e.title, c.content 
		FROM elements e
		INNER JOIN toc t ON e.id = t.element_id
		INNER JOIN contexts c ON t.id = c.toc_id
		WHERE t.name = 'main' AND e.title = '$what'
	'''

element_insert = '''
	INSERT INTO elements (space_id, element_type, title) VALUES
	'''

toc_insert = '''
	INSERT INTO toc (element_id, ordinal, name) VALUES
	'''

context_insert = '''
	INSERT INTO contexts (toc_id, context_type, content) VALUES
	'''