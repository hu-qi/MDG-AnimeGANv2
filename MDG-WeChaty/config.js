const config =  {
    TOKEN: 'your wechaty Token',
    ROOMID: 'your roomids, like "19366947850@chatroom,19366949527@chatroom"',
    AnimateImg: 'your image animate api url like "http:/127.0.0.1:5000/postdata"',
    AnimateUrl: 'your image animate api url like "http:/127.0.0.1:5000/postdataUrl"',
    TULING: {
        isOn: true,
        url: 'http://openapi.turingapi.com/openapi/api/v2',
        userInfo: {
            apiKey: 'your tuling apikey',
            userId: 'your tuling userid'
        }
    }
}

module.exports = config
