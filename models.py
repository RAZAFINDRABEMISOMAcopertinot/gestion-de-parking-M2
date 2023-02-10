class User:
    _ROLES = ["GERANT", "SECURITE", "AGENT", "COMPTABLE"]

    def __init__(self):
        pass

    def getRoles(self):
        return self._ROLES
