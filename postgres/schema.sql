-- Users
create table users (
	id serial primary key,
	created timestamp not null default now(),
	email varchar(100) not null,
	name varchar(200) default 'Username'
);

-- Each space is a distinct wiki document
create table spaces (
	id serial primary key,
	created timestamp not null default now(),
	title varchar(100) not null CONSTRAINT unique_title UNIQUE,
);

-- Elements are allowed to be: pages, lists, timelines, or pearls
-- NOTE: this table has already been created

create table element_types (
	id serial primary key,
	type_name varchar(20) not null
);

INSERT INTO element_types (id, type_name) VALUES 
	(1, 'page'),
	(2, 'list'),
	(3, 'timeline'),
	(4, 'pearl');

-- The elements table maps individual elements (pages, lists, etc.) to spaces
create table elements (
	id serial primary key,
	created timestamp not null default now(),
	space_id REFERENCES spaces ON DELETE CASCADE,
	element_type REFERENCES element_types ON DELETE RESTRICT,
	title varchar(100) not null,
	-- latest REFERENCES element_revisions	-- table not created yet
);

-- TOCs only apply to page elements 
create table toc (
	id serial primary key,
	created timestamp not null default now(),
	element_id REFERENCES elements ON DELETE CASCADE,
	element_type REFERENCES elements(element_type),
	order integer not null,
	name varchar(500),
	CONSTRAINT must_be_page CHECK (element_type = 1)
);

-- There are currently 8 context types available
create table context_types (
	id serial primary key,
	ordinal integer unique not null,
	type_name varchar(20) not null
);

INSERT INTO context_types (id, ordinal, type_name) VALUES
	(1, 0, 'main'),
	(2, 1, 'abstract'),
	(3, 2, 'summary'),
	(4, 3, 'basics'),
	(5, 4, 'motivation'),
	(6, 5, 'opinions'),
	(7, 6, 'social'),
	(8, 7, 'xcredit');

-- There are contexts for most TOC elements in a page
create table contexts (
	id serial primary key,
	created timestamp not null default now(),
	toc_id REFERENCES toc ON DELETE CASCADE,
	context_type REFERENCES context_types ON DELETE RESTRICT,
	CONSTRAINT appropriate_context_type 
	CHECK (context_type = 1 OR context_type > 3)
	);