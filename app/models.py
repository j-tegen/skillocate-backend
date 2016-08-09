from werkzeug import generate_password_hash, check_password_hash
from datetime import *
from app import db
from sqlalchemy import event
from sqlalchemy.dialects.postgresql import BYTEA
from elasticsearch import Elasticsearch
from itsdangerous import (TimedJSONWebSignatureSerializer
                            as Serializer, BadSignature, SignatureExpired)
import base64
import config

######## DATABASE MODEL #########


workExperienceProfile = db.Table('workexperienceprofile',
      db.Column('idworkexperience',db.Integer,db.ForeignKey('workexperience.idworkexperience')),
      db.Column('idprofile',db.Integer,db.ForeignKey('profile.idprofile'))
)

educationProfile = db.Table('educationprofile',
      db.Column('ideducation',db.Integer,db.ForeignKey('education.ideducation')),
      db.Column('idprofile',db.Integer,db.ForeignKey('profile.idprofile'))
)

skillProfile = db.Table('skillprofile',
      db.Column('idskill',db.Integer,db.ForeignKey('skill.idskill')),
      db.Column('idprofile',db.Integer,db.ForeignKey('profile.idprofile'))
)

languageProfile = db.Table('languageprofile',
      db.Column('idlanguage',db.Integer,db.ForeignKey('language.idlanguage')),
      db.Column('idprofile',db.Integer,db.ForeignKey('profile.idprofile'))
)

projectProfile = db.Table('projectprofile',
      db.Column('idproject',db.Integer,db.ForeignKey('project.idproject')),
      db.Column('idprofile',db.Integer,db.ForeignKey('profile.idprofile'))
)

experienceProfile = db.Table('experienceprofile',
      db.Column('idexperience',db.Integer,db.ForeignKey('experience.idexperience')),
      db.Column('idprofile',db.Integer,db.ForeignKey('profile.idprofile'))
)

meritProfile = db.Table('meritprofile',
      db.Column('ideducidmeritation',db.Integer,db.ForeignKey('merit.idmerit')),
      db.Column('idprofile',db.Integer,db.ForeignKey('profile.idprofile'))
)

publicationProfile = db.Table('publicationprofile',
      db.Column('idpublication',db.Integer,db.ForeignKey('publication.idpublication')),
      db.Column('idprofile',db.Integer,db.ForeignKey('profile.idprofile'))
)

# class ResourceRequest(db.Model):
#     __tablename__ = "resourcerequest"
#     idresourcerequest = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(72))
#     startdate = db.Column(db.DateTime)
#     enddate = db.Column(db.DateTime)
#     description = db.Column(db.String(4000))
#     externallink = db.Column(db.String(72))
#     customer = db.Column(db.Integer, db.ForeignKey('customer.idcustomer'))
#     rel_customer = db.relationship('Customer', primaryjoin='ResourceRequest.customer == Customer.idcustomer',
#                                   backref=db.backref('resourcerequest', lazy='dynamic'))
#     contactname = db.Column(db.String(128))
#     contactemail = db.Column(db.String(128))

#     def __init__(self, json_data=None):
#         self.title = json_data['title']
#         self.title = json_data['title']
#         self.startdate = json_data['startdate']
#         self.enddate = json_data['enddate']
#         self.description = json_data['description']
#         self.externallink = json_data['externallink']
#         self.contactname = json_data['contactname']
#         self.contactemail = json_data['contactemail']

#     def __repr__(self):
#         return '<ResourceRequest %r>' % (self.title)

#     def update(self, json_data):
#         self.title = json_data['title']
#         self.title = json_data['title']
#         self.startdate = json_data['startdate']
#         self.enddate = json_data['enddate']
#         self.description = json_data['description']
#         self.externallink = json_data['externallink']
#         self.contactname = json_data['contactname']
#         self.contactemail = json_data['contactemail']
#         self.customer = json_data['customer']['idcustomer']

#     @property
#     def serialize_customer(self):
#         if self.rel_customer is not None:
#             return self.rel_customer.serialize
#         else:
#             return ''

#     @property
#     def serialize(self):
#         return {
#             'idresourcerequest' : self.idresourcerequest,
#             'title' : self.title,
#             'startdate' : self.startdate,
#             'enddate' : self.enddate,
#             'description' : self.description,
#             'externallink' : self.externallink,
#             'customer' : self.serialize_customer,
#             'contactname' : self.contactname,
#             'contactemail' : self.contactemail,
#             'descriptive_header': self.serialize_customer['descriptive_header'] + ' - ' + self.title,
#             'descriptive_subheader': self.description
#         }


