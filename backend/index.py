from backend.config import app, db, bcrypt, User
from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_login import login_user, current_user, logout_user, login_required
from backend import forms
from backend.config import User, User_Act, User_Con_Act
import os
import datetime
from datetime import datetime
import calendar
from itertools import groupby
from operator import attrgetter
from docxtpl import DocxTemplate
import locale
locale.setlocale(locale.LC_TIME, "es_GT")


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/informe',methods=['GET', 'POST'])
def informe():
    
    user_id= current_user.id
    entry = User.query.filter_by(id=user_id).first()
    categorias = dict([(g.actividad_contrato, g.actividad_resuelta) for g in User_Con_Act.query.filter_by(usuario=entry.usuario).with_entities(User_Con_Act.actividad_contrato, User_Con_Act.actividad_resuelta).order_by('actividad_contrato')])
 
    
    ##ADDING VARIABLES AL REPORTE##
    if ((request.method=='POST') and (request.form.get('addinput')=='Add')):
        
        registro = User_Act(
            usuario=entry.usuario,
            no_contrato = entry.no_contrato,
            no_acuerdo = entry.no_acuerdo,
            actividad_contrato = request.form['act'],
            actividad_especifica = request.form['actEsp'],
            ano=request.form.get('anos'),
            mes=request.form.get('meses'), 
            date = datetime.strptime(request.form.get('meses')+'-'+request.form.get('anos'), '%B-%Y'))
        
        db.session.add(registro)
        db.session.commit()

        return render_template('informe.html', 
            entry=entry, 
            meses=request.form.get('meses'), 
            anos= request.form.get('anos'), 
            act=request.form.get('act'), 
            categorias=categorias)
    
    elif request.method=='GET':
        return render_template('informe.html', 
            entry=entry, 
            meses=request.form.get('meses'), 
            anos= request.form.get('anos'), 
            act=request.form.get('act'), 
            categorias=categorias)
        
    ##PARA GENERAR EL REPORTE##
    if ((request.method=='POST') and (request.form.get('submitinput')=='Generar')):
        if request.form.get('anualreport')=='anual':
            # mes y fecha inicial
            mesi = request.form.get('mesinicio')
            fi= datetime.strptime(mesi+'-'+request.form.get('anos'), '%B-%Y')

            # mes y fecha final
            mesf = request.form.get('mesfin')
            ff = datetime.strptime(mesf+'-'+request.form.get('anos'), '%B-%Y')
            
            # generacion data
            data = User_Act.query.filter((User_Act.usuario==entry.usuario)& (User_Act.ano==request.form.get('anos'))& (User_Act.date.between(fi,ff))).\
                with_entities(User_Act.actividad_contrato, User_Act.actividad_especifica).all()
            periodo='ANUAL'
            
            fecha = datetime.strptime(mesf+'-'+request.form.get('anos'), '%B-%Y')
            ld = calendar.monthrange(int(request.form.get('anos')), fecha.month)[1]
            fechaid = f"Del 01 de {mesi} al {ld} de {mesf} del {request.form.get('anos')}"  
            fechafirma= f"{ld} de {mesf} del {request.form.get('anos')}"

        else:
            data = User_Act.query.filter((User_Act.usuario==entry.usuario)&(User_Act.ano==request.form.get('anos'))&(User_Act.mes==request.form.get('meses'))).\
                with_entities(User_Act.actividad_contrato, User_Act.actividad_especifica).all()
            periodo='MENSUAL'
            fecha = datetime.strptime(request.form.get('meses')+'-'+request.form.get('anos'), '%B-%Y')
            ld = calendar.monthrange(int(request.form.get('anos')), fecha.month)[1]
            fechaid = f"Del 01 al {ld} de {request.form.get('meses')} del {request.form.get('anos')}"
            fechafirma= f"{ld} de {request.form.get('meses')} del {request.form.get('anos')}"
            
        listings = [list(g) for k, g in groupby(data, attrgetter('actividad_contrato'))]
        listings = sorted(list(set([item for lista in listings for item in lista ])), key=lambda tup: tup[0])
        dict_c = {}
        for i in listings:
            dict_c.setdefault(i[0],[]).append(i[1])   
        
        listings_c=[]
        for (key, val),n in zip(dict_c.items(),range(1,len(dict_c)+1)):
            x={
                'id': n,
                'contrato':key,
                'actividad':val
                            }
            listings_c.append(x)

        output={
            'fecha': fechaid,
            'fechafirma': fechafirma,
            'periodo': periodo,
            'usuario':entry.usuario,
            'no_contrato': entry.no_contrato,
            'no_acuerdo': entry.no_acuerdo,
            'row_contents':listings_c,
            'dpi':entry.dpi
            }
       
        dir = request.form.get('direccion')
        doc=DocxTemplate(os.path.abspath('backend\INFORME.docx'))
        doc.render(output)
        if periodo=='MENSUAL':
            doc.save(dir + "\\" + f"informe_{request.form.get('meses')}_{request.form.get('anos')}.docx")
        else:
            doc.save(dir + "\\" + f"informe_{request.form.get('anos')}.docx")

        return render_template('informe.html', entry=entry, categorias=categorias)
          
    ### PARA SALIR DEL USUARIO ###
    if (request.method == "POST") & (request.form.get('post_header') == 'log out'):
        logout_user()
        return redirect(url_for('hello_world')) 
   
    return render_template('informe.html', entry=entry, categorias=categorias)
    
    
