"""
    models.py
    ---------

"""
from datetime import datetime
from homepage import db
import re


punct = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')


class Project(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(80))
  description = db.Column(db.Text)
  url = db.Column(db.String(255))
  code = db.Column(db.String(255))
  text = db.Column(db.String(255))
  image = db.Column(db.String(255))

  def __repr(self):
      return '(Project: {})'.format(self.title)


tags = db.Table('tags',
        db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')),
        db.Column('post_id', db.Integer, db.ForeignKey('post.id'))
        )


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    body = db.Column(db.Text)
    pub_date = db.Column(db.DateTime, default=datetime.utcnow())
    is_published = db.Column(db.Boolean)

    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'))
    tags = db.relationship('Tag', secondary=tags,
        backref=db.backref('posts', lazy='dynamic'))

    def __init__(self, title="", body="", category=None, pub_date=None, is_published=False, tags=[]):
        self.title = title
        self.body = body
        self.category = category
        if pub_date is None:
            pub_date = datetime.utcnow()
        self.pub_date = pub_date
        self.is_published = is_published
        self.tags = tags

    @property
    def slugify(self):
        result = []
        for word in punct.split(self.title.lower()):
            if word:
                result.append(word)
        return '-'.join(result)

    @property
    def date(self):
      return self.pub_date.strftime("%B %d, %Y")

    def __repr__(self):
        return '(Post: {})'.format(self.title)


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

    def __repr__(self):
        return '(Tag: {})'.format(self.name)
