import bcrypt

from django.contrib.auth.hashers import BCryptSHA256PasswordHasher


class LegacyBCryptSHA256PasswordHasher(BCryptSHA256PasswordHasher):
    algorithm = "legacy_bcrypt_sha256"

    def verify(self, password, encoded):
        algorithm, data = encoded.split("$", 1)
        assert algorithm == self.algorithm

        return bcrypt.checkpw(
            password=password.encode("ascii"),
            hashed_password=data.encode("ascii"),
        )
