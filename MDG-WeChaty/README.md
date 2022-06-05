modelarts-wechaty

## Inital

```bash
npm install qrcode-terminal --save
npm install wechaty 
npm install wechaty-puppet-service --save // 这个依赖是关键
export WECHATY_PUPPET=wechaty-puppet-service // 这个很关键
export WECHATY_PUPPET_SERVICE_TOKEN="${TOKEN}" // 这个很关键
```

## Add Config

- config.js

```
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
export default config
```

## Npm Install

```bash
npm install
```

## Run

```bash
npm run dev
```
