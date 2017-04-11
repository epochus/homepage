"""
    models.py
    ---------

"""
from homepage import db


tags = db.Table('tags',
        db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')),
        db.Column('project_id', db.Integer, db.ForeignKey('project.id'))
        )


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

    def __repr__(self):
        return '{}'.format(self.name)


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    rank = db.Column(db.Integer)
    url = db.Column(db.String(4000))
    description = db.Column(db.Text)
    
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'))

    tags = db.relationship('Tag', secondary=tags,
        backref=db.backref('projects', lazy='dynamic'))

    def __repr__(self):
        return '{}'.format(self.title)