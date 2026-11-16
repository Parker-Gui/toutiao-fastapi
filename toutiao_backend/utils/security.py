from pwdlib import PasswordHash
from pwdlib.exceptions import UnknownHashError
from pwdlib.hashers.bcrypt import BcryptHasher

# 创建密码上下文（pwdlib 里叫 PasswordHash，作用等同 passlib 的 CryptContext）
pwd_context = PasswordHash((BcryptHasher(),))


# 密码加密
def get_hash_password(password: str):
    return pwd_context.hash(password)


# 密码验证：verify 返回值是布尔型
def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except UnknownHashError:
        return False
