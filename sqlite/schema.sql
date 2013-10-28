/* each space is a distinct wiki document */
drop table if exists spaces;
create table spaces (
	id integer primary key autoincrement,
	created timestamp default (strftime('%s', 'now')),
	title text not null
);

