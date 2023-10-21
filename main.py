import json
import random
import time

from gxtyLib import GXTYRequestHelper, getAESHelper, Config

if __name__ == "__main__":
    config = Config()
    aesHelper = getAESHelper(config.getPlatform())  # iOS与安卓密钥不同！
    requestHelper = GXTYRequestHelper(aesHelper, config.getPlatform(), config.getUUid(), "https://www.sportcampus.cn/api")

    # 先登录
    if config.getUseToken():
        # 直接用utoken登录
        print("使用utoken登录")
        credential = config.getCredential()
        requestHelper.setCredential(credential['utoken'], credential['cookie'])
    else:
        # 手机号登录
        print("使用手机号和密码登录")
        params = {"mobile": config.getUserInfo()['phone'],
                  "password": config.getUserInfo()['password'],
                  "info": config.getUUid(),
                  "type": 'iPhone 15' if config.getPlatform() == 'ios' else 'SM-G988N',
                  "ts": str(int(time.time() * 1000)),
                  "nonce": "8e2bee985ac94eeab836776d179b2315"
                  }
        res = requestHelper.sendEncryptedRequest('/reg/login?ltype=1', params)
        requestHelper.setCredential(utoken=res['utoken'])
        print("登录成功")

    # 获取签到点信息
    params = {
        "type": 2,
        "isBreakPoint": 1,
        "ibeacons": json.dumps([config.getSpotInfo()])
    }
    extraHeader = {"ntoken": "testsign"} if config.getPlatform().lower() == 'android' else None
    signInfo = requestHelper.sendEncryptedRequest("/association/dataListByDevice/2", params, extraHeader)
    print("可签到时间段" + json.dumps(signInfo[0]['sign_range']))

    # 确认签到
    if config.getAutoSign():
        shouldSign = True
    else:
        shouldSign = input("输入 y+回车 继续签到，输入其他退出: ") == 'y'

    if not shouldSign:
        exit(114514)

    exerciseTime = 1800 + random.randint(0, 6)
    timeStampEnd = time.time() - random.random()
    timeStampStart = timeStampEnd - exerciseTime
    signObj = {
        "nonce": signInfo[0]['nonce'],
        "ass_id": signInfo[0]['ass_id'],
        "extra": [json.dumps({
            "ass_id": signInfo[0]['ass_id'],
            "runCurSecond": exerciseTime,
            "pauseCurSecond": 0,
            "historyTime": int(time.time() * 1000),
            "startTime": int(timeStampStart * 1000),
            "endTime": str(timeStampEnd * 1000),
            "duration": exerciseTime,
            "points": []
        })]
    }
    extraHeader2 = {"ntoken": "testdosign"} if config.getPlatform().lower() == 'android' else None
    signCompleteInfo = requestHelper.sendNormalRequest("/association/doSign", signObj, extraHeader2)
    print(signCompleteInfo)
