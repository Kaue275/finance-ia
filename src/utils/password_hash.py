from passlib.hash import pbkdf2_sha256 as pbk
from exceptions.user_exception import UserError

class InvalidPasswordError(UserError):
    status_code = 422

class PasswordSecurity:
    def hash_password(password):
        hashed = pbk.hash(password)
        return hashed

    def valid_password(password):
        min_len = 6
        if len(password) < 6:
            raise InvalidPasswordError

    def verify_password(hash_password, password):
        verify = pbk.verify(password, hash_password)        
        return verify
    