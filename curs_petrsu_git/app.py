from flask import Flask,render_template,request,redirect,session, url_for,send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_required
from flask_login import LoginManager
from flask_login import UserMixin, login_user,logout_user
import enum
from flask_login import current_user
from Models import Courseworks,User,Message
from db import db
import datetime
import os
from flask import flash
from werkzeug.security import generate_password_hash, check_password_hash
app =Flask(__name__)
app.secret_key = 'my_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///curs_db.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        print(request.form['username'])
        print(request.form['password'])
        user = User.query.filter_by(username=request.form['username']).first()
        if user is None or not check_password_hash(user.password, request.form['password']):
            return 'неверный логин или пароль'
        login_user(user)

        return redirect(url_for('index'))
    return '''
           <form action = "" method = "post">
              <p>Логин<input type = "text" name = "username"/></p>
              <p>Пароль<input type = "text" name = "password"/></p>
              <p><input type = "submit" value = "Login"/></p>
           </form>
           '''


@app.route('/login/exit')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@login_manager.user_loader
def load_user(user_id):

    print(user_id)
    return User.query.get(int(user_id))


@app.route('/index',methods=['POST','GET'])
@login_required
def index():
    #TODO определять студент или препод
    #todo генерация отчетов
    #TODO определять учебный семестр
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    if (request.method == 'POST'):
        conditions = []
        AND_conditions = []
        OR_conditions1 = []
        OR_conditions2 = []
        print(request.form)
        from sqlalchemy import or_, and_
        if (request.form['name'] != ''):
            AND_conditions.append(Courseworks.studentName == request.form['name'])
        if (request.form['adviser-name'] != ''):
            AND_conditions.append(Courseworks.tutor_name == request.form['adviser-name'])

        if (request.form['department'] != ''):
            AND_conditions.append(Courseworks.departament == request.form['department'])

        flatten=False


        if (request.form['years'] != ''):
            years = request.form.getlist('years')
            print(years)
            if len(years)>1:
                OR_conditions1 = [Courseworks.year == year1 for year1 in years]
            else:
                AND_conditions.append(Courseworks.year==request.form['years'])

        if (request.form['groups'] != ''):
            grps = request.form.getlist('groups')
            print(grps)
            if len(grps) > 1:
                OR_conditions2 = [Courseworks.group == grp for grp in grps]
            else:
                AND_conditions.append(Courseworks.group == request.form['groups'])

        if OR_conditions1:
            conditions = or_(*OR_conditions1), and_(*AND_conditions)
        else:
            conditions = AND_conditions
        if OR_conditions2:
            conditions = or_(*OR_conditions2), and_(*conditions)
        else:
            conditions = conditions

        if (request.form['group-method'] == 'flatten'):
            flatten=True
        # ('sort-method', 'by-student-name'), ('sort-order', 'ascending')
        if (request.form['sort-method'] == 'by-student-name'):
            if(request.form['sort-order'] == 'ascending'):
                response=Courseworks.query.filter(*conditions).order_by(Courseworks.year, Courseworks.departament,
                                                                        Courseworks.group, Courseworks.student,
                                                                        Courseworks.studentName).all()
            else:
                response=Courseworks.query.filter(*conditions).order_by(Courseworks.year, Courseworks.departament,
                                                                        Courseworks.group, Courseworks.student,
                                                                        Courseworks.studentName.desc()).all()
        elif(request.form['sort-method'] == 'by-adviser-name'):
            if (request.form['sort-order'] == 'ascending'):
                response = Courseworks.query.filter(*conditions).order_by(Courseworks.year, Courseworks.departament,
                                                                          Courseworks.group, Courseworks.student,
                                                                          Courseworks.tutor_name).all()
            else:
                response = Courseworks.query.filter(*conditions).order_by(Courseworks.year, Courseworks.departament,
                                                                          Courseworks.group, Courseworks.student,
                                                                          Courseworks.tutor_name.desc()).all()
        else:
            if (request.form['sort-order'] == 'ascending'):
                response = Courseworks.query.filter(*conditions).order_by(Courseworks.year, Courseworks.departament,
                                                                          Courseworks.student,
                                                                          Courseworks.group).all()
            else:
                response = Courseworks.query.filter(*conditions).order_by(Courseworks.year.desc(), Courseworks.departament,
                                                                          Courseworks.student,
                                                                          Courseworks.group).all()
        counter=0
        for e in response:
            counter += 1
            print(str(counter)+" "+str(e.year)+" "+e.departament+" "+e.group+" "+e.title+" "+e.studentName+" "+e.tutor_name +" "+e.student)

        current_year = datetime.datetime.now().year
        # current_year+=5
        print("Сейчас "+str(current_year))
        #TODO для 4,5,6 курса разные поля в таблицах
        #TODO помечать поздно загруженные работы
        return render_template("curs_show.html", data=response,flatten=flatten,
                               curr_year=current_year,anchor='start_table',file_exists=file_exists)

    else:

        current_year = datetime.datetime.now().year
        return render_template("curs_show.html",curr_year=current_year)