# Create our database model
class Education(db.Model):
    __tablename__ = "education"
    ideducation = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(72))
    education = db.Column(db.String(72))
    school = db.Column(db.String(72))
    startdate = db.Column(db.DateTime)
    enddate = db.Column(db.DateTime)
    description = db.Column(db.String(512))
    user = db.Column(db.Integer, db.ForeignKey('user.iduser'))
    rel_user = db.relationship('User', primaryjoin='Education.user == User.iduser',
                                  backref=db.backref('education', lazy='dynamic'))
    timestamp = db.Column(db.DateTime, default=datetime.now())

    def __init__(self, json_data=None, user=None):
        self.title = json_data['title']
        self.education = json_data['education']
        self.school = json_data['school']
        self.description = json_data['description']
        self.startdate = json_data['startdate']
        self.enddate = json_data['enddate']
        self.user = user

    def __repr__(self):
        return '<Education %r>' % (self.title)

    def update(self, json_data):
        self.title = json_data['title']
        self.education = json_data['education']
        self.school = json_data['school']
        self.description = json_data['description']
        self.startdate = json_data['startdate']
        self.enddate = json_data['enddate']

    @property
    def serialize(self):
        return {
            'ideducation': self.ideducation,
            'title': self.title,
            'education': self.education,
            'school': self.school,
            'startdate': self.startdate,
            'enddate': self.enddate,
            'description': self.description,
            'user': self.rel_user.serialize,
            'timestamp': self.timestamp,
            'descriptive_header': self.title + ' - ' + self.education,
            'descriptive_subheader': self.school
        }

class WorkExperience(db.Model):
    __tablename__ = "workexperience"

    idworkexperience = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(72))
    employer = db.Column(db.String(72))
    startdate = db.Column(db.DateTime)
    enddate = db.Column(db.DateTime)
    description = db.Column(db.String(512))
    user = db.Column(db.Integer, db.ForeignKey('user.iduser'))
    rel_user = db.relationship('User', primaryjoin='WorkExperience.user == User.iduser',
                                  backref=db.backref('workexperience', lazy='dynamic'))
    timestamp = db.Column(db.DateTime, default=datetime.now())

    def __init__(self, json_data=None, user=None):
        self.title = json_data['title']
        self.employer = json_data['employer']
        self.description = json_data['description']
        self.startdate = json_data['startdate']
        self.enddate = json_data['enddate']
        self.user = user

    def __repr__(self):
        return '<WorkExperience %r>' % (self.title)

    def update(self, json_data):
        self.title = json_data['title']
        self.employer = json_data['employer']
        self.description = json_data['description']
        self.startdate = json_data['startdate']
        self.enddate = json_data['enddate']

    @property
    def serialize(self):
        return {
            'idworkexperience': self.idworkexperience,
            'title': self.title,
            'employer': self.employer,
            'startdate': self.startdate,
            'enddate': self.enddate,
            'description': self.description,
            'user': self.rel_user.serialize,
            'timestamp': self.timestamp,
            'descriptive_header': self.title,
            'descriptive_subheader': self.employer
        }

# class Candidate(db.Model):
#     __tablename__ = "candidate"
#     idcandidate = db.Column(db.Integer, primary_key=True)
#     rate = db.Column(db.Integer)
#     approved = db.Column(db.Integer)

#     profile = db.Column(db.Integer, db.ForeignKey('Profile.idprofile'))
#     rel_profile = db.relationship('profile', primaryjoin='Candidate.profile == Profile.idprofile',
#                                   backref=db.backref('candidate', lazy='dynamic'))

#     resourcerequest = db.Column(db.Integer, db.ForeignKey('resourcerequest.idresourcerequest'))
#     rel_resourcerequest = db.relationship('ResourceRequest', primaryjoin='Candidate.resourcerequest == ResourceRequest.idresourcerequest',
#                                   backref=db.backref('candidate', lazy='dynamic'))

#     def __init__(self, json_data):
#         self.approved = 0
#         self.rate = 0

#     def __repr__(self):
#         return '<Candidate %r>' % (self.rel_profile.rel_profile.serialize['descriptive_header'])

#     def update(self, json_data=None):
#         self.rate = json_data['rate']
#         self.approved = json_data['approved']
#         self.resourcerequest = json_data['resourcerequest']['idresourcerequest']
#         self.profile = json_data['profile']['idprofile']

#     @property
#     def serialize_profile(self):
#         if self.rel_profile is not None:
#             return self.rel_profile.serialize
#         else:
#             return ''

#     @property
#     def serialize_resourcerequest(self):
#         if self.rel_resourcerequest is not None:
#             return self.rel_resourcerequest.serialize
#         else:
#             return ''
#     @property
#     def serialize(self):
#         return {
#             'idcandidate':self.idcandidate,
#             'approved':self.approved,
#             'rate' : self.rate,
#             'profile' : self.serialize_profile,
#             'resourcerequest' : self.serialize_resourcerequest,
#             'profile' : self.rel_profile.rel_profile.serialize,
#             'descriptive_header': self.rel_profile.rel_profile.serialize['descriptive_header'] + ' - '
#                                   + self.rel_profile.serialize['descriptive_header'],
#             'descriptive_subheader': self.rel_profile.rel_profile.serialize['descriptive_subheader']
#         }


