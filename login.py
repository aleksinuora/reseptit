from werkzeug.security import check_password_hash, generate_password_hash
import users

def check_login(username, password):
    user = users.find_user(username)
    if (user):
        hash_value = user.passhash
        if check_password_hash(hash_value, password):
            return user
    return None