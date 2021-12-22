
DROP TABLE IF EXISTS Soda;
DROP TABLE IF EXISTS Score;
DROP TABLE IF EXISTS User;
DROP TABLE IF EXISTS Game;

CREATE TABLE Soda (
	name VARCHAR PRIMARY KEY
);

CREATE TABLE Score (
	soda_name VARCHAR,
	user_name VARCHAR,
	placement INTEGER,
	score INTEGER,
	PRIMARY KEY (soda_name, user_name),
	FOREIGN KEY (soda_name) 
	  REFERENCES Soda (name),
	FOREIGN KEY (user_name) 
	  REFERENCES User (name)
);

CREATE TABLE User (
	name VARCHAR PRIMARY KEY,
	game_id INTEGER,
	FOREIGN KEY (game_id) 
	  REFERENCES Game (id)
);

CREATE TABLE Game (
	id INTEGER,
	game_number INTEGER,
	soda_name VARCHAR,
	PRIMARY KEY (id, soda_name)
	FOREIGN KEY (soda_name) 
	  REFERENCES Soda (name)
);

INSERT INTO Soda(name)
VALUES('nygårda');

INSERT INTO Soda(name)
VALUES('apotekarnes');

INSERT INTO Soda(name)
VALUES('freeway');

INSERT INTO Soda(name)
VALUES('favorit');

INSERT INTO Soda(name)
VALUES('premier');


INSERT INTO Game (id, game_number, soda_name)
	SELECT ifnull(game_id, 0), game_number, name FROM 
		(SELECT row_number() over(ORDER BY random()) AS game_number, name FROM soda ),
		(SELECT count(distinct id) AS game_id FROM Game);