class Customer(db.Model):
    __tablename__ = "customer"
    idcustomer = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(72))
    customerno = db.Column(db.String(32))

    def __init__(self, json_data):
        self.name = json_data['name']
        self.customerno = json_data['customerno']

    def __repr__(self):
        return '<Customer %r>' % (self.name)

    def update(self, json_data=None):
        self.name = json_data['name']
        self.customerno = json_data['customerno']

    @property
    def serialize(self):
        return {
            'idcustomer':self.idcustomer,
            'name':self.name,
            'customerno' : self.customerno,
            'descriptive_header': self.name,
            'descriptive_subheader': self.customerno
        }

class Profile(db.Model):
    __tablename__ = "profile"

    idprofile = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    description = db.Column(db.String(4000))
    #TODO: Tags!

    workexperiences = db.relationship('WorkExperience',secondary=workExperienceProfile,
                                      backref=db.backref('profile',lazy='dynamic'))
    educations = db.relationship('Education',secondary=educationProfile,
                                      backref=db.backref('profile',lazy='dynamic'))
    experiences = db.relationship('Experience',secondary=experienceProfile,
                                      backref=db.backref('profile',lazy='dynamic'))
    publications = db.relationship('Publication',secondary=publicationProfile,
                                      backref=db.backref('profile',lazy='dynamic'))
    skills = db.relationship('Skill',secondary=skillProfile,
                                      backref=db.backref('profile',lazy='dynamic'))
    merits = db.relationship('Merit',secondary=meritProfile,
                                      backref=db.backref('profile',lazy='dynamic'))
    projects = db.relationship('Project',secondary=projectProfile,
                                      backref=db.backref('profile',lazy='dynamic'))
    languages = db.relationship('Language',secondary=languageProfile,
                                      backref=db.backref('profile',lazy='dynamic'))
    user = db.Column(db.Integer, db.ForeignKey('user.iduser'))
    rel_user = db.relationship('User', primaryjoin='Profile.user == User.iduser',
                                  backref=db.backref('profile', lazy='dynamic'))

    def __init__(self, json_data=None, user=None):
        self.user=user
        self.name = json_data['name']
        self.description = json_data['description']

    def __repr__(self):
        return '<Profile %r>' % (self.name)

    def update(self, json_data=None):
        self.name = json_data['name']
        self.description = json_data['description']

    @property
    def serialize_relations(self):
        return {
            "idprofile":self.idprofile,
            "name":self.name,
            "user" : self.rel_user.serialize,
            "workexperiences":[w.serialize for w in self.workexperiences],
            "educations":[e.serialize for e in self.educations],
            "languages":[l.serialize for l in self.languages],
            "skills":[s.serialize for s in self.skills],
            "experiences":[e.serialize for e in self.experiences],
            "projects":[p.serialize for p in self.projects],
            "merits":[m.serialize for m in self.merits],
            "publications":[p.serialize for p in self.publications],
            'description' : self.description,
            'descriptive_header': self.name,
            'descriptive_subheader': self.description
        }
    @property
    def serialize(self):
        return {
            "idprofile":self.idprofile,
            "name":self.name,
            "profile" : self.profile,
            "workexperiences":[w.idworkexperience for w in self.workexperiences],
            "educations":[e.ideducation for e in self.educations],
            "languages":[l.idlanguage for l in self.languages],
            "skills":[s.idskill for s in self.skills],
            "experiences":[e.idexperience for e in self.experiences],
            "projects":[p.idproject for p in self.projects],
            "merits":[m.idmerit for m in self.merits],
            "publications":[p.idpublication for p in self.publications],
            'description' : self.description,
            'descriptive_header': self.name,
            'descriptive_subheader': self.description
        }

