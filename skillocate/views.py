from skillocate import app, auth
from skillocate import db
from skillocate.models import *
from flask import Flask, request, jsonify, abort, session, g
from flask_sqlalchemy import SQLAlchemy

auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(email_or_token,password):
    # first try to authenticate by token
    print("TEST")
    print(email_or_token)
    user = User.verify_auth_token(email_or_token)
    if not user:
        # try to authenticate with username/password
        user = User.query.filter_by(email = email_or_token).first()
        if not user or not user.check_password(password):
            return False
    g.user = user
    return True

@app.route('/api/skilltypes', methods=['GET'])
@auth.login_required
def skill_types():
    user = g.user
    retval = get_skilltypes(user)
    return jsonify(data=retval)

@app.route('/api/profilepicture', methods=['POST'])
@auth.login_required
def upload_profile_picture():
    extension = request.json['extension']
    data = request.json['data']

    if data and allowed_file("." + extension):
        userdetails = UserDetails.queryfilter_by(user=g.user.iduser).first()
        if userdetails.rel_profilepicture is None:
            picture = File(data=data, extension=extension, filename='profilepicture')
            db.session.add(picture)
            db.session.commit()
            profile.profilepicture = picture.idfile
        else:
            picture = userdetails.rel_profilepicture
            picture.data = base64.b64decode(data)
        db.session.commit()


    return jsonify(response='success')

@app.route('/api/profilepicture', methods=['GET'])
@auth.login_required
def get_profile_picture():

    user = g.user
    img = userdetails = UserDetails.queryfilter_by(user=g.user.iduser).first().rel_profilepicture
    if img is None:
        return abort(404)
    return jsonify(img.serialize)




@app.route('/api/signin', methods=['POST'])
def login():
    json_data = request.json
    email = json_data['email']
    password = json_data['password']

    user = User.query.filter_by(email=email).first()

    if user is None:
        return jsonify(response=False)

    if user.check_password(password):
        token = user.generate_auth_token()
        return jsonify(response={ 'token': token.decode('ascii'), 'iduser' : user.iduser })

    return abort(401)


@app.route('/api/signout', methods=['POST'])
def logout():
    g.user = None
    return jsonify(response='success')

@app.route('/api/setLocale', methods=['POST'])
def set_locale():
    session['locale'] = request.json['locale']
    return jsonify(response='success')

@app.route('/api/signup', methods=['POST'])
def signup():
    json_data = request.json
    email = json_data['email']
    password = json_data['password']
    firstname = json_data['firstname']
    lastname = json_data['lastname']
    
    user = User.query.filter_by(email=email).first()
    
    if user is not None:
        return jsonify(response='user already exists')
    
    

    user = User(email=email, password=password)
    db.session.add(user)
    db.session.commit()

    userdetail = UserDetail(firstname=firstname, lastname=lastname, email=email, user=user.iduser)
    db.session.add(userdetail)
    db.session.commit()
    return jsonify(response='success')

############# USERDETAILS #############
@app.route('/api/userdetail', methods=['GET'])
@auth.login_required
def get_userdetail():
    iduser = request.args.get('user')
    
    if iduser is None:
        userdetail = UserDetail.query.filter_by(user=g.user.iduser).first()
    else:
        userdetail = UserDetail.query.filter_by(user=iduser).first()

    if userdetail is None:
        return abort(404)

    return jsonify(data=userdetail.serialize)

@app.route('/api/userdetail', methods=['PUT'])
@auth.login_required
def update_userdetail():
    if not request.json:
        abort(400)
    iduserdetail = request.json['iduserdetail']

    userdetail = UserDetail.query.get(iduserdetail)

    if userdetail is None:
        abort(404)

    userdetail.update(request.json)
    db.session.commit()

    return jsonify(data=userdetail.serialize)
############# /USERDETAILS #############
    

@app.route('/api/options', methods=['GET'])
@auth.login_required
def get_options():
    table = request.args['table']
    field = request.args['field']

    t = get_class_by_tablename(table.lower())
    c = getattr(t,field.lower())
    query = db.session.query(c.distinct().label("option"))
    options = [{"option":row.option} for row in query.all()]
    return jsonify(data=options)

@app.route('/api/workexperience', methods=['GET'])
@auth.login_required
def get_user_workexperience():
    user = g.user
    workexperience = WorkExperience.query.filter_by(profile=user.profile).all()
    if workexperience is None:
        return abort(404)
    retval = []
    for w in workexperience:
            retval.append(w.serialize)

    return jsonify(data=retval)

