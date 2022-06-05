from flask import *
# import request
import os
import uuid
import numpy as np
from animeGANv2 import *

app = Flask(__name__,template_folder='view')
app.config['MAX_CONTENT_LENGTH'] = 0.5 * 1024 * 1024  # 3MB

@app.route('/postdata', methods=['POST'])
def postdata():
    print(request)
    f = request.files['content']
    print(f)
    user_input = request.form.get("name")
    basepath = os.path.dirname(__file__)  # 当前文件所在路径
    src_imgname = str(uuid.uuid1()) + ".jpg"
    upload_path = os.path.join(basepath, 'static/srcImg/')
    
    if os.path.exists(upload_path)==False:
        os.makedirs(upload_path)
    f.save(upload_path + src_imgname)
    # img = cv2.imread(upload_path + src_imgname, 1)
 
    save_path = os.path.join(basepath, 'static/resImg/')
    if os.path.exists(save_path) == False:
        os.makedirs(save_path)
    fileSize = os.path.getsize(upload_path+src_imgname)
    if(fileSize / 1024 / 1024 > 1):
        resSets = dict()
        resSets["value"] = 10
        resSets["resurl"] = "http://127.0.0.1:5000" +'/static/resImg/' + src_imgname
    else:
        inference_from_file(upload_path+src_imgname,os.path.join(save_path, src_imgname))
        resSets = dict()
        resSets["value"] = 10
        resSets["resurl"] = "http://127.0.0.1:5000" +'/static/resImg/' + src_imgname
    return json.dumps(resSets, ensure_ascii=False)


@app.route('/postdataUrl', methods=['POST'])
def postdataUrl():
    url = request.values['content']
    print(url)
    user_input = request.form.get("name")
    basepath = os.path.dirname(__file__)  # 当前文件所在路径
    src_imgname = str(uuid.uuid1()) + ".jpg"
 
    save_path = os.path.join(basepath, 'static/resImg/')
    if os.path.exists(save_path) == False:
        os.makedirs(save_path)
    inference_from_url(url,os.path.join(save_path, src_imgname))
    resSets = dict()
    resSets["value"] = 10
    resSets["resurl"] = "http://127.0.0.1:5000" +'/static/resImg/' + src_imgname
    return json.dumps(resSets, ensure_ascii=False)
 
if __name__ == '__main__':
   app.run(threaded=True)