@app.route('/')
def anchor():
    return redirect(url_for('index', _anchor='start_table'))


@app.route('/download/<username>/<year>/<filename>')
@login_required
def download(filename,username,year):
    # Сформируй путь к файлу
    # file_path2 = os.path.join(F'storage/{username}/{year}/{filename}', filename)
    file_path = F'./storage/{username}/{year}/{filename}'
    # print(file_path2)
    # Проверь, существует ли файл
    if os.path.isfile(file_path):
        # Верни файл для скачивания
        return send_file(file_path, as_attachment=False)

    # Если файл не существует, верни ошибку
    return "Файл не найден"


def file_exists(filename,username,year):
    file_path = F'./storage/{username}/{year}/{filename}'
    print('проверяем файл')
    return os.path.isfile(file_path)


@app.route('/register',methods=['POST','GET'])
@login_required
def reg():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    #TODO определять студент или препод ( для преподов пока что заглушка?)
    # TODO: определять учебный год
    available_years=Courseworks.query.filter(Courseworks.student == current_user.username)\
        .group_by(Courseworks.year).order_by(Courseworks.year.desc()).all()
    print("Для пользователя "+current_user.username+" есть записи за след. года")
    # for e in available_years:
    #     print(e.year)
    # av_years = [y.__dict__ for y in available_years]
    # print(av_years[0]["year"])

    av_years = []
    for e in available_years:

        av_years.append(e.year)

    cur_year=datetime.datetime.now().year
    if cur_year not in av_years:
        # available_years.append(Courseworks(year=cur_year))
        available_years.insert(0, Courseworks(year=cur_year))
        print('нет работ за текущий год, добавляем год в список')
    for e in available_years:
        print(e.year)


    chosen_year = cur_year
    if (request.method == 'POST'):

        print(request.form)
        years = request.form.get('years')
        #обработка НАЙТИ
        if years is not None:
            session['chosen_year']=years
            print('POST проверяем работу за выбранный год')
            response = Courseworks.query.filter(Courseworks.student == current_user.username,
                                                Courseworks.year == years).first()
            print(response)
            if response:
                print("выводим работу за выбранный год")
                return render_template("register_work.html", stud_name=current_user.first_name,
                                       group=response.group, curs=response.group[2:3],
                                       year=response.year,title=response.title,
                                       tutor_name=response.tutor_name, tutor_status=response.tutor_status,
                                       tutor_rank=response.tutor_rank, tutor_pos=response.tutor_pos,
                                       departament=response.departament, available_years=available_years,
                                       chosen_year=years)
            else:
                flash('Нет данных за выбранный год!', 'message')
                return render_template("register_work.html", stud_name=current_user.first_name,
                                       group=current_user.cur_group_or_dep, curs=current_user.cur_group_or_dep[2:3],
                                       year=chosen_year, title="",
                                       tutor_name="", tutor_status="",
                                       tutor_rank="", tutor_pos="",
                                       departament="", available_years=available_years,
                                       chosen_year=years)

        # обработка ОТПРАВИТЬ
        #TODO ЗАМЕНИТЬ НА СЕССИИ

        _year = session.get('chosen_year')
        if _year is not None and not _year=='':
            chosen_year=_year
            print('пробуем записать работу за Выбранный год')
            print(chosen_year)
            replace_work = Courseworks.query.filter(Courseworks.student == current_user.username,
                                                    Courseworks.year == chosen_year).first()
            if replace_work:
                print('за выбранный год работа есть')
            else:
                print("не получилось найти работу за выбранный год")
        else:
            print('пробуем записать работу за ТЕКУЩИЙ год')
            print(chosen_year)
            replace_work = Courseworks.query.filter(Courseworks.student == current_user.username,
                                                Courseworks.year == cur_year).first()

        if replace_work:
            print('перезаписываем данные за текущий или выбранный год')
            replace_work.title=request.form['title']
            replace_work.tutor_name=request.form['adviser-name']
            replace_work.tutor_pos = request.form['adviser-position']
            replace_work.tutor_status = request.form['adviser-status']
            replace_work.tutor_rank = request.form['adviser-rank']
            replace_work.departament=request.form['department']
            print(replace_work.group)
            print(replace_work.year)
            db.session.add(replace_work)
            db.session.commit()
            print(chosen_year)
            flash('Данные успешно обновлены!', 'message')
            print('обновили данные')

            return render_template("register_work.html", stud_name=current_user.first_name,
                                   group=replace_work.group, curs=replace_work.group[2:3],
                                   year=chosen_year, title=request.form['title'],
                                   tutor_name=request.form['adviser-name'], tutor_status=request.form['adviser-status'],
                                   tutor_rank=request.form['adviser-rank'], tutor_pos=request.form['adviser-position'],
                                   departament=request.form['department'],available_years=available_years,
                                   chosen_year=replace_work.year)
        print('записей нет, делаем новую')
        new_work=Courseworks(title=request.form['title'],group=current_user.cur_group_or_dep,
                             departament=request.form['department'],student=current_user.username,
                             studentName=current_user.first_name,tutor_name=request.form['adviser-name'],
                             tutor_rank=request.form['adviser-rank'],
                             tutor_status=request.form['adviser-status'],tutor_pos=request.form['adviser-position'],
                             year=cur_year,link='test/test')
        db.session.add(new_work)
        db.session.commit()
        flash('Данные успешно записаны!', 'message')
        print('записали данные')
        return render_template("register_work.html", stud_name=current_user.first_name,
                               group=current_user.cur_group_or_dep, curs=current_user.cur_group_or_dep[2:3],
                               year=cur_year, title=request.form['title'],
                               tutor_name=request.form['adviser-name'], tutor_status=request.form['adviser-status'],
                               tutor_rank=request.form['adviser-rank'], tutor_pos=request.form['adviser-position'],
                               departament=request.form['department'],available_years=available_years)

    else:
        session['chosen_year'] = cur_year
        print('GET проверяем актуальные работы за ',cur_year)
        print(current_user.first_name)
        response = Courseworks.query.filter(Courseworks.group == current_user.cur_group_or_dep,
                                            Courseworks.student == current_user.username,
                                            Courseworks.year == chosen_year).first()


        print(response)
        if response:
            print("выводим актуальную работу")
            print(response.tutor_status)

            return render_template("register_work.html", stud_name=current_user.first_name,
                                   group=current_user.cur_group_or_dep, curs=current_user.cur_group_or_dep[2:3],
                                   year=chosen_year,title=response.title,
                                   tutor_name=response.tutor_name,tutor_status=response.tutor_status,
                                   tutor_rank=response.tutor_rank,tutor_pos=response.tutor_pos,
                                   departament=response.departament,available_years=available_years,
                                   chosen_year=chosen_year)

        print('актуальных работ нет')
        return render_template("register_work.html",stud_name=current_user.first_name,
                               group=current_user.cur_group_or_dep,curs=current_user.cur_group_or_dep[2:3],year=chosen_year,
                               available_years=available_years,chosen_year=chosen_year)