@app.route('/api/workexperience', methods=['POST'])
@auth.login_required
def create_workexperience():
    idworkexperience = request.json['idworkexperience']

    profile = g.user.rel_profile

    if idworkexperience is None:
        workexperience = WorkExperience(request.json, profile.idprofile)
        db.session.add(workexperience)
    else:
        workexperience = WorkExperience.query.get(idworkexperience)
        workexperience.update(request.json)

    db.session.commit()

    return jsonify(idrecord="{idrecord}".format(idrecord=workexperience.idworkexperience))

@app.route('/api/merits', methods=['GET'])
@auth.login_required
def get_user_merits():
    user = g.user
    merits = Merit.query.filter_by(profile=user.profile).all()
    if merits is None:
        return abort(404)
    retval = []
    for m in merits:
            retval.append(m.serialize)

    return jsonify(data=retval)

@app.route('/api/merit', methods=['POST'])
@auth.login_required
def create_merit():
    idmerit = request.json['idmerit']
    profile = g.user.rel_profile

    if idmerit is None:
        merit = Merit(request.json, profile.idprofile)
        db.session.add(merit)
    else:
        merit = Merit.query.get(idmerit)
        merit.update(request.json)

    db.session.commit()

    return jsonify(idrecord="{idrecord}".format(idrecord=merit.idmerit))

############# EDUCATIONS #############
@app.route('/api/users/<int:iduser>/educations', methods=['GET'])
@auth.login_required
def get_educations(iduser):
    educations = Education.query.filter_by(user=iduser).all()
    if educations is None:
        return abort(404)
    retval = []
    for edu in educations:
        retval.append(edu.serialize)

    return jsonify(data=retval)

@app.route('/api/educations/<int:ideducation>', methods=['GET'])
@auth.login_required
def get_education(iduser, ideducation):
    retval = Education.query.get(ideducation)
    if retval is None:
        return abort(404)
    return jsonify(data=retval)

    

@app.route('/api/educations', methods=['GET'])
@auth.login_required
def get_all_educations():
    retval = []
    educations = Education.query.all()
    for edu in educations:
        retval.append(edu.serialize)
    return jsonify(data=retval)

@app.route('/api/educations', methods=['POST'])
@auth.login_required
def create_education():
    if not request.json:
        abort(400)
    
    education = Education(request.json, g.user.iduser)
    db.session.add(education)
    db.session.commit()

    return jsonify(data=education.serialize)

@app.route('/api/educations', methods=['PUT'])
@auth.login_required
def update_education():
    if not request.json:
        abort(400)

    ideducation = request.json['ideducation']

    if ideducation is None:
        abort(404)

    education = Education.query.get(ideducation)
    education.update(request.json)
    db.session.commit()

    return jsonify(data=education.serialize)
############# /EDUCATIONS #############

@app.route('/api/skills', methods=['GET'])
@auth.login_required
def get_user_skills():
    user = g.user
    skills = Skill.query.filter_by(profile=user.profile).all()
    if skills is None:
        return abort(404)
    retval = []
    for s in skills:
        retval.append(s.serialize)

    return jsonify(data=retval)


@app.route('/api/skill', methods=['POST'])
@auth.login_required
def update_skill():

    idskill = request.json['idskill']
    profile = g.user.rel_profile

    if idskill is None:
        skill = Skill(request.json, profile.idprofile)
        db.session.add(skill)
    else:
        skill = Skill.query.get(idskill)
        skill.update(request.json)

    db.session.commit()

    return jsonify(idrecord="{idrecord}".format(idrecord=skill.idskill))

@app.route('/api/experiences', methods=['GET'])
@auth.login_required
def get_user_experiences():
    user = g.user
    experiences = Experience.query.filter_by(profile=user.profile).all()

    if experiences is None:
        return abort(404)
    retval = []
    for e in experiences:
            retval.append(e.serialize)

    return jsonify(data=retval)


@app.route('/api/experience', methods=['POST'])
@auth.login_required
def update_experience():
    idexperience = request.json['idexperience']
    profile = g.user.rel_profile

    if idexperience is None:
        experience = Experience(request.json, profile.idprofile)
        db.session.add(experience)
    else:
        experience = Experience.query.get(idexperience)
        experience.update(request.json)

    db.session.commit()

    return jsonify(idrecord="{idrecord}".format(idrecord=experience.idexperience))

@app.route('/api/languages', methods=['GET'])
@auth.login_required
def get_languages():
    user = g.user
    languages = Language.query.filter_by(profile=user.profile).all()
    if languages is None:
        return abort(404)
    retval = []
    for l in languages:
            retval.append(l.serialize)

    return jsonify(data=retval)


