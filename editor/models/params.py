from editor.models.database import db, print_except

class Params(db.Model):
    __tablename__ = 'params'
    id = db.Column(db.Integer, primary_key=True)
    temperature = db.Column(db.Float, nullable=True)
    top_p = db.Column(db.Float, nullable=True)
    seed = db.Column(db.Integer, nullable=True)
    harassment_threshold = db.Column(db.String(255), nullable=True) 
    hate_speech_threshold = db.Column(db.String(255), nullable=True)
    dangerous_content_threshold = db.Column(db.String(255), nullable=True)
    explicit_content_threshold = db.Column(db.String(255), nullable=True)
    model = db.Column(db.String(255), nullable=True)

class ParamsService:
    @staticmethod
    def get_params(param_id):
        try:
            return db.session.get(Params, param_id)
        except Exception as e:
            print_except("get_params", e)
