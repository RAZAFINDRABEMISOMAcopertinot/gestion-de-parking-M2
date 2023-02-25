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
    _validité = ""

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


class Voiture:


    def __init__(self, num_imm, marque, couleur, chauffeur_id):
        self._num_imm = num_imm
        self._marque = marque
        self._couleur = couleur
        self._id_chauffeur = chauffeur_id

    def getNumImm(self):
        return self._num_imm

    def getMarque(self):
        return self._marque

    def getCouleur(self):
        return self._couleur

    def getChauffeur(self):
        return self._id_chauffeur

    def setNumImm(self, num_imm):
        self._num_imm = num_imm

    def setMarque(self, marque):
        self._marque = marque

    def setCouleur(self, couleur):
        self._couleur = couleur

    def setChauffeur(self, id_chauffeur):
        self._id_chauffeur = id_chauffeur

class CarteGrise:

    _IMMATRICULATION = ["VUI", "VNI", "MHP", "CP"]
    _date_de_circulation = ""

    def __init__(self, energie, type, nombre_place, genre, id_vehicule):
        self._energie = energie
        self._type = type
        self._nombre_place = nombre_place
        self._genre = genre
        self._id_vehicule = id_vehicule


    def getEnergie(self):
        return self._energie

    def getType(self):
        return self._type

    def getNomberPlace(self):
        return self._nombre_place

    def getGenre(self):
        return self._genre

    def getVehicule(self):
        return self._id_vehicule

    @classmethod
    def getImmatriculation(cls):
        return cls._IMMATRICULATION

    def getDateDeCirculation(self):
        return self._date_de_circulation

    def setEnergie(self, energie):
        self._energie = energie

    def setType(self, type):
        self._type = type

    def setNombePlace(self, nombe_place):
        self._nombre_place = nombe_place

    def setGenre(self, genre):
        self._genre = genre

    def setDateDeCirculation(self, date_de_circulation):
        # Enlever les espces
        date_de_circulation = re.sub("\s+", "", date_de_circulation)

        # Convertir la date en objet datetime
        date_de_circulation_date_object = datetime.datetime.strptime(date_de_circulation, "%m/%d/%Y")

        # Formater l'objet datetime sous la forme YYYY-MM-DD
        formatted_date = date_de_circulation_date_object.strftime("%Y-%m-%d")

        self._date_de_circulation = formatted_date

    def setVehicule(self, id_vehicule):
        self._id_vehicule = id_vehicule


class Abonnement:
    _TYPES = ["PERMANENT", "JOUR", "NUIT"]

    def __init__(self, type, prix):
        self._type = type
        self._prix = prix

    @classmethod
    def getAllTypes(cls):
        return cls._TYPES

    def getType(self):
        return self._type

    def getPrix(self):
        return self._prix

    def setType(self, type):
        self._type = type

    def setPrix(self, prix):
        self._prix = prix


class CarteAbonnement:

    _debut = ""
    _fin = ""
    _DEJAPAYER = ["NON", "OUI"]
    _ENCOREVALIDE = ["NON", "OUI"]

    def __init__(self, id_abonnement, id_chauffeur, payer=False, valide=True):
        self._payer = payer
        self._valide = valide
        self._id_abonnement = id_abonnement
        self._id_chauffeur = id_chauffeur

    @classmethod
    def getDejaPayer(cls):
        return cls._DEJAPAYER

    @classmethod
    def getEncoreValide(cls):
        return cls._ENCOREVALIDE

    def getPayer(self):
        return self._payer

    def getValide(self):
        return self._valide

    def getAbonnement(self):
        return self._id_abonnement

    def getChauffeur(self):
        return self._id_chauffeur

    def getDebut(self):
        return self._debut

    def getFin(self):
        return self._fin

    def setPayer(self):
        self._payer = True

    def setValide(self, valide):
        self._valide = valide

    def setAbonnement(self, abn):
        self._id_abonnement = abn

    def setChauffeur(self, chf):
        self._id_chauffeur = chf

    def setDebut(self, debut):
        # Enlever les espces
        debut = re.sub("\s+", "", debut)

        # Convertir la date en objet datetime
        debut_object = datetime.datetime.strptime(debut, "%m/%d/%Y")

        # Formater l'objet datetime sous la forme YYYY-MM-DD
        formatted_date = debut_object.strftime("%Y-%m-%d")

        self._debut = formatted_date

    def setFin(self, fin):
        # Enlever les espces
        fin = re.sub("\s+", "", fin)

        # Convertir la date en objet datetime
        fin_object = datetime.datetime.strptime(fin, "%m/%d/%Y")

        # Formater l'objet datetime sous la forme YYYY-MM-DD
        formatted_date = fin_object.strftime("%Y-%m-%d")

        self._fin = formatted_date


