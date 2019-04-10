from flask import(
	Blueprint,flash,g,redirect,render_template,request,url_for
	)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp=Blueprint('blog',__name__)

@bp.route('/')
def index():
	db=get_db()
	posts=db.execute(
		'SELECT p.id,title,body,created,author_id,username'
		' FROM post p JOIN user u ON p.author_id=u.id'
		' ORDER BY created DESC'
	).fetchall()
	return render_template('blog/index.html',posts=posts)
	#render_template可以带参数，这就把信息传到模板了

#在html中，也可以通过urlfor构造链接，还有别的{{}}控制语句等等，详情不展开
#写在这里是因为在html中写注释怪怪的...

@bp.route('/create',methods=('GET','POST'))
@login_required
#这里用了loginRequired这个装饰器之后，就必须在登录状态才能使用本视图
def create():
	if request.method=='POST':
		title=request.form['title']
		body=request.form['body']
		error=None

		if error is not None:
			flash(error)
		else:
			db=get_db()
			db.execute(
				'INSERT INTO post (title,body,author_id)'
				'VALUES (?,?,?)',
				(title,body,g.user['id'])
			)
			db.commit()
			return redirect(url_for('blog.index'))

	return render_template('blog/create.html')
	#嗯？在create.html中，{{request.form['body']}}这样的东西是什么操作？
	#试了一下把那两个东西删掉，没有影响...

#这个是通过id获取一个post，update和delete的时候都要用到，
#可以检查作者与登录用户是否一致，独立为一个函数是为了减少代码重复？
#wdnmd，原来这个post意思是帖子...不是post请求
def get_post(id,check_author=True):
	post=get_db().execute(
		'SELECT p.id,title,body,created,author_id,username'
		' FROM post p JOIN user u ON p.author_id=u.id'
		' WHERE p.id=?',
		(id,)
	).fetchone()

	if post is None:
		abort(404,"post id {0} dosen't exist.".formmat(id))
	if check_author and post['author_id']!=g.user['id']:
		abort(403)
	return post

@bp.route('/<int:id>/update',methods=('GET','POST'))
@login_required
def update(id):
	post=get_post(id)

	if request.method=='POST':
		title=request.form['title']
		body=request.form['body']
		error=None
		if not title:
			error='缺少title'
		if error is not None:
			flash(error)
		else:
			db=get_db()
			db.execute(
				'UPDATE post SET title=?,body=?'
				' WHERE id =?',
				(title,body,id)
			)
			db.commit()
			return redirect(url_for('blog.index'))
	return render_template('blog/update.html',post=post)
	#这个update.html更骚了，第13行还可以{{xxx or xxx}}的

@bp.route('/<int:id>/delete',methods=('POST',))
@login_required
def delete(id):
	get_post(id)
	db=get_db()
	db.execute('DELETE FROM post WHERE id=?',(id,))
	db.commit()
	return redirect(url_for('blog.index'))