class Project(db.Model):
    __tablename__ = "project"

    idproject = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(72))
    customer = db.Column(db.Integer, db.ForeignKey('customer.idcustomer'))
    rel_customer = db.relationship('Customer', primaryjoin='Project.customer == Customer.idcustomer',
                                  backref=db.backref('project', lazy='dynamic'))

    hours = db.Column(db.Integer)
    startdate = db.Column(db.DateTime)
    enddate = db.Column(db.DateTime)
    description = db.Column(db.String(512))
    user = db.Column(db.Integer, db.ForeignKey('user.iduser'))
    rel_user = db.relationship('User', primaryjoin='Project.user == User.iduser',
                                  backref=db.backref('project', lazy='dynamic'))
    timestamp = db.Column(db.DateTime, default=datetime.now())

    def __init__(self, json_data=None, user=None):
        self.name = json_data['name']
        self.description = json_data['description']
        self.startdate = json_data['startdate']
        self.enddate = json_data['enddate']
        self.hours = json_data['hours']
        self.user = user

    def __repr__(self):
        return '<Project %r>' % (self.name)

    def update(self, json_data):
        self.name = json_data['name']
        self.customer = json_data['customer']['idcustomer']
        self.description = json_data['description']
        self.startdate = json_data['startdate']
        self.enddate = json_data['enddate']
        self.hours = json_data['hours']

    @property
    def serialize_customer(self):
        if self.rel_customer is not None:
            return self.rel_customer.serialize
        else:
            return ''

    @property
    def serialize(self):
        return {
            'idproject': self.idproject,
            'name': self.name,
            'hours': self.hours,
            'customer': self.serialize_customer,
            'startdate': self.startdate,
            'enddate': self.enddate,
            'description': self.description,
            'user': self.rel_user.serialize,
            'timestamp': self.timestamp,
            'descriptive_header': self.name,
            'descriptive_subheader': self.serialize_customer['name']
        }


class Experience(db.Model):
    __tablename__ = "experience"

    idexperience = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(72))
    startdate = db.Column(db.DateTime)
    enddate = db.Column(db.DateTime)
    description = db.Column(db.String(512))
    user = db.Column(db.Integer, db.ForeignKey('user.iduser'))
    rel_user = db.relationship('User', primaryjoin='Experience.user == User.iduser',
                                  backref=db.backref('experience', lazy='dynamic'))
    timestamp = db.Column(db.DateTime, default=datetime.now())

    def __init__(self, json_data=None, user=None):
        self.name = json_data['name']
        self.description = json_data['description']
        self.startdate = json_data['startdate']
        self.enddate = json_data['enddate']
        self.user = user

    def __repr__(self):
        return '<Experience %r>' % (self.name)

    def update(self, json_data):
        self.name = json_data['name']
        self.description = json_data['description']
        self.startdate = json_data['startdate']
        self.enddate = json_data['enddate']

    @property
    def serialize(self):
        return {
            'idexperience': self.idexperience,
            'name': self.name,
            'startdate': self.startdate,
            'enddate': self.enddate,
            'description': self.description,
            'user': self.rel_user.serialize,
            'timestamp': self.timestamp,
            'descriptive_header': self.name,
            'descriptive_subheader': self.description
        }


class Language(db.Model):
    __tablename__ = "language"

    idlanguage = db.Column(db.Integer, primary_key=True)
    language = db.Column(db.String(128))
    listening = db.Column(db.String(32))
    writing = db.Column(db.String(32))
    reading = db.Column(db.String(32))
    conversation = db.Column(db.String(32))
    verbal = db.Column(db.String(32))
    user = db.Column(db.Integer, db.ForeignKey('user.iduser'))
    rel_user = db.relationship('User', primaryjoin='Language.user == User.iduser',
                                  backref=db.backref('language', lazy='dynamic'))
    timestamp = db.Column(db.DateTime, default=datetime.now())

    def __init__(self, json_data=None, user=None):
        self.language = json_data['language']
        self.listening = json_data['listening']
        self.writing = json_data['writing']
        self.reading = json_data['reading']
        self.conversation = json_data['conversation']
        self.verbal = json_data['verbal']
        self.user = user

    def __repr__(self):
        return '<Language %r>' % (self.language)

    def update(self, json_data):
        self.language = json_data['language']
        self.listening = json_data['listening']
        self.writing = json_data['writing']
        self.reading = json_data['reading']
        self.conversation = json_data['conversation']
        self.verbal = json_data['verbal']

    @property
    def serialize(self):
        return {
            'idlanguage': self.idlanguage,
            'language': self.language,
            'listening': self.listening,
            'writing':self.writing,
            'reading': self.reading,
            'conversation': self.conversation,
            'verbal': self.verbal,
            'user': self.rel_user.serialize,
            'timestamp': self.timestamp,
            'descriptive_header': self.language,
            'descriptive_subheader': ''
        }

