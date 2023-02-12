import re
import bcrypt
import datetime


class User:
    _ROLES = ["GERANT", "SECURITE", "AGENT", "COMPTABLE"]

    _password = ""

    def __init__(self, nom, prénom, email, rôle):
        self._nom = nom
        self._prénom = prénom
        self._email = email
        self._rôle = rôle

    @classmethod
    def getRoles(cls):
        return cls._ROLES

    def getNom(self):
        return self._nom

    def getPrénom(self):
        return self._prénom

    def getEmail(self):
        return self._email

    def getPassword(self):
        return self._password

    def getRôle(self):
        return self._rôle

    def setNom(self, nom):
        self._nom = nom

    def setPrénom(self, prénom):
        self._prénom = prénom

    def setEmail(self, email):
        self._email = email

    def setPassword(self, password):
        formated_password = password.encode("utf-8")
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(formated_password, salt)
        self._password = hashed_password

    @classmethod
    def checkPassword(cls, password1, password2):
        password_to_check = password1.encode("utf-8")
        hashed_password = password2.encode("utf-8")
        return bcrypt.checkpw(password_to_check, hashed_password)

    def setRôle(self, rôle):
        self._rôle = rôle


class Chauffeur:
    _date_naissance = ""

    def __init__(self, nom, prénom, lieu_naissance):
        self._nom = nom
        self._prénom = prénom
        self._lieu_naissance = lieu_naissance

    def getNom(self):
        return self._nom

    def getPrénom(self):
        return self._prénom

    def getDateNaissance(self):
        return self._date_naissance

    def getLieuNaissance(self):
        return self._lieu_naissance

    def setNom(self, nom):
        self._nom = nom

    def setPrénom(self, prénom):
        self._prénom = prénom

    def setDateNaissance(self, date_naissance):

        # Enlever les espces
        date_naissance = re.sub("\s+", "", date_naissance)

        # Convertir la date en objet datetime
        date_object = datetime.datetime.strptime(date_naissance, "%m/%d/%Y")

        # Formater l'objet datetime sous la forme YYYY-MM-DD
        formatted_date = date_object.strftime("%Y-%m-%d")

        self._date_naissance = formatted_date

    def setLieuNaissance(self, lieu_naissance):
        self._lieu_naissance = lieu_naissance


class Permis:

    _CATEGORIES = ["A", "Aprim", "B", "C", "D", "E", "F"]

    def __init__(self, cim, categorie, chauffeur):
        self._cim = cim
        self._categorie = categorie
        self._id_chauffeur = chauffeur

    @classmethod
    def getCatgories(cls):
        return cls._CATEGORIES

    def getChauffeur(self):
        return self._id_chauffeur

    def getCim(self):
        return self._cim

    def getCategorie(self):
        return self._categorie

    def getValidité(self):
        return self._validité

    def setCheuffeur(self, id_chauffeur):
        self._id_chauffeur = id_chauffeur

    def setCim(self, cim):
        self._cim = cim

    def setCategorie(self, categorie):
        self._categorie = categorie

    def setValidité(self, validité):
        # Enlever les espces
        validité = re.sub("\s+", "", validité)

        # Convertir la date en objet datetime
        validité_date_object = datetime.datetime.strptime(validité, "%m/%d/%Y")

        # Formater l'objet datetime sous la forme YYYY-MM-DD
        formatted_date = validité_date_object.strftime("%Y-%m-%d")

        self._validité = formatted_date
