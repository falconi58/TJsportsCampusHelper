import json
import os

from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64
import hashlib
import requests


def getAESHelper(platform: str):
    if platform.lower() == 'android':
        return AndroidAESHelper()
    elif platform.lower() == 'ios':
        return IOSAESHelper()
    else:
        raise Exception("Unknown Platform")


class AESHelper:
    def __init__(self):
        pass

    def encrypt(self, plaintext: bytes) -> bytes:
        pass

    def decrypt(self, ciphertext: bytes) -> bytes:
        pass

    def getSign(self, msg: str) -> str:
        pass


class AndroidAESHelper(AESHelper):
    def __init__(self):
        super().__init__()
        self.key = b'nO5Mm4zggvrbYyIJ'
        self.iv = b'1111111111111111'

    def encrypt(self, plaintext: bytes):
        backend = default_backend()
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(self.iv), backend=backend)
        encryptor = cipher.encryptor()

        padder = padding.PKCS7(algorithms.AES.block_size).padder()
        padded_plaintext = padder.update(plaintext) + padder.finalize()

        ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()
        return ciphertext

    def decrypt(self, ciphertext: bytes):
        backend = default_backend()
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(self.iv), backend=backend)
        decryptor = cipher.decryptor()

        padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()

        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
        plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()

        return plaintext

    def getSign(self, msg: str):
        # salt变了！
        msg = 'nO5Mm4zggvrbYyIJ0zbnKkq2sdb~4KscsiscARpddata' + msg
        hl = hashlib.md5()
        hl.update(msg.encode('ascii'))
        return hl.hexdigest()


class IOSAESHelper(AESHelper):
    def __init__(self):
        super().__init__()
        self.key = b'OmZw5Vk9YRIctFbD'

    def encrypt(self, plaintext: bytes):
        backend = default_backend()
        cipher = Cipher(algorithms.AES(self.key), modes.ECB(), backend=backend)
        encryptor = cipher.encryptor()

        padder = padding.PKCS7(algorithms.AES.block_size).padder()
        padded_plaintext = padder.update(plaintext) + padder.finalize()

        ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()
        return ciphertext

    def decrypt(self, ciphertext: bytes):
        backend = default_backend()
        cipher = Cipher(algorithms.AES(self.key), modes.ECB(), backend=backend)
        decryptor = cipher.decryptor()

        padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()

        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
        plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()

        return plaintext

    def getSign(self, msg: str):
        # salt变了！
        msg = 'MITY@*TeYBBZrBAYrLCm8U.2Y+Pt0@vltP1U$.X$data' + msg
        hl = hashlib.md5()
        hl.update(msg.encode('ascii'))
        return hl.hexdigest()


class DataBean:

    def __init__(self, obj: dict):
        self.obj = obj

    def getDataStr(self):
        if self.obj is None:
            return '{}'
        else:
            return json.dumps(self.obj, separators=(',', ':'))


