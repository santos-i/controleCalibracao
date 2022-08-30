import datetime
from io import BytesIO
from flask import render_template, redirect, url_for, request, send_file
from application.services.forms import  RegisterForm, UpdateProjetoForm, EditForm, UpdatePrazoForm
from application.extensions.database import db
from application.services.models import Certificado, Equipamento


def init_app(app):

    @app.route('/')
    def home():
        try:
            equipments = Equipamento.query.all()
            return render_template('home.html', equipments=equipments)
        
        except:
            return render_template('home.html', equipments=[])


    @app.route('/registro', methods=['GET','POST'])
    def registro():
        error = None
        form = RegisterForm()

        if request.method == 'POST':
            if request.form['submit_button'] == 'cancel':
                return redirect(url_for('home'))
            
            elif request.form['submit_button'] == 'ok':
                if Equipamento.query.filter_by(sn=form.sn.data).first():
                    error = 'Equipamento já resgistrado!\n\
                        Para realizar alteração utilizar o botão "edit".'
                    
                    return render_template('registro.html', form=form, error=error)

                else:
                    if request.form.get('select') == 'sim': # Caso tenha prazo para calibração
                        calibracao = request.form.get('calibrationDate')
                        # transforma a string para Date.
                        calibracao =  datetime.datetime.strptime(calibracao,'%Y-%m-%d').date()
                        prazo = int(request.form.get('prazo'))
                        vencimento = calibracao + datetime.timedelta(days=prazo)
                        # copia para registro do nome do certificado
                        calibracao2 = calibracao.strftime('%Y%m%d')

                        new_equipment = Equipamento(
                            sn = form.sn.data.upper(),
                            equipamento = form.equipamento.data.upper(),
                            fabricante = form.fabricante.data.title(),  
                            modelo = form.modelo.data.upper(),
                            projeto = form.projeto.data.upper(),
                            calibracao = calibracao,
                            vencimento = vencimento,
                        )

                        db.session.add(new_equipment)
                        
                        # Gera o nome do certificado
                        fileName = form.fabricante.data.upper() + '_'
                        fileName += form.equipamento.data.upper() + '_'
                        fileName += form.modelo.data.upper() + '_' 
                        fileName += form.sn.data + '_'
                        fileName += calibracao2 + '-CERT_CAL.pdf'

                        file = request.files['certificado']
                        
                        certificado = Certificado(
                            fileName = fileName,
                            certificado = file.read(),
                            equipment_sn = new_equipment.sn,
                            calibracao = new_equipment.calibracao
                        ) 

                        db.session.add(certificado)
                        db.session.commit()                      

                        return redirect(url_for('home'))


                    else: # Não possui prazo para calibração
                        new_equipment = Equipamento(
                            sn = form.sn.data.upper(),
                            equipamento = form.equipamento.data.upper(),
                            fabricante = form.fabricante.data.upper(),  
                            modelo = form.modelo.data.upper(),
                            projeto = form.projeto.data.upper(),
                            calibracao = None,
                            vencimento = None,
                        )
                        
                        db.session.add(new_equipment)
                        db.session.commit()
                        return redirect(url_for('home'))

        return render_template('registro.html', form=form, error=error)


    @app.route('/edit/<sn>', methods=['GET', 'POST'])
    def edit(sn):

        ### DEFINIR relação entre as entidades (equipamento e certificado) 
        form = EditForm()
        equipment = Equipamento.query.filter_by(sn=sn).first()
        
        if request.method == 'POST':
            if request.form['submit_button'] == 'cancel':
                return redirect(url_for('home'))
            
            elif request.form['submit_button'] == 'delete':
                    db.session.delete(equipment)
                    Certificado.query.filter_by(equipment_sn=equipment.sn).delete()
                    db.session.commit()
                    return redirect(url_for('home'))
            
            elif request.form['submit_button'] == 'ok':
                    if request.form.get('select') == 'sim':
                        calibracao = request.form.get('calibrationDate')
                        calibracao =  datetime.datetime.strptime(calibracao,'%Y-%m-%d').date()
                        prazo = int(request.form.get('prazo'))
                        vencimento = calibracao + datetime.timedelta(days=prazo)
                        # copia para registro do nome do certificado
                        calibracao2 = calibracao.strftime('%Y%m%d')


                        equip = Equipamento.query.filter_by(sn=sn).first()
                        equip.calibracao = calibracao
                        equip.vencimento = vencimento

                        db.session.commit()


                        # Gera o nome do certificado
                        fileName = equipment.fabricante + '_'
                        fileName += equipment.equipamento + '_'
                        fileName += equipment.modelo + '_' 
                        fileName += equipment.sn + '_'
                        fileName += calibracao2 + '-CERT_CAL.pdf'

                        file = request.files['certificado']
                        
                        certificado = Certificado(
                            fileName = fileName,
                            certificado = file.read(),
                            equipment_sn = equipment.sn,
                            calibracao = calibracao
                        ) 

                        db.session.add(certificado)
                        db.session.commit()           
                        return redirect(url_for('home'))
                
                    else:
                        equip = Equipamento.query.filter_by(sn=sn).first()
                        equip.calibracao = None
                        equip.vencimento = None
                        db.session.commit()
                        return redirect(url_for('home'))

        return render_template('edit.html', form=form, equipment=equipment)


    @app.route('/editProjeto/<sn>', methods=['GET', 'POST'])
    def editProjeto(sn):
        form = UpdateProjetoForm()
        equip = Equipamento.query.filter_by(sn=sn).first()

        if request.method == 'POST':
            if request.form['submit_button'] == 'cancel':
                return redirect(url_for('home'))
            
            elif request.form['submit_button'] == 'ok':
                equip.projeto = form.projeto.data.upper()
                db.session.commit()
                return redirect(url_for('home'))

        return render_template('editProjeto.html',form=form, equipment=equip)


    @app.route('/editPrazo/<sn>', methods=['GET', 'POST'])
    def editPrazo(sn):
        form = UpdatePrazoForm()
        equipment = Equipamento.query.filter_by(sn=sn).first()

        if request.method == 'POST':
            if request.form['submit_button'] == 'cancel':
                return redirect(url_for('home'))
            
            elif request.form['submit_button'] == 'ok':
                prazo = int(request.form.get('prazo'))
                calibracao = equipment.calibracao
                vencimento = calibracao + datetime.timedelta(days=prazo)

                equip = Equipamento.query.filter_by(sn=sn).first()
                equip.vencimento = vencimento
                db.session.commit()
 
                return redirect(url_for('home'))

        return render_template('editPrazo.html', form=form, equipment=equipment)


    @app.route('/certificados_<sn>')
    def certificados(sn):
        docs = Certificado.query.filter_by(equipment_sn=sn).all()
        equipamento = Equipamento.query.filter_by(sn=sn).first()

        return render_template('certificados.html', docs=docs, equip=equipamento)


    @app.route('/<fileName>')
    def download(fileName):
        file = Certificado.query.filter_by(fileName=fileName).first()
        try:
            return send_file(
                BytesIO(file.certificado),
                attachment_filename= file.fileName,
                as_attachment=True
                )
        except:
            return render_template('teste.html')


    @app.route('/del-<fileName>')
    def deleteFile(fileName):

        file = Certificado.query.filter_by(fileName=fileName).first()
        sn = file.equipment_sn
        db.session.delete(file)
        db.session.commit()

        return  certificados(sn)


        