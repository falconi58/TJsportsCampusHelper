const https = require("https");
const fs = require("fs")
var crypto = require('crypto');
const {
    v4: uuidv4
} = require('uuid');
const HOST = "www.sportcampus.cn"
var uuid = uuidv4();
var utoken = "";
const readline = require('readline');
const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

async function sendHttpRequest(host, port, route, headers = {}, encoding = 'utf8', sendData) {
    let options = {
        hostname: host,
        port: port,
        path: '/' + route,
        method: sendData == "get" ? "GET" : "POST",
        headers: headers
    };
    let data = '';
    return new Promise(function (resolve, reject) {
        let req = https.request(options, function (res) {
            res.setEncoding(encoding);
            res.on('data', function (chunk) {
                data += chunk;
            });
            res.on('end', function () {
                resolve({
                    data: data,
                    code: res.statusCode
                });
            });
        });
        if (sendData != "get") {
            req.write(sendData);
        }
        req.on('error', (e) => {
            resolve(e.message);
        });
        req.end();
    });
}
async function readlineSync(question) {
    return new Promise((resolve, reject) => {
        rl.question(question, (ans) => {
            resolve(ans);
            rl.close()
        })
    })
}

function parseSendData(data) {
    return `data=${data}&sign=${crypto.createHash('md5').update("lpKK*TJE8WaIg%93O0pfn0#xS0i3xE$zdata" + data).digest("hex")}`
}
(async () => {
    console.warn("读取配置文件...");
    var userInfo = {};
    var spotInfo = {};
    var autoSign = false;
    try {
        var config = JSON.parse(fs.readFileSync("./config.json", 'utf8'));
        spotInfo = config.spotInfo;
        userInfo = config.userInfo;
        autoSign = config.autoSign;
    } catch (e) {
        console.warn("配置文件无效。");
        process.exit();
    }
    if (!config.userInfo.useToken) {
        console.warn("正在尝试登录...");
        var loginResult = JSON.parse((await sendHttpRequest(HOST, 443, "/api/reg/login", {
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"
        }, "utf8", parseSendData(JSON.stringify({ info: uuid, mobile: userInfo.phone, password: userInfo.password, type: "iPhone13,3" })))).data)
        if (loginResult.code != "200") {
            console.warn("登录失败。");
            process.exit();
        }
        utoken = loginResult.data.utoken;
    } else {
        console.warn("使用utoken登录...");
        utoken = config.userInfo.utoken;
    }
    console.warn("正在获取签到点...");
    var ibeacon = JSON.stringify({
        type: 2,
        isBreakPoint: 1,
        ibeacons: JSON.stringify([spotInfo])
    })
    var spotResult = JSON.parse((await sendHttpRequest(HOST, 443, "/api/association/dataListByDevice/2", {
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        "utoken": utoken
    }, "utf8", parseSendData(ibeacon))).data);
    if (spotResult.code != "200") {
        console.warn("获取签到点失败。");
        process.exit();
    }
    if (!spotResult.data[0]?.nonce) {
        console.warn("获取签到点失败。");
        process.exit();
    }
    console.warn(`签到点：${spotResult.data[0].name}，可签到时间：${spotResult.data[0].sign_range}`)
    if (!autoSign) {
        var input = await readlineSync("要签到吗？(y/n) ");
        if (input != "y") {
            process.exit();
        }
    } else {
        console.warn("已设置为自动签到");
    }
    console.warn("尝试签到...");
    var exerciseTime = 1800 + 5 * Math.random();
    var timeStampEnd = (new Date).getTime() / 1000 - Math.random();
    var timeStampStart = timeStampEnd - exerciseTime;
    var signObj = {
        nonce: spotResult.data[0].nonce,
        ass_id: spotResult.data[0].ass_id,
        extra: [{
            endTime: timeStampEnd,
            duration: exerciseTime,
            startTime: timeStampStart
        }]
    };
    var signResult = JSON.parse((await sendHttpRequest(HOST, 443, "/api/association/doSign", {
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        "utoken": utoken
    }, "utf8", parseSendData(JSON.stringify(signObj)))).data);
    console.warn(signResult.msg)
})()
