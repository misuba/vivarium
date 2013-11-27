Vivarium
--------------------
Vivarium aspires to be a new kind of wiki: one in which every user can tune
their own view of each page, and one which prominently features visualiza-
tions of the page's "health" (defined as a function of views, updates, and 
more) as a way of coaxing users to maintain the wiki such that each page will
be discoverable and relevant.

It will begin as a single-user wiki, and multi-user functionality will be 
added in the future. Security, scalability, etc. are explicitly works in
progress.


Status
--------------------
Flask is now interacting with a Postgres backend to add and display pages.
I'm torn between adding lists or writing a link parser as my next step.


Basic Objects
--------------------
Spaces		:	Each space is a a distinct wiki document. It is possible to
				link between elements in different spaces, but the linking
				exhibits different behavior.
Elements	:	Each element is an individual item within a space. There are 
				four to choose from: pages, lists, timelines, and pearls.
Links		:	Hyperlinks between elements, with the same notation and 
				behavior as standard (i.e. Wikipedia) internal links.


Element Types: 
--------------------
Pages		:	This is a wiki page. It has the greatest number of features
				available, e.g. TOCs, contexts, windows, and embedded media.
				Its maximum size is (basically) unlimited.
Lists		:	A list is an ordered series of text items, of limited size,
				with or without toggled check boxes. The number of items
				allowed is (basically) unlimited. Links are permitted.
Timelines	:	A timeline is a list which includes 1-2 dates. Dates are
				allowed to be relative to other dates, e.g. "after X" or 
				"six months after X". Simultaneous items are allowed.
Pearls		:	A pearl is a small (text-only) item with no explicit title.
				Links are permitted but may not be the only content. It is
				the smallest and simplest of the types.


Future Element Types: 
-------------------------		
Extracts	:	Not implemented in this version! But when it IS implemented,
				an extract will be a text object similar to a page, with
				TOCs, contexts, and embedded media available. Unlike a page,
				there are two kinds of content within a TOC section and they
				will be permitted to have distinct contexts: a "source"
				content (e.g. text from a book) and "commentary" content 
				(e.g. your summary of the text). 
Archives	:	Not implemented in this version! But when it IS implemented,
				an archive will be an explicitly historical (and immutable)
				text and/or media object. It will otherwise have features
				similar to an extract, e.g. commentary content.


Page Features:
--------------------
TOC			:	An ordered series of headings for a single page element,
				which may be visible or invisible. If no TOCs are specified,
				there is still an (invisible) "main" TOC element so the page
				can have contexts enabled. All TOC headings besides "main"
				must contain content of some kind.
Contexts	:	This is a (perhaps unique?) feature of this wiki. A context
				is a distinct "type" of text contained within a TOC heading.
				In the case of a multi-user wiki, only the "main" context is
				shared with other users by default; all others are private by
				default. More information on contexts below.
Windows		:	An embedded context from a different page element, usually 
				"main". Unlike an internal link, it can be read immediately 
				and does not have to be clicked on. A window cannot be edited
				directly, but it can be removed, and it updates when the 
				context is updated on the original page.
Tags		:	Keywords which help you search for a given context or element, 
				with the same behavior as standard wiki tags.


Contexts:
--------------------------
The available contexts are renamable 

0 :	Main		:	The stuff you want to see all the time; default content.
1 :	Basics		:	Too low-level to want to see constantly, but useful from
					time to time.
2 :	Motivation	:	Why do you care about this? What is it good for?
3 :	Opinions	:	Personal feelings and opinions; editorial comments.
4 :	Social		:	What do other people say/think?
5 :	XCredit		:	Related papers, resources, spinoff ideas, etc.


A bit more about contexts:
----------------------------
A context is a specific category of text within a page, with its own revision
ID and distinct privacy and visibility setting. It's an optional feature
intended to give structure to a page and allow users to add subjective or 
personalized content that will be clearly delineated from the main 
informational content of the page. A brief example is shown below:


--> Page Title: ULYSSES
--> +---------------------------------------------
--> | Context: Motivations
--> | Revision ID: 3
--> | Visible: True
--> | 
--> | Research for book report due April 13
--> +---------------------------------------------
--> | Context: Main
--> | Revision ID: 12
--> | Visible: True
--> |
--> | This book describes a day in the life of Leopold Bloom [ ... ]
--> +---------------------------------------------
--> | Context: Opinions
--> | Revision ID: 4
--> | Visible: False
--> |
--> | Week Three: This book weighs on me like a curse.
--> +---------------------------------------------

Every TOC heading within a page has its own set of contexts; a page without
any user-added TOCs still has one "main" (invisible) TOC heading enabled. 
Using contexts gives you the following extra features:

	*	Browse motivations to determine whether a page is still relevant and
		worth maintaining.
	*	A page can contain snippets of "related" content rather than spinning
		off multiple stub-length pages that will be viewed much less
		frequently.
	*	Search for keywords on a context-specific basis, e.g. "(research IN
		Motivations) AND (CPU IN Main)"
	*	[Add more here]


SQL Schema:
--------------------------

USERS
======================================================================
| id | timestamp | name/nym | email | username  | password           |
+----+-----------+----------+-------+-----------+--------------------+
| pk | timestamp | varchar  | email | sha2 hash | salted pbkdf2 hash | 
======================================================================


PRIVILEGE_TYPES
===============
| id | name   |
+----+--------+
| pk | admin  |
|    | read   |
|    | write  |
|    | lock   |
|    | delete |
===============


USERS_TO_PRIVILEGES
=======================================================================
| id | user    | context    | privilege_type    | timestamp | active  |
+----+---------+------------+-------------------+-----------+---------+
| pk | user_id | context_id | privilege_type_id | timestamp | boolean |
=======================================================================


SPACES
============================
| id | created   | name    |
+----+-----------+---------+
| pk | timestamp | varchar |
============================


ELEMENT_TYPES
=================
| id | name     |
+----+----------+
| pk | page     |
|    | list     |
|    | timeline |
|    | pearl    |
=================


ELEMENTS
===================================================
| id | space    | created   | elem_type | title   |
+----+----------+-----------+-----------+---------+
| pk | space_id | timestamp | type_id   | varchar |
===================================================


TOC
===================================================
| id | element    | ordinal | name    | created   |
+----+------------+---------+---------+-----------+
| pk | element_id | 0       | varchar | timestamp |
===================================================


CONTEXT_TYPES
=============================
| id | ordinal | name       |
+----+---------+------------+
| pk | 0       | main       |
|    | 1       | subtitle   |
|    | 2       | abstract   |
|    | 3       | motivation |
|    | 4       | basics     |
|    | 5       | opinions   |
|    | 6       | social     |
|    | 7       | xcredit    |
=============================


CONTEXTS
=========================================================
| id | toc    | context_type    | created   | latest    |
+----+--------+-----------------+-----------+-----------+
| pk | toc_id | context_type_id | timestamp | timestamp |
=========================================================


REVISIONS
=========================================
| id | context    | created   | content |
+----+------------+-----------+---------+
| pk | context_id | timestamp | text    |
=========================================


MEDIA
======================
| id | link | object |
+----+------+--------+
| pk | text | blob   |
======================


