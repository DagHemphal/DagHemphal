
DROP TABLE IF EXISTS Soda;
DROP TABLE IF EXISTS Score;
DROP TABLE IF EXISTS User;
DROP TABLE IF EXISTS Game;

CREATE TABLE Soda (
	name VARCHAR PRIMARY KEY
);

CREATE TABLE Game (
	id INTEGER PRIMARY KEY,
	year_date DATE
);

CREATE TABLE Round (
	id INTEGER,
	round_number INTEGER,
	game_id INTEGER,
	soda_name VARCHAR,
	PRIMARY KEY (id, soda_name),
	FOREIGN KEY (game_id)
	  REFERENCES Game (id),
	FOREIGN KEY (soda_name)
	  REFERENCES Soda (name)
);

CREATE TABLE User (
	name VARCHAR PRIMARY KEY,
);

CREATE TABLE User_games (
	user_name VARCHAR,
	game_id INTEGER,
	FOREIGN KEY (user_name) 
	  REFERENCES User (name),
	FOREIGN KEY (game_id) 
	  REFERENCES Game (id)
);

CREATE TABLE Score (
	soda_name VARCHAR,
	user_name VARCHAR,
	placement INTEGER,
	score INTEGER,
	game_id INTEGER,
	PRIMARY KEY (soda_name, user_name),
	FOREIGN KEY (soda_name) 
	  REFERENCES Soda (name),
	FOREIGN KEY (user_name) 
	  REFERENCES User (name),
	FOREIGN KEY (game_id)
	  REFERENCES Game (id)
);








INSERT INTO Soda(name)
VALUES('apotekarnes');

INSERT INTO Soda(name)
VALUES('premier');

#fix to round
INSERT INTO Game (id, game_number, soda_name)
	SELECT ifnull(game_id, 0), game_number, name FROM 
		(SELECT row_number() over(ORDER BY random()) AS game_number, name FROM soda ),
		(SELECT count(distinct id) AS game_id FROM Game);






