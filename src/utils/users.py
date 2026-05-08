

from hashlib import sha256

User = dict[str, int | str]

def hash_password(password: str) -> str:
	return sha256(password.encode("utf-8")).hexdigest()

def generate_user(username: str, display_name: str, email: str, phone: str, password: str) -> User:
  return {
    "username": username,
    "display_name": display_name,
    "email": email,
    "phone": phone,
    "password_hash": hash_password(password),
  }