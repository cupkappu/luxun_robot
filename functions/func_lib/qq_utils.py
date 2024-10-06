import requests
from PIL import Image
import base64
from io import BytesIO
import os

def process_cq(cq_messages,img_llm: bool = True):
    # 用于使用llm解析图片
    cqs = []
    for item in cq_messages:
        # 步骤2：将cq码解析成字典形式
        cq_content = item[4:-1]  # 移除[CQ:和]
        cq_parts = cq_content.split(",")  # 按照,分割
        cq_dict = {"type": "cq_code", "cq": {"cqType": cq_parts[0]}}
        for part in cq_parts[1:]:
            key, value = part.split("=", 1)  # 在第一个等号处分割字符串
            cq_dict["cq"][key] = value
        if (cq_dict['cq']['cqType']=='image'):
            cqs.append(
                {'image':vision(cq_dict['cq']['file'])}
            )
        if cq_dict['cq']['cqType']=='at':
            cqs.append({'at':cq_dict['cq']['qq']})
    return cqs

def vision(imgfilename):
    getimginfoUrl = os.getenv('QQ_ONEBOT_HTTP_URL')+"/get_image"
    info=requests.get(getimginfoUrl,params={"file":imgfilename})
    file = info.json()['data']['file']
    filename=file.replace("/root/.config/QQ/", "")
    url=os.getenv('QQ_IMAGE_SERVER')+filename
    response = requests.get(url)
    # print(response)
    img = Image.open(BytesIO(response.content))
    jpg = BytesIO()
    img.convert('RGB').save(jpg, format='JPEG')
    jpg.seek(0)
    text = base64.b64encode(jpg.read()).decode()
    return text