# Create our database model
class Publication(db.Model):
    __tablename__ = "publication"

    idpublication = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(72))
    authors = db.Column(db.String(4000))
    publication = db.Column(db.String(128))
    date = db.Column(db.DateTime)
    description = db.Column(db.String(512))
    user = db.Column(db.Integer, db.ForeignKey('user.iduser'))
    rel_user = db.relationship('User', primaryjoin='Publication.user == User.iduser',
                                  backref=db.backref('publication', lazy='dynamic'))
    timestamp = db.Column(db.DateTime, default=datetime.now())

    def __init__(self, json_data=None, user=None):
        self.title = json_data['title']
        self.authors = json_data['authors']
        self.publication = json_data['publication']
        self.description = json_data['description']
        self.date = json_data['date']
        self.user = user

    def __repr__(self):
        return '<Publication %r>' % (self.title)

    def update(self, json_data):
        self.title = json_data['title']
        self.authors = json_data['authors']
        self.publication = json_data['publication']
        self.description = json_data['description']
        self.date = json_data['date']

    @property
    def serialize(self):
        return {
            'idpublication': self.idpublication,
            'title': self.title,
            'authors': self.authors,
            'publication': self.publication,
            'date': self.date,
            'description': self.description,
            'user': self.rel_user.serialize,
            'timestamp': self.timestamp,
            'descriptive_header': self.title,
            'descriptive_subheader': self.description
        }

class Skill(db.Model):
    __tablename__ = "skill"

    idskill = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(72))
    level = db.Column(db.Integer)
    description = db.Column(db.String(512))
    user = db.Column(db.Integer, db.ForeignKey('user.iduser'))
    rel_user = db.relationship('User', primaryjoin='Skill.user == User.iduser',
                                  backref=db.backref('skill', lazy='dynamic'))
    timestamp = db.Column(db.DateTime, default=datetime.now())

    def __init__(self, json_data=None, user=None):
        self.name = json_data['name']
        self.description = json_data['description']
        self.level = json_data['level']
        self.user = user

    def __repr__(self):
        return '<Level %r>' % (self.name)

    def update(self, json_data):
        self.name = json_data['name']
        self.description = json_data['description']
        self.level = json_data['level']

    @property
    def serialize(self):
        return {
            'idskill': self.idskill,
            'name': self.name,
            'level': self.level,
            'description': self.description,
            'user': self.rel_user.serialize,
            'timestamp': self.timestamp,
            'descriptive_header': self.name,
            'descriptive_subheader': self.description
        }

class Merit(db.Model):
    __tablename__ = "merit"

    idmerit = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    date = db.Column(db.DateTime)
    description = db.Column(db.String(512))
    user = db.Column(db.Integer, db.ForeignKey('user.iduser'))
    rel_user = db.relationship('User', primaryjoin='Merit.user == User.iduser',
                                  backref=db.backref('merit', lazy='dynamic'))
    timestamp = db.Column(db.DateTime, default=datetime.now())

    def __init__(self, json_data=None, user=None):
        self.name = json_data['name']
        self.description = json_data['description']
        self.date = json_data['date']
        self.user = user

    def __repr__(self):
        return '<Merit %r>' % (self.name)

    def update(self, json_data):
        self.name = json_data['name']
        self.description = json_data['description']
        self.date = json_data['date']

    @property
    def serialize(self):
        return {
            'idmerit': self.idmerit,
            'name': self.name,
            'date': self.date,
            'description': self.description,
            'user': self.rel_user.serialize,
            'timestamp': self.timestamp,
            'descriptive_header': self.name,
            'descriptive_subheader': self.description
        }



class UserDetail(db.Model):
    __tablename__ = "userdetail"
    iduserdetail = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(72), default="")
    lastname = db.Column(db.String(72), default="")
    address = db.Column(db.String(128), default="")
    zipcode = db.Column(db.String(16), default="")
    city = db.Column(db.String(32), default="")
    country = db.Column(db.String(32), default="")
    email = db.Column(db.String(128), default="")
    position = db.Column(db.String(128), default="")
    description = db.Column(db.String(4000), default="")
    phone = db.Column(db.String(16), default="")
    mobilephone = db.Column(db.String(16), default="")

    user = db.Column(db.Integer, db.ForeignKey('user.iduser'))
    rel_user = db.relationship('User', primaryjoin='UserDetail.user == User.iduser',
                                  backref=db.backref('userdetail', lazy='dynamic'))
    profilepicture = db.Column(db.Integer, db.ForeignKey('file.idfile'))
    rel_profilepicture = db.relationship('File', primaryjoin='UserDetail.profilepicture == File.idfile',
                                  backref=db.backref('userdetail', lazy='dynamic'))
    birthdate = db.Column(db.DateTime)

    def __init__(self, firstname=None, lastname=None, address=None, zipcode=None,
                 city=None, country=None, birthdate=None, phone=None, mobilephone=None, email=None, position=None,
                  description=None, user=None):
        self.firstname = firstname
        self.lastname = lastname
        self.address = address
        self.zipcode = zipcode
        self.city = city
        self.country = country
        self.birthdate = birthdate
        self.phone = phone
        self.mobilephone = mobilephone
        self.email = email
        self.position = position
        self.description = description
        self.user = user

    def update(self, json_data):
        self.firstname = json_data['firstname']
        self.lastname = json_data['lastname']
        self.address = json_data['address']
        self.mobilephone = json_data['mobilephone']
        self.phone = json_data['phone']
        self.city = json_data['city']
        self.country = json_data['country']
        self.zipcode = json_data['zipcode']
        self.birthdate = json_data['birthdate']
        self.position= json_data['position']
        self.description= json_data['description']

    @property
    def serialize_profilepicture(self):
        if self.rel_profilepicture is not None:
            return self.rel_profilepicture.serialize
        else:
            return ""
    @property
    def serialize(self):
        return {
            'iduserdetail': self.iduserdetail,
            'firstname': self.firstname,
            'lastname': self.lastname,
            'address': self.address,
            'city': self.city,
            'zipcode': self.zipcode,
            'country': self.country,
            'mobilephone': self.mobilephone,
            'phone': self.phone,
            'birthdate': self.birthdate,
            'profilepicture' : self.serialize_profilepicture,
            'email' : self.email,
            'position' : self.position,
            'description' : self.description,
            'descriptive_header': self.firstname + ' ' + self.lastname,
            'descriptive_subheader': self.position
        }


