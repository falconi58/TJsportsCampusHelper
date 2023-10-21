import base64
from gxtyLib import getAESHelper

if __name__ == "__main__":
    # 解密请求测试
    p = input("input platform(ios/android): ")
    aesHelper = getAESHelper(p)
    data = input("input data: ")
    bb = base64.b64decode(data)
    decrypted = aesHelper.decrypt(bb).decode('utf-8')
    print("decrypted: " + decrypted)

    # 验签测试
    sign = input("input sign: ")
    idealSign = aesHelper.getSign(decrypted)
    if sign != '' and idealSign == sign:
        print("Sign check passed")
    else:
        print("Sign check failed")
