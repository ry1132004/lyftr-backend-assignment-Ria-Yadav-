import hmac
import hashlib

secret = b"testsecret"

body = b'{"message_id":"m1","from":"+911234567890","to":"+14155550100","ts":"2025-01-15T10:00:00Z","text":"Hello"}'

signature = hmac.new(secret, body, hashlib.sha256).hexdigest()
print(signature)
