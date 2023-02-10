import bcrypt

class User:
    _ROLES = ["GERANT", "SECURITE", "AGENT", "COMPTABLE"]

    _password = ""

    def __init__(self, nom, prénom, email, rôle):
        self._nom = nom
        self._prénom = prénom
        self._email = email
        self._rôle = rôle

    @classmethod
    def getRoles(self):
        return self._ROLES

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

    def setRôle(self, rôle):
        self._rôle = rôle
