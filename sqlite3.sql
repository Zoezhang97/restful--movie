CREATE TABLE IF NOT EXISTS COLLECTION(
	tvmaze_id INTEGER,
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	last_update NUMERIC,
	name text,
	type text,
	language text,
	genres text,
	status text,
	runtime INTEGER,
	premiered NUMERIC,
	officialSite text,
	schedule text,
	rating INTEGER,
	weight INTEGER,
	network text,
	summary text,
	_links text

)