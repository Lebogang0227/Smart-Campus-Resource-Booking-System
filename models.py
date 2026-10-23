class User:
    def __init__(self, username, password, role, campus=None):
        self.username = username
        self._password = password #makes it private
        self.role = role
        self.campus = campus

    def check_password(self, password):
        return self._password == password

    def get_description(self):
        return f"{self.role.title()} - {self.username}"

    def __str__(self):
        return self.get_description()


class Lecturer(User):
    def __init__(self, username, password, campus):
        super().__init__(username, password, "lecturer", campus)

    def get_description(self):
        return f"Lecturer ({self.campus}): {self.username}"

class CampusAdmin(User):
    def __init__(self, username, password, campus):
        super().__init__(username, password, "admin", campus)

    def get_description(self):
        return f"Campus Administrator ({self.campus}): {self.username}"

class SystemOperator(User):
    def  __init__(self, username, password):
        super().__init__(username, password, "operator", None)
    def get_description(self):
        return f"System Operator: {self.username}"


def build_user_from_record(record):
    role = record["role"]
    if role == "lecturer":
        return Lecturer(record["username"], record["password"], record["campus"])
    if role == "admin":
        return CampusAdmin(record["username"], record["password"], record["campus"])
    if role == "operator":
        return SystemOperator(record["username"], record["password"])
    # fallback
    return User(record["username"], record["password"], role, record["campus"])