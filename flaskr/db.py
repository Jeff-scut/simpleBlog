import sqlite3

import click
from flask import current_app,g
from flask.cli import with_appcontext

#get_db用于创建连接
def get_db():
	if 'db' not in g:
		g.db=sqlite3.connect(
			current_app.config['DATABASE'],
			detect_types=sqlite3.PARSE_DECLTYPES
			)
		g.db.row_factory=sqlite3.Row
	return g.db
#g是一个特殊对象，独立于每一个请求，可以存储可能多个函数都会用到的数据
#current_app也是个特殊对象，指向处理请求的flask应用

def close_db(e=None):
	db=g.pop('db',None)
	if db is not None:
		db.close()

#数据库初始化
def init_db():
	db=get_db()
	with current_app.open_resource('schema.sql') as f:
		db.executescript(f.read().decode('utf8'))

#click.command用于定义一个名叫init-db的命令行
@click.command('init-db')
@with_appcontext
def init_db_command():
	"""Clear the existing data and create new tables."""
	init_db()
	click.echo('Initialized the database')

#一个用来注册函数的函数，需要在工厂中执行
#第一个是让Flask在返回响应后进行清理时调用
#第二个是一个可以与flask一起工作的命令行
def init_app(app):
	app.teardown_appcontext(close_db)
	app.cli.add_command(init_db_command)