class GXTYRequestHelper:

    def __init__(self, aesHelper: AESHelper, platform: str, initUuid: str, urlPrefix: str, checkCert=True):
        self.aesHelper = aesHelper
        self.urlPrefix = urlPrefix
        if platform.lower() == 'android':
            self.nowHeader = {'Content-Type': 'application/x-www-form-urlencoded',
                              "Accept-Language": "zh-CN,zh;q=0.8",
                              "User-Agent": "okhttp-okgo/jeasonlzy",
                              "X-Channel": "ru_huawei",
                              "Packagename": "com.example.gita.gxty",
                              "Xxversionxx": "20180601",
                              "Versionname": "2.9.8",
                              "Versioncode": "519",
                              "Platform": "android",
                              "E206b53e98e9ecc295427aa5e1a4c18b": "0,0,0,0,0,0",  # 这个是固定的
                              "Uuid": initUuid
                              }
        elif platform.lower() == 'ios':
            self.nowHeader = {'Content-Type': 'application/x-www-form-urlencoded',
                              "Accept-Language": "zh-CN,zh;q=0.8",
                              "User-Agent": "CollegeSports2/2.2.48 (iPhone; iOS 17.0.1; Scale/3.00)",
                              "xxversionxx": "20180601",
                              "versionname": "2.2.48",
                              "versioncode": "431",
                              "platform": "iOS",
                              "uuid": initUuid
                              }
        else:
            raise Exception("Unknown Platform")

        self.checkCert = checkCert

    def setCredential(self, utoken: 'str|None' = None, cookie: 'str|None' = None):
        if utoken:
            self.nowHeader['utoken'] = utoken
        if cookie:
            self.nowHeader['Cookie'] = cookie

    def getAESData(self, dataBean: 'DataBean'):
        return base64.encodebytes(self.aesHelper.encrypt(dataBean.getDataStr().encode('utf-8'))).decode('utf-8')

    def getSign(self, dataBean: 'DataBean'):
        return self.aesHelper.getSign(dataBean.getDataStr())

    def sendEncryptedRequest(self, path: str, params: dict, extraHeaders: 'dict|None' = None) -> dict:
        bean = DataBean(params)
        if extraHeaders is None:
            completeHeader = self.nowHeader
        else:
            completeHeader = {}
            completeHeader.update(self.nowHeader)
            completeHeader.update(extraHeaders)
        res = requests.post(self.urlPrefix + path, headers=completeHeader,
                            data={"sign": self.getSign(bean), "data": self.getAESData(bean)}, verify=self.checkCert)
        if 'Set-Cookie' in res.headers:
            self.nowHeader['Cookie'] = res.headers['Set-Cookie']
            print("SetCookie!" + res.headers['Set-Cookie'])

        resJson = res.json()
        if 'data' not in resJson or type(resJson['data']) is not str:
            raise Exception("请求出错：" + res.text)
        resBase64AesEncrypted = resJson['data']
        bb = base64.b64decode(resBase64AesEncrypted)
        decryptedDataJson = self.aesHelper.decrypt(bb).decode("utf-8")
        return json.loads(decryptedDataJson)

    def sendNormalRequest(self, path: str, params: dict, extraHeaders: 'dict|None' = None):
        bean = DataBean(params)
        if extraHeaders is None:
            completeHeader = self.nowHeader
        else:
            completeHeader = {}
            completeHeader.update(self.nowHeader)
            completeHeader.update(extraHeaders)
        res = requests.post(self.urlPrefix + path, headers=completeHeader,
                            data={"sign": self.getSign(bean), "data": bean.getDataStr()}, verify=self.checkCert)
        resJson = res.json()
        return resJson


class Config:
    def __init__(self):
        self.configDict = {
            "useToken": False,
            "platform": "<YOUR PLATFORM>",
            "userInfo": {
                "phone": "11451419198",
                "password": "myPassword",
            },
            "credential": {
                "utoken": "1234567890abcdef1234567890abcdef",
                "cookie": "PHPSESSID=zbnKkq2sdbb4ascsiscadhsnda; path=/",
            },
            "spotInfo": {
                "major": 11451,
                "minor": 41919,
                "uuid": "FDA50693-A4E2-4FB1-AFCF-C6EB07647825"
            },
            "uuid": "C003DCCAE5A256D6605EE54A56825C14",
            "autoSign": False
        }
        if os.path.exists("config.json"):
            self.configDict = json.load(open('config.json'))
        else:
            json.dump(self.configDict, open("config.json", "w"))
            print("已生成配置文件模板，请修改后重新运行脚本！")
            exit(114514)

    def getUseToken(self):
        return self.configDict['useToken']

    def getUserInfo(self):
        return self.configDict['userInfo']

    def getCredential(self):
        return self.configDict['credential']

    def getSpotInfo(self):
        return self.configDict['spotInfo']

    def getAutoSign(self):
        return self.configDict['autoSign']

    def getUUid(self):
        return self.configDict['uuid']

    def getPlatform(self):
        return self.configDict['platform']
