import requests
from PIL import Image
import base64
from io import BytesIO
import os
from llm import vlm
from langchain_core.messages import HumanMessage
from langchain_core.language_models.chat_models import BaseChatModel

async def process_cq(cq_messages,img_llm: bool = True) -> dict:
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
            if img_llm:
                url = get_imgurl(cq_dict['cq']['file'])
                result = file_from_url(url)
                result = base64_from_file(result)
                if result != 'Undecodable image.':
                    result = await vlm_desc(img_b64=result)
                cqs.append(
                    {'image':result,'img_url':url}
                )
            else:
                file = file_from_url(get_imgurl(cq_dict['cq']['file']))
                cqs.append({"image":file.getvalue()})
        if cq_dict['cq']['cqType']=='at':
            cqs.append({'at':cq_dict['cq']['qq']})
    return cqs

def get_imgurl(imgfilename):
    getimginfoUrl = os.getenv('QQ_ONEBOT_HTTP_URL')+"/get_image"
    info=requests.get(getimginfoUrl,params={"file":imgfilename})
    file = info.json()['data']['file']
    filename=file.replace("/root/.config/QQ/", "")
    url=os.getenv('QQ_IMAGE_SERVER')+filename
    return url

def file_from_url(url:str)->BytesIO:
    response = requests.get(url)
    return BytesIO(response.content)

def base64_from_file(file:BytesIO)->str:
    try:
        img = Image.open(file)
        jpg = BytesIO()
        img.convert('RGB').save(jpg, format='JPEG')
        jpg.seek(0)
        text = base64.b64encode(jpg.read()).decode()
    except:
        text = "Undecodable image."
    return text

async def vlm_desc(img_b64: str, 
             vlm:BaseChatModel = vlm,) -> str:
    message = HumanMessage(
        content=[
            {"type": "text", "text": """
             As a professional visual obstacle assistant,
            You need to accurately and simply capture the focus of the image, 
             describe to users
             """.replace('\n','')},
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"},
            },
        ]
    )
    ai_msg = await vlm.ainvoke([message])
    return ai_msg.content
