#添加了init.py之后，就可以把所在的文件夹作为一个包
#另，在这里写工厂函数
import os

from flask import Flask

def create_app(test_config=None):
	app=Flask(__name__,instance_relative_config=True)
	# in...config=True意为，配置文件是相对于实例文件夹的相对路径
	app.config.from_mapping(
		SECRET_KEY='dev',
		DATABASE=os.path.join(app.instance_path,'flaskr.sqlite'),
		)
	#此为配置
	if test_config is None:
		app.config.from_pyfile('config.py',silent=True)
	else:
		app.config.from_mapping(test_config)
	try:
		os.makedirs(app.instance_path)
	except OSError:
		pass
	#使用config.py重载上边的缺省配置or使用test_config
	#try-except目的是确保instance folder的存在

	@app.route('/hello')
	def hello():
		return 'helloWorld!'

	from . import db
	db.init_app(app)

	from . import auth
	app.register_blueprint(auth.bp)

	from . import blog
	app.register_blueprint(blog.bp)
	app.add_url_rule('/',endpoint='index')
	#上面两个是蓝图的注册
	#原本index视图的端点是blog.index，这样加了规则之后，url_for('index')就会有跟url_for('blog.index')一样的效果


	return app
