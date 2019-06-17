from flaskext.mysql import MySQL

class Database:
	def __init__(self, app, user, password, db, host='localhost', port=3306):
		# MySQL configurations
		app.config['MYSQL_DATABASE_USER'] = user
		app.config['MYSQL_DATABASE_PASSWORD'] = password
		app.config['MYSQL_DATABASE_PORT'] = port
		app.config['MYSQL_DATABASE_DB'] = db
		app.config['MYSQL_DATABASE_HOST'] = host

		mysql = MySQL()
		mysql.init_app(app)
		self.mysql = mysql

	def get_data(self, sql, params=None):
		conn = self.mysql.connect()
		cursor = conn.cursor()
		try:
			print(sql)
			cursor.execute(sql, params)
		except Exception as e:
			print(e)
			return False

		result = cursor.fetchall()
		cursor.close()
		conn.close()
		# We always return the data as a big list to keep this as generic as possible 😉
		return result

	def set_data(self, sql, params=None):
		conn = self.mysql.connect()
		cursor = conn.cursor()
		print("Setting Data")
		try:
			print(sql)
			cursor.execute(sql, params)
			conn.commit()
		except Exception as e:
			print(e)

		cursor.close()
		conn.close()

		# Is this ok on an update?
		return cursor.lastrowid
