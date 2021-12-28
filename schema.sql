DROP TABLE IF EXISTS Game;
DROP TABLE IF EXISTS Soda;
DROP TABLE IF EXISTS Round;
DROP TABLE IF EXISTS User;
DROP TABLE IF EXISTS Score;

CREATE TABLE Game (
	id INTEGER PRIMARY KEY,
	year_date DATE
);

CREATE TABLE Soda (
	game_id INTEGER,
	name VARCHAR,
	PRIMARY KEY (game_id, name),
	FOREIGN KEY (game_id)
	  REFERENCES Game (id)
);

CREATE TABLE Round (
	id INTEGER,
	round_number INTEGER,
	game_id INTEGER,
	soda_name VARCHAR,
	PRIMARY KEY (id, game_id, soda_name),
	FOREIGN KEY (game_id)
	  REFERENCES Game (id),
	FOREIGN KEY (soda_name)
	  REFERENCES Soda (name)
);

CREATE TABLE User (
	name VARCHAR,
	game_id INTEGER,
	round_id INTEGER,
	PRIMARY KEY (name, game_id),
	FOREIGN KEY (game_id)
	  REFERENCES Game (id),
	FOREIGN KEY (round_id)
	  REFERENCES Round (id)
);

CREATE TABLE Score (
	soda_name VARCHAR,
	user_name VARCHAR,
	placement INTEGER,
	score INTEGER,
	game_id INTEGER,
	PRIMARY KEY (user_name, game_id, soda_name),
	FOREIGN KEY (soda_name)
	  REFERENCES Soda (name),
	FOREIGN KEY (user_name) 
	  REFERENCES User (name),
	FOREIGN KEY (game_id)
	  REFERENCES Game (id)
);

-- CREATING test data
--Create new game
/*INSERT INTO Game (year_date)
	SELECT DATE();


--add soda to game
INSERT INTO Soda(game_id, name)
	SELECT MAX(id), LOWER('apotekarnes') FROM Game;

--add new round
INSERT INTO Round (id, round_number, game_id, soda_name)
	SELECT ifnull(round_id, 0), round_number, game, name FROM 
		(SELECT row_number() over(ORDER BY random()) AS round_number, name 
			FROM Soda WHERE game_id IN(SELECT MAX(id) FROM Game)),
		(SELECT MAX(id) AS game FROM Game),
		(SELECT COUNT(distinct id) AS round_id FROM Round WHERE game_id IN(SELECT MAX(id) FROM Game));
/*
--add new user to latest round and game
INSERT OR IGNORE INTO User (name, game_id, round_id)
		SELECT LOWER('test'), 1, COUNT(distinct id) - 1 AS round_id FROM Round WHERE game_id IN(SELECT MAX(id) FROM Game);

--add score to user test
INSERT OR IGNORE INTO Score (soda_name, user_name, placement, score, game_id)
	SELECT Soda.name, User.name, '2', 20, User.game_id 
	FROM Soda, User
	WHERE Soda.name = LOWER('apotekarnes')
	AND User.game_id = Soda.game_id
	AND User.name = LOWER('test')
	AND User.game_id = 2;*/