@app.route('/api/language', methods=['POST'])
@auth.login_required
def update_language():
    idlanguage = request.json['idlanguage']

    profile = g.user.rel_profile

    if idlanguage is None:
        language = Language(request.json, profile.idprofile)
        db.session.add(language)

    else:
        language = Language.query.get(idlanguage)
        language.update(request.json)

    db.session.commit()

    return jsonify(idrecord="{idrecord}".format(idrecord=language.idlanguage))

@app.route('/api/publications', methods=['GET'])
@auth.login_required
def get_user_publications():
    user = g.user
    publications = Publication.query.filter_by(profile=user.profile).all()
    if publications is None:
        return abort(404)
    retval = []
    for p in publications:
        retval.append(p.serialize)

    return jsonify(data=retval)


@app.route('/api/publication', methods=['POST'])
@auth.login_required
def create_publication():
    idpublication = request.json['idpublication']
    profile = g.user.rel_profile

    if idpublication is None:
        publication = Publication(request.json, profile.idprofile)
        db.session.add(publication)
    else:
        publication = Publication.query.get(idpublication)
        publication.update(request.json)

    db.session.commit()

    return jsonify(idrecord="{idrecord}".format(idrecord=publication.idpublication))

@app.route('/api/projects', methods=['GET'])
@auth.login_required
def get_user_projects():
    user = g.user
    projects = Project.query.filter_by(profile=user.profile).all()
    if projects is None:
        return abort(404)
    retval = []
    for p in projects:
            retval.append(p.serialize)

    return jsonify(data=retval)

@app.route('/api/customers',methods=['GET'])
@auth.login_required
def get_customeroptions():
    customers = Customer.query.all()
    retval = []
    for c in customers:
        retval.append(c.serialize)
    return jsonify(data=retval)

@app.route('/api/resourcerequest',methods=["GET"])
@auth.login_required
def get_resourcerequests():

    resourceRequests = ResourceRequest.query.all()
    if resourceRequests is None:
        return abort(404)
   
    return jsonify(data=[r.serialize for r in resourceRequests])

@app.route('/api/resourcerequest',methods=["POST"])
@auth.login_required
def save_resourcerequest():
    idresourcerequest = request.json['idresourcerequest']

    customer = request.json['customer']

    if customer is None:
        customer = Customer({'name' : request.json['customername']})
        db.session.add(customer)
        db.session.commit()
    else:
        customer = Customer.query.get(customer['idcustomer'])

    if idresourcerequest is None:
        resourceRequest = ResourceRequest(request.json)
        resourceRequest.customer = customer.idcustomer
        db.session.add(resourceRequest)
    else:
        resourceRequest = ResourceRequest.query.get(idresourcerequest)
        resourceRequest.update(request.json)

    resourceRequest.customer = request.json['customer']['idcustomer']
    db.session.commit()

    return jsonify(idrecord="{idrecord}".format(idrecord=resourceRequest.idresourcerequest))

@app.route('/api/competenceprofiles',methods=['GET'])
@auth.login_required
def get_competenceprofiles():
    #TODO: kontrollera admin
    idprofile = request.args.get('idprofile')

    if idprofile is not None:
        profile = Profile.query.get(idprofile)
        profiles = CompetenceProfile.query.filter_by(profile=profile.idprofile).all()
    else:
        profiles = CompetenceProfile.query.all()

    return jsonify(data=[p.serialize_relations for p in profiles])

@app.route('/api/competenceProfile',methods=['POST'])
@auth.login_required
def save_competenceprofiles():

    profile = g.user.rel_profile
    experiences = request.json['experiences']
    publications = request.json['publications']
    projects = request.json['projects']
    educations = request.json['educations']

    workExperiences = request.json['workExperiences']
    languages = request.json['languages']

    skills = request.json['skills']
    merits = request.json['merits']

    idcompetenceprofile = request.json['idcompetenceprofile']

    if idcompetenceprofile is None:
        competenceProfile = CompetenceProfile(request.json, profile.idprofile)
        db.session.add(competenceProfile)
        db.session.commit()
    else:
        competenceProfile = CompetenceProfile.query.get(idcompetenceprofile)
        competenceProfile.update(request.json)

    competenceProfile.workexperiences = [WorkExperience.query.get(w['idworkexperience'])  for w in workExperiences]
    competenceProfile.educations = [Education.query.get(e['ideducation'])  for e in educations]
    competenceProfile.experiences = [Experience.query.get(e['idexperience'])  for e in experiences]
    competenceProfile.skills = [Skill.query.get(s['idskill'])  for s in skills]
    competenceProfile.publications = [Publication.query.get(p['idpublication'])  for p in publications]
    competenceProfile.languages = [Language.query.get(l['idlanguage'])  for l in languages]
    competenceProfile.projects = [Project.query.get(p['idproject'])  for p in projects]
    competenceProfile.merits = [Merit.query.get(m['idmerit'])  for m in merits]

    db.session.commit()
    return jsonify(idrecord="{idrecord}".format(idrecord=competenceProfile.idcompetenceprofile))

