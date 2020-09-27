
import string, random
from hashlib import blake2b


def generate_random_string(size=10, chars = string.ascii_lowercase + string.digits):
    return ''.join(random.choices(chars, k=size))


def generate_id():
    return "u"+generate_random_string()


def generate_password():
    return generate_random_string(size=20,chars=string.ascii_letters+string.digits)


def get_salted_password(app_id,unsalted_password):
    return blake2b(unsalted_password.encode('utf-8'),salt=app_id.encode('utf-8')[:16],digest_size=20).hexdigest()
