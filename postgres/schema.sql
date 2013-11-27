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
	title varchar(100) not null CONSTRAINT unique_title UNIQUE
);
/* comment comment */

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
	space_id integer REFERENCES spaces ON DELETE CASCADE,
	element_type integer REFERENCES element_types ON DELETE RESTRICT,
	title varchar(100) default 'pearl_element'
);

create table list_nodes (
	id serial primary key,
	element_id integer,
	title varchar(100) not null,
	subtitle varchar(500),
	content text
);

create table list_relationship_types (
	id serial primary key,
	type_name varchar(20) not null
);

INSERT INTO list_relationship_types (id, type_name) VALUES 
	(1, 'parent'),
	(2, 'child'),
	(3, 'sibling');

create table list_relationships (
	id serial primary key,
	left_node integer references list_nodes ON DELETE CASCADE,
	right_node integer references list_nodes ON DELETE CASCADE,
	relationship integer references list_relationship_types ON DELETE RESTRICT,
	CONSTRAINT consistent_node_order CHECK (left_node < right_node)
);

create table toc (
	id serial primary key,
	created timestamp not null default now(),
	element_id integer REFERENCES elements ON DELETE CASCADE,
	ordinal integer default 0,
	name varchar(500)
);

-- There are currently 8 context types available
create table context_types (
	id serial primary key,
	ordinal integer unique not null,
	type_name varchar(20) not null
);

INSERT INTO context_types (id, ordinal, type_name) VALUES
	(1, 0, 'main'),
	(2, 1, 'subtitle'),
	(3, 2, 'abstract'),
	(4, 3, 'motivation'),
	(5, 4, 'basics'),
	(6, 5, 'opinions'),
	(7, 6, 'social'),
	(8, 7, 'xcredit');

create table contexts (
	id serial primary key,
	created timestamp not null default now(),
	toc_id integer REFERENCES toc ON DELETE CASCADE,
	context_type integer REFERENCES context_types ON DELETE RESTRICT,
	content text
);

create table revisions (
	id serial primary key,
	created timestamp not null default now(),
	context_id integer REFERENCES contexts,
	action varchar(100),
	content text
);

CREATE OR REPLACE FUNCTION revisions_function() RETURNS trigger AS $revisions_function$
BEGIN
	IF (tg_op = 'DELETE') THEN
		INSERT INTO revisions (context_id, content, action) VALUES (old.id, old.content, 'DELETE');
		RETURN OLD;
	ELSIF (tg_op = 'INSERT') THEN
		INSERT INTO revisions (context_id, content, action) VALUES (new.id, new.content, 'INSERT');
		RETURN NEW;
	ELSIF (tg_op = 'UPDATE') THEN
		INSERT INTO revisions (context_id, content, action) VALUES (new.id, new.content, 'UPDATE');
		RETURN NEW;
	END IF;
	RETURN NULL;
END;
$revisions_function$ LANGUAGE plpgsql;

CREATE TRIGGER revisions_trigger
AFTER INSERT OR DELETE OR UPDATE ON contexts
FOR EACH ROW EXECUTE PROCEDURE revisions_function();
