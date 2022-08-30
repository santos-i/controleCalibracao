from application.extensions.database import db

### definir relação entre das entidades.
class Equipamento(db.Model):
    sn = db.Column(db.String, primary_key=True)
    equipamento = db.Column(db.String(512))
    fabricante = db.Column(db.String(512))
    modelo = db.Column(db.String(512))
    projeto = db.Column(db.String(512))
    calibracao = db.Column(db.Date)
    vencimento = db.Column(db.Date)

    def __repr__(self):
        return str(self.sn)


class Certificado(db.Model):
    fileName = db.Column(db.String, primary_key=True)
    certificado = db.Column(db.LargeBinary)
    equipment_sn = db.Column(db.String)
    calibracao = db.Column(db.Date)