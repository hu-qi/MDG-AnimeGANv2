const { Wechaty, FileBox } = require('wechaty');

const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');
const config = require('./config');
const fetch = require('node-fetch')

const name = 'wechat-puppet-wechat';
let bot = '';
bot = new Wechaty({
    name, // generate xxxx.memory-card.json and save login data for the next login
    puppet: 'wechaty-puppet-service',
    puppetOptions: {
        token: config.Token,
    }
});

//  二维码生成
function onScan(qrcode, status) {
    require('qrcode-terminal').generate(qrcode); // 在console端显示二维码
    const qrcodeImageUrl = [
        'https://wechaty.js.org/qrcode/',
        encodeURIComponent(qrcode),
    ].join('');
    console.log(qrcodeImageUrl);
}

// 登录
async function onLogin(user) {
    console.log(`贴心小助理${user}登录了`);
      if (config.TULING.isOn) {
        console.log(`已开启机器人自动聊天模式`);
      }
    // 登陆后创建定时任务
    // await initDay();
}

//登出
function onLogout(user) {
    console.log(`小助手${user} 已经登出`);
}

bot.on('scan', onScan);
bot.on('login', onLogin);
bot.on('logout', onLogout);
bot
    .start()
    .then(() => console.log('开始登陆微信'))
    .catch((e) => console.error(e));

// 监听消息
bot.on('message', async function (m) {
    console.log('--------message--------')
    console.log(m)
    const contact = m.talker();
    const content = m.text();
    const room = m.room();
    let contactList = [];
    if (room) {
        console.log('--------room--------');
        console.log(room)
        console.log(`Room:${room.topic()},${contact}发来${content}`)
        if (config.ROOMID.includes(room.id)) {
            if (/^动漫化$/i.test(content)) { 
                m.say('请您发一张图片,尽量小点');
                if (contactList.length == 0) {       //如果列表为空,说明没有food监听。
                    contactList.push(contact);

                    bot.on('message', async function food(n) {
                        // console.log('food监听')
                        const contact1 = n.talker();
                        const content1 = n.text();
                        if (/^动漫化$/i.test(content1) || n.self()) return;
                        // console.log('speak2');
                        contactList.forEach(async (person, index) => {   //如果在列表中且是同一个人。
                            if (person == contact1) {
                                console.log(n)
                                if (n.type() == bot.Message.Type.Image) {  //发送的是图片格式
                                    n.say(`${contact1},我们正在飞速画出您的照片,请耐心等待。`);
                                    await saveMediaFile(n);

                                } else {
                                    n.say('发送的不是图片格式,请重新发送关键字.');
                                }
                                n.say('了解更多请点击：huaweicloud.ai')
                                contactList.splice(index, 1)//移除这个人
                                return  //每个人只可能出现一次,所以出现一次后,就终止。
                            }
                        })
                        if (!contactList.length) bot.removeListener('message', food);  //如果列表为空,则移除监听。
                    })
                }
                else if (!contactList.includes(contact)) contactList.push(contact); //列表中如果已有此人,就不添加。

            } else if (content.includes('头像')) {
                m.say('图像生成中……');
                sendImagesUrl(contact.payload.avatar).then(async res => {
                    console.log('url res')
                    console.log(res)
                    if (res) {
                        console.log(res.resurl)
                        if (res.value) {
                            fetch(res.resurl).then(file => {
                                return file.buffer()
                            }).then(buffer => {
                                const resultName = './avatars/' + contact.payload.weixin + '.png'
                                fs.writeFile(resultName, buffer, async (a, b) => {
                                    //    console.log(a,b)
                                    const _fileBox = FileBox.fromFile(resultName)
                                    m.say(_fileBox)
                                })
                            }).catch(err => {
                                m.say("对不起，我崩溃了~")
                            })

                        } else if (res.value === 0) {
                            m.say("图片不能超过1M哦~@" + m.talker())
                        } else {
                            m.say('偶被外星人抓走了~')
                        }

                    }
                }).catch(err => {
                    console.log('url err')
                    console.log(err)
                })
            } else if (config.TULING.isOn) {
                // 对话机器人
                if (m.type() == bot.Message.Type.Text) {
                    let sayText = await sendText(m.text())
                    console.log(sayText)
                    sayText && m.say(sayText)
                }
            }
        } else {
            console.log("非关注的群聊，忽略对话~")
            return
        }
    } else {
        console.log(`非群聊，${contact}:${content}`)
    }
    if (m.self()) return;
})

// 保存图片
async function saveMediaFile(message) {
    const image = message.toImage()
    const fileBox = await image.artwork()
    const fileName = './images/' + fileBox.name
    const resultName = './results/' + fileBox.name
    fileBox.toFile(fileName).then(_res => {
        sendImages(fileName).then(async res => {
            if (res) {
                console.log(res.resurl)
                if (res.value) {
                    fetch(res.resurl).then(file => {
                        return file.buffer()
                    }).then(buffer => {
                        fs.writeFile(resultName, buffer, async (a, b) => {
                            const _fileBox = FileBox.fromFile(resultName)
                            message.say(_fileBox)
                        })
                    }).catch(err => {
                        message.say("对不起，我崩溃了~")
                    })

                } else {
                    message.say("图片不能超过1M哦~@" + message.talker())
                }

            }
        }).catch(err => {
            console.log(err)
        })
    }).catch(err => {
        console.log('err:')
        console.log(err)
    })
}

// 生成动漫化图片
async function sendImages(fileName) {
    let resp = {}
    console.log('start')
    const form = new FormData();
    form.append('content', fs.createReadStream(fileName));
    await fetch(config.AnimateImg, {
        method: "post",
        body: form
    }).then(res =>
        res.json()
    ).then(json => {
        console.log(json)
        resp = json
    }).catch(err => {
        console.log('err')
        console.log(err)
        resp = err
    })

    return resp
}

// 生成动漫头像
async function sendImagesUrl(url) {
    let resp = {}
    console.log('start url')
    const form = new FormData();
    form.append('content', url);
    await fetch(config.AnimateUrl, {
        method: "post",
        body: form
    }).then(res =>
        res.json()
    ).then(json => {
        console.log(json)
        resp = json
    }).catch(err => {
        console.log('err')
        console.log(err)
        // if (err.response && err.response.data) {
        //     resp = err.response.data
        // }
        resp = err
    })

    return resp
}

// 图灵对话
async function sendText(text) {
    let respText = ''
    console.log('send tuling', text)
    console.log(Object.assign(config.TULING.userInfo, {
        "reqType": 0, // 默认文本
        "perception": {
            "inputText": {
                "text": text
            }
        }
    }))
    const _data = {
        "perception": {
            "inputText": {
                "text": text
            }
        },
        "userInfo": {
            "apiKey": config.TULING.userInfo.apiKey,
            "userId": config.TULING.userInfo.userId
        }
    };
    await axios({
        method: 'POST',
        url: config.TULING.url,
        data: _data
    })
        .then(res => {
            console.log('-------- tuling res --------')
            console.dir(res.data.results[0].values.text)
            respText = res.data.results[0].values.text
        }).catch(err => {
            console.log(err)
        })
    return respText
}