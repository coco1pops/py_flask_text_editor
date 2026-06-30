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
    world_rules = db.Column(db.Text, nullable=True)

class ParamsService:
    @staticmethod
    def get_params(param_id):
        try:
            return db.session.get(Params, param_id)
        except Exception as e:
            print_except("get_params", e)
    @staticmethod
    def insert_base_params():     
        try:
            params = Params(
                id=1,
                temperature=0.7,
                top_p=0.9,
                harassment_threshold="BLOCK_MEDIUM_AND_ABOVE",
                hate_speech_threshold="BLOCK_MEDIUM_AND_ABOVE",
                dangerous_content_threshold="BLOCK_MEDIUM_AND_ABOVE",
                explicit_content_threshold="BLOCK_MEDIUM_AND_ABOVE",
                model="gemini-2.5-flash-lite",
                world_rules="*Relationships*/n*Locations*/n*Major world rules*/n*Timeline markers*")

            db.session.add(params)
            db.session.commit()

            return params.id  # works for BOTH SQLite & Postgres
    
        except Exception as e:
            db.session.rollback()
            print_except("insert_params", e)

class Models(db.Model):
    __tablename__= 'models'
    model_id = db.Column(db.String(30), primary_key=True)
    is_default = db.Column(db.Boolean, default=False)
    deprecated = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(30), nullable=True)

class ModelsService:
    @staticmethod
    def get_active_models():
        try:
            return Models.query.filter_by(deprecated=False).order_by(Models.name.desc()).all()
        except Exception as e:
            print_except("get_active_models", e)  

    def get_default_model():
        try:
            return Models.query.filter_by(is_default=True, deprecated=False).first()
        except Exception as e:
            print_except("get_default_model", e)  