from critiquebrainz.data import db


class License(db.Model):
    __tablename__ = 'license'

    id = db.Column(db.Unicode, primary_key=True)
    full_name = db.Column(db.Unicode, nullable=False)
    info_url = db.Column(db.Unicode)

    _reviews = db.relationship('Review', cascade='delete', lazy='dynamic', backref='license')

    def to_dict(self):
        response = dict(id=self.id,
                        full_name=self.full_name,
                        info_url=self.info_url)
        return response

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self
