from editor.models.database import db, print_except

from datetime import datetime

class SysInt(db.Model):
    __tablename__ = "sysints"

    sysint_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.Text)
    instruction = db.Column(db.Text)

class SysIntService:
    @staticmethod
    def get_sysint(sysint_id, allow_not_found=False):
        try:
            sysint = db.session.get(SysInt, sysint_id)

            if not sysint and not allow_not_found:
                print_except("get_sysint", "Record not found")

            return sysint
        except Exception as e:
            print_except("get_sysint", e)
    
    @staticmethod
    def get_sysints():
        try:
            return SysInt.query.all()
        except Exception as e:
            print_except("get_sysints", e)


    @staticmethod
    def insert_sysint(name, description, instruction):
        try:
            sysint = SysInt(
                name=name,
                description=description,
                instruction=instruction
            )

            db.session.add(sysint)
            db.session.commit()

            return sysint.sysint_id  # works for BOTH SQLite & Postgres
    
        except Exception as e:
            db.session.rollback()
            print_except("insert_sysint", e)

    @classmethod
    def update_sysint(cls, sysint_id, name, description, instruction):
        try:
            sysint = cls.get_sysint(sysint_id)

            if not sysint:
                return False

            sysint.name = name
            sysint.description = description
            sysint.instruction = instruction

            db.session.commit()
            return True
        
        except Exception as e:
            db.session.rollback()
            print_except("update_sysint", e)

    @classmethod
    def delete_sysint(cls, sysint_id):
        try:
            sysint = cls.get_sysint(sysint_id)

            if not sysint:
                return False

            db.session.delete(sysint)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print_except("delete_sysint", e)