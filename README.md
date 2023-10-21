# 同济高校体育一秒自动签到及自动跑步
源作者[sorakadoaoR](https://github.com/sorakadoaoR)&nbsp;&nbsp;&nbsp;&nbsp; 源项目地址[sportCampusSignHelper](https://github.com/sorakadoaoR/sportCampusSignHelper)
## 自动签到简介

由于刷锻时间和本人学习健身时间冲突，加上本人不喜欢被强制性的运动刷锻，在佬的基础上实现了一台电脑随时随地即可同济刷锻的手法，提供给同样时间安排冲突的同学使用，后面若有更新我也会及时随着佬更新fork，直到毕业不需要刷锻为止，但须知：文明其精神，野蛮其体魄。希望能帮tj学子节省出更多时间在别的有益的事情上

## 使用方法

1. 安装依赖

    ```shell
    pip install -r requirements.txt
    ```

2. 运行

    请先安装python，实测python3.11.2可以运行，其他版本请自行尝试
    ```shell
    python main.py
    ```

3. 配置文件

    首次运行main.py会自动生成如下的`config.json`配置文件, 其中包含你的账号与签到点信息。

    一个配置好的`config.json`应该看起来像这样：

    ```JSON
    {
        "useToken": true,
        "platform": "<YOUR PLATFORM>",
        "userInfo": {
            "phone": "1234567",
            "password": "myPassword"
        },
        "credential": {
            "utoken": "1234567890abcdef1234567890abcdef",
            "cookie": "PHPSESSID=zbnKkq2sdbb4ascsiscadhsnda; path=/"
        },
        "spotInfo": {
            "major": 11451,
            "minor": 41919,
            "uuid": "FDA50693-A4E2-4FB1-AFCF-C6EB07647825"
        },
        "uuid": "C003DCCAE5A256D6605EE54A56825C14",
        "autoSign": false
    }
    ```
    对于同济四平的ios用户，最下面的uuid改为：2B8237CF-A809-751C-DA00-6D97150342EA-1662083223-998001<br>
   四平安卓用户改为:2B8237CFA809751CDA006D97150342EA1662083223998001<br>
   嘉定校区还请自行操作<br><br>
   我已帮忙抓包到四平乒乓馆or攀岩馆的spotInfo：{"major": 10003,
        "minor": 25693},{"major": 10004,
        "minor": 5901}，{"major": 10090,
        "minor": 50565}，{"major": 10090,
        "minor": 50719}，可签到时间段"[[\"11:30\",\"13:30\"],[\"11:30\",\"21:00\"],[\"17:00\",\"21:00\"],[\"08:00\",\"21:00\"],[\"15:00\",\"21:00\"]]"<br>
        输入这些数据后再次启动main.py即可一秒完成一次刷锻
    ### 平台
    
    在`platform`字段输入你的平台名称，只接接受`android`或者`ios`

    ### UUID

    在请求高校体育的服务器时，请求头需要一个UUID字段，该字段应由设备的各种识别信息生成，可以通过下方的抓包方法获取，或者随意填写一个合法的uuid放在`uuid`字段即可

    请注意，安卓版本没有`-`分割，iOS版本有`-`分割    

    ### 登录方式

    以下两种方式选择一种即可

    1. 使用`utoken`登录：

        将`useToken`属性设为`true`来使用这种登录方式
        
        将抓包得到的utoken(应为32位的16进制字符串)填入`utoken`字段，cookie填入`cookie`字段。使用这种时登录方式，无需填写`phone`和`password`字段，并且可以免除在APP上重复登陆的情况

    2. 使用手机号和密码登录：

        将`useToken`属性设为`false`来使用这种登录方式

        其中，`phone`和`password`字段为高校体育账号的手机号和密码。这些信息只会被发送到高校体育服务器。

    ### 场地信息

    `spotInfo`中的`major`、`minor`、`uuid`字段为签到点信息。
    
    这三个值可以通过到签到点现场，在扫描签到信号的时候抓包获取；或者使用一些信标（iBeacon）扫描软件当场扫描获取，在使用扫描软件时，直接搜索uuid为`FDA50693-A4E2-4FB1-AFCF-C6EB07647825`的设备即可

    ### 自动签到

    `autoSign`字段为布尔值，代表是否需要在签到前进行二次确认来防止在可签到时间段外意外签到。

## 抓包方法

### iOS

目前市面上有许多抓包软件，这里推荐iOS使用Stream软件来进行抓包。

Stream的使用教程可以参考[这个视频](https://www.bilibili.com/video/BV1Ea411g7Wq/?t=00m18s)的0:18~2:16

1. 安装上述的抓包软件

2. 打开高校体育，随意打开几个界面

3. 停止抓包，在结果中找到任意目标为`www.sportcampus.cn`请求，utoken、cookie、UUID在http请求头中，

场地信标信息除了通过信标（iBeacon）扫描软件获取，也可以直接使用下面章节的iOS加解密方法进行解密从"POST .../dataListByDevice/2"请求体中获取

### 安卓

由于安卓的新版高校体育启用了SSL Pinning，想抓包极其麻烦，建议直接手机密码登录，并通过信标（iBeacon）扫描软件当场扫描获取场地iBeacon信标信息

如果你执意要抓包，并拥有root设备，可以参考[这篇教程](https://blog.anzupop.com/posts/cracking-sportcampus/)，获取utoken、cookie等信息，然后抓取场地信标请求，并解密请求体即可获取iBeacon信标信息

## 关于加密和签名

以下结论均为脱壳+反编译得来，仅保证当前版本有效，推测服务端是是根据请求Header的Platform字段来决定使用哪个平台的加解密和签名算法

## 安卓(高校体育版本号2.9.8)

### sign算法

sign算法没有太大变化，仍为`salt+"data"+JSON文本`，但是salt的值变为了`nO5Mm4zggvrbYyIJ0zbnKkq2sdb~4KscsiscARpd`

### 加密

对于一些请求的data，新版用了AES/CBC/PKCS7Padding进行加密，**注意AES工作模式是CBC模式**，密钥为`nO5Mm4zggvrbYyIJ`，IV为`1111111111111111`

## iOS(高校体育版本号2.2.48)

### sign算法

sign算法没有太大变化，仍为`salt+"data"+JSON文本`，但是salt的值变为了`MITY@*TeYBBZrBAYrLCm8U.2Y+Pt0@vltP1U$.X$`

### 加密

高校体育使用`CCCrypt`方法进行加密，传递的`CCOption`是`0x3`，也就是`kCCOptionPKCS7Padding | kCCOptionECBMode`，**注意AES工作模式是ECB模式**，密钥为`OmZw5Vk9YRIctFbD`

## 更新日志

v1.0: 首次发布

v1.1: bug修复

v1.2: 加入utoken登录方法

v2.0: 支持了最新版本（2.9.8）的安卓版高校体育

v2.1: 支持了最新版本（2.2.48）的iOS版本高校体育

# 以下是如何远程跑步刷锻
1.在电脑上下载雷神模拟器 <br>
2.在浏览器上搜索fake location以及高校体育app进行下载（在雷神自带的应用中心中没有资源），其中fate location需要你充值9块一个月的会员专业版，
fakelocation界面如下，设置路径，记得更改速度和循环次数，启动模拟
![image](https://github.com/FAUST-BENCHOU/TJsportsCampusHelper/assets/126341483/12d26aa8-81a0-4745-9330-dad9d46143f9)

3.雷神模拟器中打开高校体育，开始跑步即可<br>
#### 具体跑步刷锻操作可参考[b站一片叶](https://www.bilibili.com/video/BV1BX4y1G7u3/?spm_id_from=333.880.my_history.page.click&vd_source=2b5cff4a90d42367005014f1d6d11ec0)


