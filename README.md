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
npm run dev
```

> Changelog：[change to UOS web](https://wechaty.js.org/2022/07/22/wechaty-office-hour/).

## More Information

See the blog in [wechaty.js.org](https://wechaty.js.org/2022/07/21/three-steps-to-develop-a-chatbot-to-generate-cartoon-avatars-in-one-second/) or in [Ai Gallery](https://developer.huaweicloud.com/develop/aigallery/article/detail?id=ce5e7b98-a738-4833-adad-ef9ce75f9151).

