from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
import Crypto
from Crypto.Hash import SHA
from Crypto.Cipher import PKCS1_v1_5, AES
from Crypto.PublicKey import RSA
from Crypto import Random
import ast, os, six, base64
from pkcs7 import PKCS7Encoder

class RequestDecryptionMiddleware(MiddlewareMixin):
  PUBLIC_KEY_FILE_PATH = "keys/public.key"
  PRIVATE_KEY_FILE_PATH = "keys/private.key"
  PRIVATE_KEY = None
  PUBLIC_KEY = None
  def process_request(self, request):
    if not os.path.isfile(self.PUBLIC_KEY_FILE_PATH):
      self.generate_keys()
    # request._body = self.decrypt(request.body)
    return None

  def process_response(self, request, response):
    if request.method=="GET":
      client_aes_key = self.decrypt_rsa(request.headers["Authorization"])
      response.content = self.encrypt_aes256(client_aes_key, response.content)
    return response

  def encrypt(self, message):
    # First check for client_encrypted_secret in cache. Only decrypt the key if not found
    client_secret_key = decrypt_rsa(self, client_encrypted_secret)
    return encrypt_aes256(client_secret_key, message)

  def decrypt(self, client_encrypted_secret, encoded_encrypted_message):
    # First check for client_encrypted_secret in cache. Only decrypt the key if not found
    client_secret_key = decrypt_rsa(self, client_encrypted_secret)
    return decrypt_aes256(client_secret_key, encoded_encrypted_message)

  def encrypt_aes256(self, key, raw):
    encoder = PKCS7Encoder()
    raw = encoder.encode(raw.decode('utf-8'))
    iv = Random.new().read(16)
    # raw = self._pad(raw)
    # iv = Random.new().read(AES.block_size)
    cipher = AES.new(key, AES.MODE_CBC, iv, segment_size=128)
    return base64.b64encode(iv + cipher.encrypt(raw))

  def decrypt_aes256(self, key, enc):
    encoder = PKCS7Encoder()
    enc = base64.b64decode(enc)
    iv = enc[:16]
    cipher = AES.new(key, AES.MODE_CBC, iv, segment_size=128)
    return encoder.decode(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')
    # return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

  def _pad(self, s):
    bs = 16
    return s + (bs - len(s) % bs) * chr(bs - len(s) % bs)

  # @staticmethod
  #   def _unpad(s):
  #     return s[:-ord(s[len(s)-1:])]

  def encrypt_rsa(self, message):
    public_key = self._get_public_key()
    public_key_object = RSA.importKey(public_key)
    cipher = PKCS1_v1_5.new(public_key_object)
    # random_phrase = 'M'
    # h = SHA.new(str.encode(message))
    encrypted_message = cipher.encrypt(self._to_format_for_encrypt(message))
    # use base64 for save encrypted_message in database without problems with encoding
    return base64.b64encode(encrypted_message)


  def decrypt_rsa(self, encoded_encrypted_message):
    # Decrypt request.headers['secret-key'] using privat key and assign it to client_secret_key
    # Using AES algorithm, decrypt request.body using client_secret_key as the secret key
    encrypted_message = base64.b64decode(encoded_encrypted_message)
    private_key = self._get_private_key()
    private_key_object = RSA.importKey(private_key)
    cipher = PKCS1_v1_5.new(private_key_object)
    dsize = SHA.digest_size
    sentinel = Random.new().read(15+dsize)
    decrypted_message = cipher.decrypt(encrypted_message, sentinel)
    return six.text_type(decrypted_message, encoding='utf8')

  def _get_public_key(self):
    if self.PUBLIC_KEY:
      return self.PUBLIC_KEY
    else:
      with open(self.PUBLIC_KEY_FILE_PATH, 'r') as _file:
        self.PUBLIC_KEY = _file.read()
        return self.PUBLIC_KEY

  def _get_private_key(self):
    if self.PRIVATE_KEY:
      return self.PRIVATE_KEY
    else:
      with open(self.PRIVATE_KEY_FILE_PATH, 'r') as _file:
        self.PRIVATE_KEY = _file.read()
        return self.PRIVATE_KEY

  def generate_keys(self):
    random_generator = Random.new().read
    key = RSA.generate(1024, random_generator)
    self.PRIVATE_KEY, self.PUBLIC_KEY = key.exportKey().decode("utf-8"), key.publickey().exportKey().decode("utf-8")
    self.create_directories()
    with open(self.PRIVATE_KEY_FILE_PATH, 'w') as private_file:
      private_file.write(self.PRIVATE_KEY)
    with open(self.PUBLIC_KEY_FILE_PATH, 'w') as public_file:
      public_file.write(self.PUBLIC_KEY)
    return self.PRIVATE_KEY, self.PUBLIC_KEY

  def create_directories(self, for_private_key=True):
    public_key_path = self.PUBLIC_KEY_FILE_PATH.rsplit('/', 1)[0]
    if not os.path.exists(public_key_path):
      os.makedirs(public_key_path)
    if for_private_key:
      private_key_path = self.PRIVATE_KEY_FILE_PATH.rsplit('/', 1)[0]
      if not os.path.exists(private_key_path):
        os.makedirs(private_key_path)


  def _to_format_for_encrypt(value):
    if isinstance(value, int):
      return six.binary_type(value)
    for str_type in six.string_types:
      if isinstance(value, str_type):
        return value.encode('utf8')
    if isinstance(value, six.binary_type):
      return value