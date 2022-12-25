import sqlite3
from flask import g, Flask, jsonify, request
app = Flask(__name__)

DATABASE = 'database.db'

def get_db():
	db = getattr(g, '_database', None)

	if db is None:
		db = g._database = sqlite3.connect(DATABASE)

	#db.row_factory = sqlite3.Row

	return db

@app.teardown_appcontext
def close_connection(exception):
	db = getattr(g, '_database', None)
	if db is not None:
		db.close()

def init_db():
	with app.app_context():
		db = get_db()
		with app.open_resource('schema.sql', mode='r') as f:
			db.cursor().executescript(f.read())
		db.commit()


def query_db(query, args=(), one=False):
	cur = get_db().execute(query, args)
	rv = cur.fetchall()
	get_db().commit()
	cur.close()
	return (rv[0] if rv else None) if one else rv


@app.route("/")
def home():
	return app.send_static_file('index.html')

@app.route("/info")
def info():
	return app.send_static_file('info.html')

@app.route("/gamemaster")
def game():
	return app.send_static_file('game.html')

@app.route("/sqlinit")
def init():
	init_db()
	return "inited"

@app.route('/api/get_games')
def get_games():
	res = query_db("""select id, year_date from Game Order by id desc""")
	return jsonify(res)

@app.route('/api/join', methods=['POST'])
def show_sodas():
	if request.is_json:
		data = request.get_json()
		username = data[0]['username']
		game_id = data[0]['game_id']
		

		#get users ranking of sodas for specific game
		res = query_db("""select round_number, Round.soda_name 
			from Round, User, Score
			where round.game_id=?
			and User.name = LOWER(?)
			and round.game_id = User.game_id
			and round.game_id = Score.game_id 
			and round.id = user.round_id
			and User.name = Score.user_name
			and Round.soda_name = Score.soda_name
			order by placement""",[game_id, username])
		
		lastest_game = query_db("select max(id) from game")
		if int(game_id) >= lastest_game[0][0]:
			#check if user have sent score
			score = query_db("""select * 
				FROM Score 
				where user_name = lower(?) 
				and game_id = (select max(id) from Game)""", [username])
			if not score:
				#Add user to this round of latest game
				query_db("""insert or ignore into User (name, game_id, round_id)
					SELECT LOWER(?), game_id, count(distinct id) - 1 as round_id from Round WHERE game_id IN(SELECT MAX(id) FROM Game)
					""", [username])

				#Update user to latest game if score not sent.
				query_db("""update User
					SET round_id = (select max(id) from Round WHERE game_id = (select max(id) from Game))
					WHERE game_id = (select max(id) from Game)
					and name = LOWER(?);""", [username])
				#select sodas id and the randomized number
				res = query_db("""select game_id, round_number
					from Round 
					WHERE id in (select max(id)
						from Round 
						where game_id = (select max(id) from Game)
					)
					and game_id = (select max(id) from Game)
					order by round_number
					""")

		
		#if user not sent score for a round return this
		if not res:
			return jsonify("no data")
		return jsonify(res) #skicka username som kaka!
	return jsonify(message='Error')


#post
@app.route('/api/done', methods=['POST'])
def send_soda_rankning():
	if request.is_json:
		sodas = request.get_json()
		username = sodas[0]['username']

		#get latest round from latest game.
		new_game = query_db("""select * 
			FROM Round, User 
			WHERE Round.game_id = (select MAX(id) from Game) 
			and Round.game_id = User.game_id
			and User.name = lower(?) 
			and Round.id in (select max(id) 
				from round 
				WHERE game_id = (select MAX(id) from Game))
			and Round.id = User.round_id""",[username])
		print (new_game)
		if new_game:
			return jsonify(message='Vänta på att rundan är slut')
		
		sodas.pop(0)
		#add sodas score # fixa ifall man klicakr på nytt spel innan ny runda så kommer inte poängen räknas med från senaste rundan 
		for soda in sodas:
			score = len(sodas) - (soda['placement'] -1)
			print(soda)
			query_db("""insert OR IGNORE INTO Score (soda_name, user_name, placement, score, game_id)
				SELECT soda_name, name, ?, ?, game_id FROM(
				Select * 
				from round, User 
				where round_number=? 
				and round.game_id =(select max(id) from Game) 
				and User.name = lower(?)
				and round.game_id=User.game_id
				and round.id = User.round_id
				)
				
			""", [soda['placement'], score, soda['round_number'], username])

		res = query_db("""select soda_name 
			FROM Score 
			where game_id=(select max(id) from game) 
			and user_name = lower(?)
			order by placement;
			""", [username])
		return jsonify(res) #return name for soda.
	return jsonify(message='Error')


@app.route('/api/add_soda', methods=['POST'])
def add_soda():
	if request.is_json:
		soda = request.get_json()

		res = query_db("""insert or ignore into soda(game_id, name) 
			SELECT MAX(id), LOWER(?) FROM Game
		""", [soda])
		return jsonify(res)
	return jsonify(message='error')

#todo select by game_id
@app.route('/api/get_score', methods=['POST'])
def get_score():
	if request.is_json:
		game_id = request.get_json()
		res = query_db("""select soda_name, sum(score) as sum_score 
			from score
			where game_id = ?
			group by soda_name 
			order by sum_score desc""",[game_id])
		return jsonify(res)
	return jsonify(message='error')

@app.route('/api/new_game')
def new_game():
	res = query_db("insert INTO Game (year_date) SELECT DATE()")
	return new_round()


@app.route('/api/new_round')
def new_round():

	#create new round
	query_db("""insert INTO Round (id, round_number, game_id, soda_name)
	SELECT ifnull(round_id, 0), round_number, game, name FROM 
		(SELECT row_number() over(ORDER BY random()) AS round_number, name 
			FROM Soda WHERE game_id IN(SELECT MAX(id) FROM Game)),
		(SELECT MAX(id) AS game FROM Game),
		(SELECT COUNT(distinct id) AS round_id FROM Round WHERE game_id IN(SELECT MAX(id) FROM Game))
	""")

	return get_round()

@app.route('/api/get_round')
def get_round():
	res = query_db("""select *
		from Round 
		WHERE id in (select max(id)
			from Round 
			where game_id = (select max(id) from Game)
		)
		and game_id = (select max(id) from Game)""")

	return jsonify(res)

if __name__ == "__main__":
	app.run(debug=True)