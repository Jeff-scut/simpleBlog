#这是认证功能的蓝图，把代码注册到蓝图，再到
#工厂函数中把蓝图注册到应用；分多个蓝图，每个蓝图一个模块
import functools

from flask import(Blueprint,flash,g,redirect,render_template,request,session,url_for)
from werkzeug.security import check_password_hash,generate_password_hash

from flaskr.db import get_db

bp=Blueprint('auth',__name__,url_prefix='/auth')
#url_prefix会添加到所有与本蓝图有关的url前面

#使用app.register_blueprint()导入并注册蓝图，在工厂函数中
#下面是auth的视图

@bp.route('/register',methods=('GET','POST'))
def register():
	if request.method=='POST':
		username=request.form['username']
		password=request.form['password']
		db=get_db()
		error=None

		if db.execute(
			'SELECT id FROM user WHERE username=?',(username,)
			).fetchone() is not None:
				error='User {} is already registered.'.format(username)
		if error is None:
			db.execute(
				'INSERT INTO user (username,password) VALUES (?,?)',
				(username,generate_password_hash(password))
			)
			#问号是占位符
			db.commit()
			return redirect(url_for('auth.login'))
			#这里出现了redirect！
		flash(error)
	return render_template('auth/register.html')

@bp.route('/login',methods=('GET','POST'))
def login():
	if request.method=='POST':
		username=request.form['username']
		password=request.form['password']
		db=get_db()
		error=None

		user=db.execute(
			'SELECT * FROM user WHERE username=?',(username,)
		).fetchone()
		if user is None:
			error="Incorrect username"
		elif not check_password_hash(user['password'],password):
			error="Incorrect password"
		if error is None:
			session.clear()
			session['user_id']=user['id']
			return redirect(url_for('index'))
		flash(error)
		#session是一个dict用于储存横跨请求的值。
		#当验证成功后，用户的id被储存于一个新的会话中
		#会话数据被储存到一个向浏览器发送的 cookie 中，在后继请求中，浏览器会返回它
	return render_template('auth/login.html')

#这个beforeRequest会在试图函数之前运行，作用是检查用户id是否在session中
@bp.before_app_request
def load_logged_in_user():
	user_id=session.get('user_id')
	if user_id is None:
		g.user=None
	else:
		g.user=get_db().execute(
			'SELECT * FROM user WHERE id =?',(user_id,)
			).fetchone()

#注销功能，把id从session中移除
@bp.route('/logout')
def logout():
	session.clear()
	return redirect(url_for('index'))

#在其他试图中的验证功能，使用装饰器，what's that?
def login_required(view):
	@functools.wraps(view)
	def wrapped_view(**kwargs):
		if g.user is None:
			return redirect(url_for('auth.login'))
		return view(**kwargs)
	return wrapped_view