class File(db.Model):
    __tablename__ = "file"
    idfile = db.Column(db.Integer, primary_key=True)
    data = db.Column(BYTEA)
    extension = db.Column(db.String(72))
    filename = db.Column(db.String(72))

    @property
    def get_data(self):
        return base64.b64encode(bytes(self.data)).decode('utf8')

    def __init__(self, data=None, extension=None, filename=None):
        self.data = base64.b64decode(data)
        self.extension = extension
        self.filename = filename

    def update(self, json_data):
        self.data = json_data['data']
        self.extension = json_data['extension']
        self.filename = json_data['filename']

    @property
    def serialize(self):
        return {
            'data': self.get_data,
            'extension': self.extension,
            'filename': self.filename,
            'idfile': self.idfile
        }



class User(db.Model):
    __tablename__ = 'user'
    iduser = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128))
    password = db.Column(db.String(128))

    def __init__(self, email, password):
        self.email = email.lower()
        self.set_password(password)
        # self.profile = profile

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def generate_auth_token(self, expiration = 86400):
        try:
            s = Serializer(config.secret_key, expires_in = expiration)
        except Exception as err:
            print(err)
        return s.dumps({ 'iduser': self.iduser })

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(config.secret_key)
        print("----- s -----")
        print(s)
        print(token)
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None # valid token, but expired
        except BadSignature:
            return None # invalid token
        user = User.query.get(data['iduser'])
        return user

######## DATABASE MODEL #########


class SearchResult():
    educations = []
    publications = []
    skills = []
    projects = []
    workexperiences = []
    languages = []
    merits = []
    experiences = []
    profiles = []

    def __init__(self):
        self.educations = []
        self.publications = []
        self.skills = []
        self.projects = []
        self.workexperiences = []
        self.languages = []
        self.merits = []
        self.experiences = []
        self.profiles = []

    @property
    def serialize(self):
        return {
            "workexperiences":[w for w in self.workexperiences],
            "educations":[e for e in self.educations],
            "languages":[l for l in self.languages],
            "skills":[s for s in self.skills],
            "experiences":[e for e in self.experiences],
            "projects":[p for p in self.projects],
            "merits":[m for m in self.merits],
            "publications":[p for p in self.publications],
            "profiles" : [p for p in self.profiles]
        }



def count_educations(idprofile):
    return Education.query.filter_by(profile=idprofile).count()

def get_class_by_tablename(tablename):
  for c in db.Model._decl_class_registry.values():
    if hasattr(c, '__tablename__') and c.__tablename__ == tablename:
      return c

def count_table(iduser, table):
    c = get_class_by_tablename(table)
    return c.query.filter_by(user=iduser).count()


def count_workexperience(idprofile):
    return WorkExperience.query.filter_by(profile=idprofile).count()

def count_language(idprofile):
    return Language.query.filter_by(profile=idprofile).count()

def count_skill(idprofile):
    return Skill.query.filter_by(profile=idprofile).count()

def count_publication(idprofile):
    return Publication.query.filter_by(profile=idprofile).count()

def count_experience(idprofile):
    return Experience.query.filter_by(profile=idprofile).count()

def count_merit(idprofile):
    return Merit.query.filter_by(profile=idprofile).count()

