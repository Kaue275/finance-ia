from passlib.hash import pbkdf2_sha256 as pbk

class PasswordSecurity:
    def hash_password(password):
        hashed = pbk.hash(password)
        return hashed

    def verify_password(hash_password, password):
        verify = pbk.verify(password, hash_password)        
        return verify