@app.route('/api/candidates',methods=['GET'])
@auth.login_required
def get_candidates():
    #TODO: kontrollera admin
    idcandidate = request.args.get('idcandidate')

    if idcandidate is not None:
        return jsonify(data=Candidate.query.get(idcandidate).serialize)

    idresourcerequest = request.args.get('resourcerequest')

    if idresourcerequest is not None:
        candidates = Candidate.query.filter_by(resourcerequest=idresourcerequest).all()
    else:
        candidates = Candidate.query.all()
    try:
        print([c.serialize for c in candidates])
    except Exception as err:
        print(err)
    return jsonify(data=[c.serialize for c in candidates])

@app.route('/api/candidates',methods=["POST"])
@auth.login_required
def save_candidate():

    idcandidate = request.json['idcandidate']

    resourcerequest = ResourceRequest.query.get(request.json['resourcerequest']['idresourcerequest'])

    competenceprofile = CompetenceProfile.query.get(request.json['competenceprofile']['idcompetenceprofile'])

    if resourcerequest is None or competenceprofile is None:
        abort(404)

    if idcandidate is None:
        candidate = Candidate(request.json)
        candidate.resourcerequest = resourcerequest.idresourcerequest
        candidate.competenceprofile = competenceprofile.idcompetenceprofile
        db.session.add(candidate)
    else:
        candidate = Candidate.query.get(idcandidate)
        candidate.update(request.json)

    db.session.commit()

    return jsonify(idrecord="{idrecord}".format(idrecord=candidate.idcandidate))

@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
  return response

@app.route('/api/project', methods=['POST'])
@auth.login_required
def create_project():

    idproject = request.json['idproject']
    profile = g.user.rel_profile

    customer = request.json['customer']

    if customer is None:
        customer = Customer({'name' : request.json['customername']})
        db.session.add(customer)
        db.session.commit()
    else:
        customer = Customer.query.get(customer['idcustomer'])


    if idproject is None:
        project = Project(request.json,profile.idprofile)
        project.customer = customer.idcustomer
        db.session.add(project)

        db.session.commit()


    else:
        project = Project.query.get(idproject)
        project.update(request.json)
        db.session.commit()



    return jsonify(idrecord="{idrecord}".format(idrecord=idproject))

@app.route('/api/deleterecord', methods=['DELETE'])
@auth.login_required
def delete_object():
    table = request.args['table']
    idrecord = request.args['idrecord']
    record = get_class_by_tablename(table)
    db.session.delete(record.query.get(idrecord))
    db.session.commit()
    return jsonify(response='success')

@app.route('/api/test',methods=['GET'])
def test():
    return jsonify(response='hello')

@app.route('/api/search', methods=['POST'])
def search():
    print(request.json)
    data = request.json['query']

    if len(data) < 2:
        print("fsdfsd")
        return jsonify({})

    res = SearchResult()
    profiles = []
    es = Elasticsearch()
    search_body = {
        "from": 0,
        "size": 10,
        "query": {
            "query_string": {
                "query": "*" + data + "*"
            }
        }
    }

    for e in es.search(body=search_body).get('hits').get('hits'):
        src = e.get('_source')
        profiles.append(src['profile'])
        if e.get('_type') == 'education':
            education = Education.query.get(src['ideducation'])
            res.educations.append(education.serialize)

        if e.get('_type') == 'skill':
            skill = Skill.query.get(src['idskill'])
            res.skills.append(skill.serialize)

        if e.get('_type') == 'language':
            language = Language.query.get(src['idlanguage'])
            res.languages.append(language.serialize)
        if e.get('_type') == 'merit':
            merit = Merit.query.get(src['idmerit'])
            res.merits.append(merit.serialize)

        if e.get('_type') == 'publication':
            publication = Publication.query.get(src['idpublication'])
            res.publications.append(publication.serialize)
        if e.get('_type') == 'experience':
            experience = Experience.query.get(src['idexperience'])
            res.experiences.append(experience.serialize)
        if e.get('_type') == 'workexperience':
            workexperience = WorkExperience.query.get(src['idworkexperience'])
            res.workexperiences.append(workexperience.serialize)
        if e.get('_type') == 'project':
            project = Project.query.get(src['idproject'])
            res.projects.append(project.serialize)

    for p in set(profiles):
        res.profiles.append(Profile.query.get(p).serialize)

    return jsonify(res.serialize)