def get_skilltypes(iduser):
    return [{
                'locale':'Educations',
                'name':'education',
                'order': 1,
                'count': count_table(iduser, "education")
            },{
                'locale':'Work experience',
                'name':'workexperience',
                'order': 2,
                'count': count_table(iduser, "workexperience")
            },{
                'locale':'Experience',
                'name':'experience',
                'order': 3,
                'count': count_table(iduser, "experience")
            },{
                'locale':'Publications',
                'name':'publication',
                'order': 4,
                'count': count_table(iduser, "publication")
            },{
                'locale':'Projects',
                'name':'project',
                'order': 5,
                'count': count_table(iduser, "project")
            },{
                'locale':'Language',
                'name':'language',
                'order': 6,
                'count': count_table(iduser, "language")
            },{
                'locale':'Merits',
                'name':'merit',
                'order': 7,
                'count': count_table(iduser, "merit")
            },{
                'locale':'Skills',
                'name':'skill',
                'order': 8,
                'count': count_table(iduser, "skill")
            }]


########## ELASTIC SEARCH #########
def after_education_insert(mapper, connection, target):
    es = Elasticsearch()
    es.index(index="knowbase", doc_type="education", id=target.ideducation,
             body={
                    'ideducation': target.ideducation,
                    'title': target.title,
                    'education': target.education,
                    'school': target.school,
                    'startdate': target.startdate,
                    'enddate': target.enddate,
                    'description': target.description,
                    'profile': target.profile,
                    'timestamp': target.timestamp
             })

def after_education_update(mapper, connection, target):
    es = Elasticsearch()
    es.update(index='knowbase',doc_type='education',id=target.ideducation,
                body={"doc": {
                    'ideducation': target.ideducation,
                    'title': target.title,
                    'education': target.education,
                    'school': target.school,
                    'startdate': target.startdate,
                    'enddate': target.enddate,
                    'description': target.description,
                    'profile': target.profile,
                    'timestamp': target.timestamp
                }})
def after_education_delete(mapper, connection, target):
    es = Elasticsearch()
    es.delete(index='knowbase', doc_type='education', id=target.ideducation)


def after_workexperience_insert(mapper, connection, target):
    es = Elasticsearch()
    es.index(index="knowbase", doc_type="workexperience", id=target.idworkexperience,
             body={
                'idworkexperience': target.idworkexperience,
                'title': target.title,
                'employer': target.employer,
                'startdate': target.startdate,
                'enddate': target.enddate,
                'description': target.description,
                'profile': target.profile
            })

def after_workexperience_update(mapper, connection, target):
    es = Elasticsearch()
    es.update(index='knowbase',doc_type='workexperience',id=target.idworkexperience,
                body={"doc": {
                'idworkexperience': target.idworkexperience,
                'title': target.title,
                'employer': target.employer,
                'startdate': target.startdate,
                'enddate': target.enddate,
                'description': target.description,
                'profile': target.profile
            }})
def after_workexperience_delete(mapper, connection, target):
    es = Elasticsearch()
    es.delete(index='knowbase',doc_type='workexperience',id=target.idworkexperience)

def after_project_insert(mapper, connection, target):
    es = Elasticsearch()

    es.index(index='knowbase',doc_type='project',id=target.idproject,
             body={
                'idproject': target.idproject,
                'name': target.name,
                'hours': target.hours,
                #'customer': target.rel_customer.serialize,
                'startdate': target.startdate,
                'enddate': target.enddate,
                'description': target.description,
                'profile': target.profile
            })


def after_project_update(mapper, connection, target):
    es = Elasticsearch()
    try:
        es.update(index='knowbase',doc_type='project',id=target.idproject,
                    body={"doc": {
                    'idproject': target.idproject,
                    'name': target.name,
                    'hours': target.hours,
                    'customer': target.rel_customer.serialize,
                    'startdate': target.startdate,
                    'enddate': target.enddate,
                    'description': target.description,
                    'profile': target.profile
                }})
    except Exception as err:
        print(err)

def after_project_delete(mapper, connection, target):
    es = Elasticsearch()
    es.delete(index='knowbase',doc_type='project',id=target.idproject)

def after_experience_insert(mapper, connection, target):
    es = Elasticsearch()
    es.index(index='knowbase',doc_type='experience',id=target.idexperience,
             body={
                'idexperience': target.idexperience,
                'name': target.name,
                'startdate': target.startdate,
                'enddate': target.enddate,
                'description': target.description,
                'profile': target.profile
            })

def after_experience_update(mapper, connection, target):
    es = Elasticsearch()
    es.update(index='knowbase',doc_type='experience',id=target.idexperience,
                body={"doc": {
                'idexperience': target.idexperience,
                'name': target.name,
                'startdate': target.startdate,
                'enddate': target.enddate,
                'description': target.description,
                'profile': target.profile
            }})
def after_experience_delete(mapper, connection, target):
    es = Elasticsearch()
    es.delete(index='knowbase',doc_type='experience',id=target.idexperience)


