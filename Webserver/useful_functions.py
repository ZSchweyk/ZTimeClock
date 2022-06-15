import hashlib


def sha256(string: str):
    return hashlib.sha256(string.encode()).hexdigest()


def remove_spaces(string: str):
    return "".join([char for char in string.split(" ") if char != ""])
