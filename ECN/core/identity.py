# core/identity.py

import uuid
import base64
import nacl.signing
import nacl.encoding

class Identity:
    def __init__(self):
        # 创建 Ed25519 密钥对
        self.signing_key = nacl.signing.SigningKey.generate()
        self.verify_key = self.signing_key.verify_key
        self.did = self.generate_did()

    def generate_did(self) -> str:
        # 使用 base64 编码的公钥作为 DID 的一部分
        pubkey_b64 = self.verify_key.encode(encoder=nacl.encoding.Base64Encoder).decode("utf-8")
        return f"did:ecn:{pubkey_b64[:20]}"

    def sign(self, message: str) -> str:
        signed = self.signing_key.sign(message.encode("utf-8"))
        return base64.b64encode(signed.signature).decode("utf-8")

    def get_public_key(self) -> str:
        return self.verify_key.encode(encoder=nacl.encoding.Base64Encoder).decode("utf-8")

    def __repr__(self):
        return f"<Identity DID={self.did}>"


# 公钥验签工具函数

def verify_signature(public_key_b64: str, message: str, signature_b64: str) -> bool:
    try:
        verify_key = nacl.signing.VerifyKey(public_key_b64.encode("utf-8"), encoder=nacl.encoding.Base64Encoder)
        signature = base64.b64decode(signature_b64)
        verify_key.verify(message.encode("utf-8"), signature)
        return True
    except Exception as e:
        print(f"[Verify] Signature invalid: {e}")
        return False


# 示例
if __name__ == "__main__":
    id = Identity()
    msg = "task_abc_xyz"
    sig = id.sign(msg)
    print("Signature:", sig)
    print("Verify:", verify_signature(id.get_public_key(), msg, sig))
