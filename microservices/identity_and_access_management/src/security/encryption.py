from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization



def generate_keys():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096
    )
    pem_private = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    with open("../../encryption_private_key.pem", "wb") as f:
        f.write(pem_private)

    public_key = private_key.public_key()
    pem_public = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    with open("encryption_public_key.pem", "wb") as f:
        f.write(pem_public)