@app.route('/index', methods = ['GET', 'POST'])
def hello_world():
    categories = [(g.id, g.usuario) for g in User.query.with_entities(User.id, User.usuario).order_by('id').all()]
    category_dict = dict(categories)
    add_form = forms.ContratoForm()
    add_form.usuario.choices = categories
    
    ### PARA REGISTRAR UN NUEVO USUARIO###
    if forms.RegistrationForm().validate_on_submit():
        register_form = forms.RegistrationForm()
        hashed_password = bcrypt.generate_password_hash(register_form.password.data).decode('utf-8')
        registro = User(
            usuario=register_form.usuario.data,
            no_contrato = register_form.no_contrato.data,
            no_acuerdo = register_form.no_acuerdo.data,
            email = register_form.email.data,
            dpi = register_form.dpi.data,
            password = hashed_password)
        
        db.session.add(registro)
        db.session.commit()

        # condicion para  verificar si ese unica en email y contraseña
        user = User.query.filter_by(email=forms.RegistrationForm().email.data).first()
        if user and bcrypt.check_password_hash(user.password, forms.RegistrationForm().password.data):
            login_user(user, remember=True)
        return redirect(url_for('hello_world'))
    
    ####  PARA INGRESAR CON EL USUARIO GUARDADO ###
    if forms.LoginForm().validate_on_submit():
        user = User.query.filter_by(email = forms.LoginForm().email.data).first()
        if user and bcrypt.check_password_hash(user.password, forms.LoginForm().password.data):
            login_user(user, remember = True)
            return redirect('informe')
    #### PARA REGISTRAR ACTIVIDADES ESPECIFICAS DEL CONTRATO ####    
    if add_form.validate_on_submit():
        add_register = User_Con_Act(
            usuario= category_dict[add_form.usuario.data],
            actividad_contrato = add_form.actividad_contrato.data,
            actividad_resuelta = add_form.actividad_resuelta.data
        )
        db.session.add(add_register)
        db.session.commit()
      
        return render_template('index.html', 
            login_form = forms.LoginForm(),
            register_form = forms.RegistrationForm(),
            add_form= add_form
            )

    return render_template('index.html', 
        login_form = forms.LoginForm(),
        register_form = forms.RegistrationForm(),
        add_form=add_form
        )

@app.route('/delete', methods =['GET', 'POST'])
def delete():
    # ID e INDIVIDUO PARA DESARROLLO
    user_id= current_user.id
    individuo = User.query.filter_by(id=user_id).with_entities(User.usuario).first()[0]
    
    #BASES DE DATOS#
    usuarios = User.query.filter_by(id=user_id).first()
    registros = User_Act.query.filter_by(usuario=individuo).all()
    actividades = User_Con_Act.query.filter_by(usuario=individuo).all()
    
    # BASE DE TABLA OBSERVADA EN ELIMINAR 
    usuarios_table = User.query.all()
    
    ### PARA CAMBIAR ALGUN REGISTRO ###
    if request.form.get('editar') =='editado':
        
        if request.form.get('new_usuario')=='editar':
            usuarios.usuario =request.form.get('newusuario')
            for u in registros:
                u.usuario = request.form.get('newusuario')
            for u in actividades:
                u.usuario = request.form.get('newusuario')
        
        elif request.form.get('new_dpi')=='editar':
            usuarios.dpi = request.form.get('newdpi')
        
        elif request.form.get('new_contrato')=='editar':
            usuarios.no_contrato  = request.form.get('newcontrato')
            for u in registros:
                u.no_contrato = request.form.get('newcontrato')
        
        elif request.form.get('new_acuerdo')=='editar':
            usuarios.no_acuerdo =request.form.get('newactividad')
            for u in registros:
                u.no_acuerdo = request.form.get('newactividad')

        db.session.commit()
        return render_template('delete.html', table=usuarios, usuarios=usuarios_table) 
    
    ### PARA ELIMINAR REGISTRO ###
    if request.form.get('borrar')=='eliminar':
        if request.form.get('deleteit') == str(current_user.id):
            User.query.filter_by(id=user_id).delete()
            for u in registros:
                db.session.delete(u)
            for u in actividades:
                db.session.delete(u)
            db.session.commit()

            return redirect(url_for('hello_world'))
        
        else:        
            flash('Solocitud no permitida')
            return render_template('delete.html', table = usuarios, usuarios = usuarios_table)        
    
    ### PARA SALIR DEL USUARIO ###
    if (request.method == "POST") & (request.form.get('post_header') == 'log out'):
        logout_user()
        return redirect(url_for('hello_world')) 

    return render_template('delete.html', table = usuarios, usuarios = usuarios_table)