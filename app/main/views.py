from flask import request, render_template, session, redirect, url_for, current_app, abort, flash, make_response, \
    jsonify
from flask.ext.login import login_required, current_user
import uuid
from app.decorators import admin_required, permission_required
from . import main
from .forms import PostForm
from .. import db
from ..models import User, Role, Permission, Post, Category
import os
import random
import datetime

@main.route('/', methods=['GET'])
def index():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['POST_PER_PAGE'], error_out=False
    )
    posts = pagination.items
    return render_template('index.html', posts=posts, pagination=pagination)


@main.route('/posts', methods=['GET'])
def posts():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['POST_PER_PAGE'], error_out=False
    )
    posts = pagination.items
    return render_template('all_posts.html', posts=posts, pagination=pagination)


@main.route('/post/<id>', methods=['GET'])
def post(id):
    post = Post.query.get_or_404(id)
    return render_template('post.html', post=post)


@main.route('/put-post', methods=['GET', 'POST'])
@login_required
@admin_required
def put_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(id= str(uuid.uuid1()),
                    title=form.title.data,
                    author=current_user._get_current_object(),
                    body_html=form.body_html.data,
                    category=Category.query.get(form.category.data))
        db.session.add(post)
        db.session.commit()
        flash('发帖成功')
        return redirect(url_for('main.post', id=post.id))
    return render_template('add_post.html', form=form)


@main.route('/edit-post/<id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_post(id):
    post = Post.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.body_html = form.body_html.data
        post.category = Category.query.get(form.category.data)
        post.timestamp = datetime.datetime.utcnow()
        db.session.add(post)
        db.session.commit()
        flash('修改成功')
        return redirect(url_for('main.post', id=post.id))
    form.title.data = post.title
    form.body_html.data = post.body_html
    form.category.data = post.category_id
    return render_template('update_post.html', form=form)

@main.route('/delete-post/<id>', methods=['GET'])
@login_required
@admin_required
def delete_post(id):
    post = Post.query.get_or_404(id)
    db.session.delete(post)
    return jsonify(state='delete_success')




@main.route('/categories')
def categories():
    page = request.args.get('page', 1, type=int)
    pagination = Category.query.paginate(
        page, per_page=current_app.config['CATEGORY_PER_PAGE'], error_out=False
    )
    categories = pagination.items
    return render_template('all_categories.html', categories=categories, pagination=pagination)



@main.route('/posts_by_category/<int:category_id>')
def posts_by_category(category_id):
    page = request.args.get('page', 1, type=int)
    category = Category.query.get_or_404(category_id)
    query = category.posts
    print(type(query))
    pagination = query.paginate(
        page, per_page=current_app.config['POST_PER_PAGE'], error_out=False
    )
    posts = pagination.items
    return render_template('posts_by_category.html', category = category,posts=posts,pagination=pagination)


@main.route('/message_board')
def message_board():
    return render_template('message_board.html')
@main.route('/about_me')
def about_me():
    return render_template('about_me.html')



def gen_rnd_filename():
    filename_prefix = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    return '%s%s' % (filename_prefix, str(random.randrange(1000, 10000)))


@main.route('/ckupload/', methods=['POST', 'OPTIONS'])
def ckupload():
    """CKEditor file upload"""
    error = ''
    url = ''
    callback = request.args.get("CKEditorFuncNum")
    if request.method == 'POST' and 'upload' in request.files:
        fileobj = request.files['upload']
        fname, fext = os.path.splitext(fileobj.filename)
        rnd_name = '%s%s' % (gen_rnd_filename(), fext)
        filepath = os.path.join(current_app.static_folder, 'upload', rnd_name)
        # 检查路径是否存在，不存在则创建
        dirname = os.path.dirname(filepath)
        if not os.path.exists(dirname):
            try:
                os.makedirs(dirname)
            except:
                error = 'ERROR_CREATE_DIR'
        elif not os.access(dirname, os.W_OK):
            error = 'ERROR_DIR_NOT_WRITEABLE'
        if not error:
            fileobj.save(filepath)
            url = url_for('static', filename='%s/%s' % ('upload', rnd_name))
    else:
        error = 'post error'
    res = """<script type="text/javascript">
  window.parent.CKEDITOR.tools.callFunction(%s, '%s', '%s');
</script>""" % (callback, url, error)
    response = make_response(res)
    response.headers["Content-Type"] = "text/html"
    return response