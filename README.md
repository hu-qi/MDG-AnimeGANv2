# MDG-AnimateGANv2

## Run AnimateGANv2 service

```bash
wget https://obs-aigallery-zc.obs.cn-north-4.myhuaweicloud.com/clf/code/AnimeGAN/AnimeGAN.zip
# or
# curl -O https://obs-aigallery-zc.obs.cn-north-4.myhuaweicloud.com/clf/code/AnimeGAN/AnimeGAN.zip
unzip AnimeGAN.zip
cp app.py ./AnimeGANv2
cp animeGANv2.py ./AnimeGANv2
cd ./AnimeGANv2 && python app.py
# after run on http://127.0.0.1:5000
```

## Run WeChaty

```bash
cd MDG-WeChaty
npm install
export WECHATY_PUPPET_SERVICE_TOKEN=YOURTOKEN
npm run dev
```

## Notice

```
SyntaxError: Unexpected token < in JSON at position 0
    at JSON.parse (<anonymous>)
    at IncomingMessage.<anonymous> (MDG-AnimeGANv2\MDG-WeChaty\node_modules\wechaty-puppet-service\dist\src\client\puppet-service.js:59:34)
    at IncomingMessage.emit (node:events:539:35)
    at IncomingMessage.emit (node:domain:475:12)
    at endReadableNT (node:internal/streams/readable:1345:12)  
    at proce
```

Modify puppet-service.js:59 to: 

```javascript
try {
    resolve(JSON.parse(body));
}catch(err) {
    return {}
}
```