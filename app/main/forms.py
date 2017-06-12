from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, Regexp, ValidationError
from app.models import Role, User,Category


class PostForm(Form):
    category = SelectField('分类', coerce=int)
    title = StringField('标题', validators=[Length(0,128),DataRequired()])
    body_html = TextAreaField('正文',validators=[DataRequired(),])
    submit = SubmitField('提交')
    def __init__(self, *args, **kwargs):
        super(PostForm,self).__init__(*args, **kwargs)
        self.category.choices=[(category.id, category.name) for category in Category.query.order_by(Category.name).all()]