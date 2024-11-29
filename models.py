from CTFd.config import process_boolean_str
from CTFd.models import db
from CTFd.utils import get_app_config

class Solutions(db.Model):
    __tablename__ = "solutions"

    id = db.Column(db.Integer, db.ForeignKey("challenges.id", ondelete="CASCADE"), primary_key=True)
    solution = db.Column(db.Text)
    state = db.Column(db.String(80), nullable=False, default="visible")

