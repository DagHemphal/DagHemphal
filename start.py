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

@app.route('/api/join/<username>')
def show_sodas(username):
	query_db("""insert or ignore into User (name, game_id)
		SELECT LOWER(?), count(distinct id) - 1 as game_id from Game
		""", [username])

	res = query_db("""
		select game_number, user.soda_name from game,
		(select score.*, game_id from score,user where score.user_name = user.name and user.name = lower(?)) as user
		where game.id = user.game_id 
		and game.soda_name = user.soda_name
		order by placement;
		""", [username])
	if not res:
		res = query_db("""
			select id, game_number from Game where id = (select game_id from User where name = lower(?))
			""", [username])
	return jsonify(res) #skicka username som kaka!

#post
@app.route('/api/done', methods=['POST'])
def send_soda_rankning():
	if request.is_json:
		sodas = request.get_json()
		username = sodas[0]['username']
		game_id = sodas[0]['game_id']

		new_game = query_db("select count(distinct id) as game_id from Game")
		if (new_game[0][0] - 1) == int(game_id):
			return jsonify(message='Vänta på att spelet är slut')
		
		sodas.pop(0)

		for soda in sodas:
			score = len(sodas) - (soda['placement'] -1)
			query_db("""insert or ignore into score (soda_name, user_name, placement, score)
			select soda_name, lower(?), ?, ? from game where id=? and game_number=? 
			""", [username, soda['placement'], score, game_id, soda['game_number']])

		res = query_db("select soda_name from score where user_name = lower(?) order by placement", [username])
		return jsonify(res) #return name for soda.
	return jsonify(message='Error')


@app.route('/api/add_soda', methods=['POST'])
def add_soda():
	if request.is_json:
		soda = request.get_json()
		res = query_db("""insert or ignore into soda(name) 
			VALUES(LOWER(?))
		""", [soda])
		return jsonify(res)
	return jsonify(message='error')

#get
@app.route('/api/get_score')
def get_score():
	res = query_db("select soda_name, sum(score) as sum_score from score group by soda_name order by sum_score desc");
	return jsonify(res);

@app.route('/api/new_game')
def new_game():

	query_db("""insert into Game (id, game_number, soda_name)
	select ifnull(game_id, 0), game_number, name from 
		(select row_number() over(order by random()) as game_number, name from soda ),
		(select count(distinct id) as game_id from Game)
	""")

	res = query_db("select * from game where id = (select count(distinct id) as id from Game) - 1")

	return jsonify(res)

@app.route('/api/get_game')
def get_game():

	res = query_db("select * from game where id = (select count(distinct id) as id from Game) - 1")

	return jsonify(res)

if __name__ == "__main__":
	app.run(debug=True)