@app.route('/report',methods=['POST','GET'])
@login_required
def report():
    return "здесь будем загружать pdf с отчетом"


@app.route('/list_unreg',methods=['POST','GET'])
@login_required
def report_unreg():
    return "здесь будем загружать pdf со студентами, не загрузившими работы"


@app.route('/upload',methods=['POST','GET'])
@login_required
def load():
    #TODO проверять курс и выводить нужные поля для загрузки
    # TODO определять студент или препод ( для преподов пока что заглушка?)
    #todo определять учеб год
    available_years=Courseworks.query.filter(Courseworks.student == current_user.username)\
        .group_by(Courseworks.year).order_by(Courseworks.year.desc()).all()
    print("Для пользователя "+current_user.username+" есть записи за след. года")
    for e in available_years:
        print(e.year)
    if (request.method == 'GET'):
        chose_year = datetime.datetime.now().year

        return render_template("load.html",year=chose_year,curs=current_user.cur_group_or_dep[2:3],
                               group=current_user.cur_group_or_dep,stud_name=current_user.first_name,
                               available_years=available_years)
    else:
        years = request.form.get('years')

        # обработка НАЙТИ
        if years is not None:
            session['year'] = years
            print("выбран ", years)
            print('POST проверяем работу за выбранный год (ЗАГРУЗКА)')
            response = Courseworks.query.filter(Courseworks.student == current_user.username,
                                                Courseworks.year == years).first()

            print(response)
            if response:
                print("выводим поля для загрузки за выбранный год (ЗАГРУЗКА)")
                print(response.tutor_status)

                return render_template("load.html", year=years, curs=response.group[2:3],
                                       group=response.group, stud_name=current_user.first_name,
                                       available_years=available_years)
            else:
                # flash('Нет данных за выбранный год!', 'message')
                return render_template("load.html", year=2023, curs=current_user.cur_group_or_dep[2:3],
                                       group=current_user.cur_group_or_dep, stud_name=current_user.first_name,
                                       available_years=available_years)
        print(request.form)
        chose_year = session.get('year')
        print(chose_year)

        if not chose_year:
            print('!@!**')
            chose_year = datetime.datetime.now().year
        print('загружаем на ',chose_year)
        pdf_file = request.files['doc-file']

        pdf_content = pdf_file.read()
        print(request.form['for-doc'])
        work_name=''
        #TODO ЗАПИСЫВАТЬ ДАТУ ЗАГРУЗКИ (или сразу проверять актуальность)
        #TODO записывать путь к отчету
        if request.form['for-doc']=='int-report':
            work_name='report'
        elif request.form['for-doc']=='int-slides':
            work_name='slides'
        elif request.form['for-doc'] == 'fin-preport':
            work_name = 'practic_report'
        elif request.form['for-doc'] == 'fin-report':
            work_name = 'final_report'
        elif request.form['for-doc'] == 'fin-slides':
            work_name = 'final_slides'
        elif request.form['for-doc'] == 'fin-antiplagiat':
            work_name = 'antiplagiat'
        elif request.form['for-doc'] == 'fin-sup-review':
            work_name = 'review'
        elif request.form['for-doc'] == 'fin-review':
            work_name = 'final_review'
        else:
            return 'неизвестная ошибка'
        os.makedirs(F'storage/{current_user.username}/{chose_year}', exist_ok=True)
        with open(F'storage/{current_user.username}/{chose_year}/{work_name}.pdf', 'wb') as f:
            f.write(pdf_content)
        return 'записали'

if __name__=="__main__":

    app.run(debug=True)
    db.create_all()