def after_language_insert(mapper, connection, target):
    es = Elasticsearch()
    es.index(index='knowbase',doc_type='language',id=target.idlanguage,
             body={
            'idlanguage': target.idlanguage,
            'language': target.language,
            'listening': target.listening,
            'writing':target.writing,
            'reading': target.reading,
            'conversation': target.conversation,
            'verbal': target.verbal,
            'profile': target.profile
        })

def after_language_update(mapper, connection, target):
    es = Elasticsearch()
    es.update(index='knowbase',doc_type='language',id=target.idlanguage,
                body={"doc": {
                'idlanguage': target.idlanguage,
                'language': target.language,
                'listening': target.listening,
                'writing':target.writing,
                'reading': target.reading,
                'conversation': target.conversation,
                'verbal': target.verbal,
                'profile': target.profile
            }})
def after_language_delete(mapper, connection, target):
    es = Elasticsearch()
    es.delete(index='knowbase',doc_type='language',id=target.idlanguage)

def after_publication_insert(mapper, connection, target):
    es = Elasticsearch()
    es.index(index='knowbase',doc_type='publication',id=target.idpublication,
             body={
                'idpublication': target.idpublication,
                'title': target.title,
                'authors': target.authors,
                'publication': target.publication,
                'date': target.date,
                'description': target.description,
                'profile': target.profile
            })

def after_publication_update(mapper, connection, target):
    es = Elasticsearch()
    es.update(index='knowbase',doc_type='publication',id=target.idpublication,
                body={"doc": {
                'idpublication': target.idpublication,
                'title': target.title,
                'authors': target.authors,
                'publication': target.publication,
                'date': target.date,
                'description': target.description,
                'profile': target.profile
            }})
def after_publication_delete(mapper, connection, target):
    es = Elasticsearch()
    es.delete(index='knowbase',doc_type='publication',id=target.idpublication)

def after_skill_insert(mapper, connection, target):
    es = Elasticsearch()
    es.index(index='knowbase',doc_type='skill',id=target.idskill,
             body={
                'idskill': target.idskill,
                'name': target.name,
                'level': target.level,
                'description': target.description,
                'profile': target.profile
            })

def after_skill_update(mapper, connection, target):
    es = Elasticsearch()
    es.update(index='knowbase',doc_type='skill',id=target.idskill,
                body={"doc": {
                'idskill': target.idskill,
                'name': target.name,
                'level': target.level,
                'description': target.description,
                'profile': target.profile
            }})

def after_skill_delete(mapper, connection, target):
    es = Elasticsearch()
    es.delete(index='knowbase',doc_type='skill',id=target.idskill)

def after_merit_insert(mapper, connection, target):
    es = Elasticsearch()
    es.index(index='knowbase',doc_type='merit',id=target.idmerit,
             body={
                'idmerit': target.idmerit,
                'name': target.name,
                'date': target.date,
                'description': target.description,
                'profile': target.profile
            })

def after_merit_update(mapper, connection, target):
    es = Elasticsearch()
    es.update(index='knowbase',doc_type='merit',id=target.idmerit,
                body={"doc": {
                'idmerit': target.idmerit,
                'name': target.name,
                'date': target.date,
                'description': target.description,
                'profile': target.profile
            }})

def after_merit_delete(mapper, connection, target):
    es = Elasticsearch()
    es.delete(index='knowbase',doc_type='merit',id=target.idmerit)


event.listen(Education, 'after_insert', after_education_insert)
event.listen(Education, 'after_update', after_education_update)
event.listen(Education, 'after_delete', after_education_delete)

event.listen(WorkExperience, 'after_insert', after_workexperience_insert)
event.listen(WorkExperience, 'after_update', after_workexperience_update)
event.listen(WorkExperience, 'after_delete', after_workexperience_delete)

event.listen(Project, 'after_insert', after_project_insert)
event.listen(Project, 'after_update', after_project_update)
event.listen(Project, 'after_delete', after_project_delete)

event.listen(Experience, 'after_insert', after_experience_insert)
event.listen(Experience, 'after_update', after_experience_update)
event.listen(Experience, 'after_delete', after_experience_delete)

event.listen(Language, 'after_insert', after_language_insert)
event.listen(Language, 'after_update', after_language_update)
event.listen(Language, 'after_delete', after_language_delete)

event.listen(Publication, 'after_insert', after_publication_insert)
event.listen(Publication, 'after_update', after_publication_update)
event.listen(Publication, 'after_delete', after_publication_delete)

event.listen(Merit, 'after_insert', after_merit_insert)
event.listen(Merit, 'after_update', after_merit_update)
event.listen(Merit, 'after_delete', after_merit_delete)

event.listen(Skill, 'after_insert', after_skill_insert)
event.listen(Skill, 'after_update', after_skill_update)
event.listen(Skill, 'after_delete', after_skill_delete)