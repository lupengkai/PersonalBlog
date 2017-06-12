from flask import request, url_for, redirect
from flask_admin.contrib.sqla import ModelView
from flask.ext.login import current_user


class NewBlogModelView(ModelView):
    def is_accessible(self):
        return current_user.is_administrator()

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('main.login', next=request.url))
