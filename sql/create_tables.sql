CREATE TABLE IF NOT EXISTS movies (
    show_id TEXT,
    movie_type TEXT NOT NULL, 
    title TEXT NOT NULL, 
    director TEXT, 
	  cast_members TEXT,
    country TEXT, 
    date_added DATE, 
    release_year INTEGER NOT NULL,
    rating VARCHAR(25),
    duration VARCHAR(20) NOT NULL,
  	listed_in TEXT,
    description TEXT,
	  rating_category TEXT
);
