from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    sn  = StringField('Serial Number', validators=[DataRequired()])
    equipamento  = StringField('Equipamento', validators=[DataRequired()])
    fabricante  = StringField('Fabricante', validators=[DataRequired()])
    modelo  = StringField('Modelo', validators=[DataRequired()])
    projeto  = StringField('Projeto', validators=[DataRequired()])


class EditForm(FlaskForm):
    calibracao  = StringField('Calibração', validators=[DataRequired()])


class UpdateProjetoForm(FlaskForm):
    projeto  = StringField('Projeto', validators=[DataRequired()])


class UpdatePrazoForm(FlaskForm):
    prazo  = IntegerField('Projeto', validators=[DataRequired()])