-- Each space is a distinct wiki document
create table spaces (
	id serial primary key,
	created timestamp not null default now(),
	title varchar(100) not null CONSTRAINT unique_title UNIQUE,
);

-- Elements are allowed to be: pages, lists, timelines, or pearls
create table element_types (
	id serial primary key,
	type_name varchar(20) not null
);

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
	space_id REFERENCES spaces ON DELETE CASCADE,
	element_id REFERENCES elements ON DELETE CASCADE,
	order integer not null,
	name varchar(500)
);