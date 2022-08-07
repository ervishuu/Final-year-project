from app import app


def userDetails(id):
    data = Users.query.filter_by(id=id).first()
    if data:
        return data
    else:
        return "not found"
