from pathlib import Path
from io import BytesIO
import base64
from functools import lru_cache
from PIL import Image
from playwright.sync_api import sync_playwright

@lru_cache(maxsize=1)
def models():
    from transformers import CLIPModel, CLIPProcessor, AutoProcessor, AutoModelForImageTextToText
    clip='openai/clip-vit-base-patch32'
    vlm='HuggingFaceTB/SmolVLM-256M-Instruct'
    return CLIPModel.from_pretrained(clip).eval(), CLIPProcessor.from_pretrained(clip), AutoModelForImageTextToText.from_pretrained(vlm).eval(), AutoProcessor.from_pretrained(vlm)

def ask(question, state):
    import torch
    regions=[('Indicadores y presupuesto','.grid'),('Menú semanal','.columns >> nth=0'),('Compras e inventario','.columns >> nth=1'),('Recetas','#recipeRows')]
    captures=[]
    with sync_playwright() as p:
        browser=p.chromium.launch()
        try:
            page=browser.new_page(viewport={'width':1440,'height':1000})
            page.goto('http://127.0.0.1:8000/')
            page.evaluate('''s=>{data=s.data;for(const k of ['people','budget','reserve'])document.getElementById(k).value=s[k];render()}''',state)
            for name, selector in regions:
                captures.append((name,page.locator(selector).screenshot()))
        finally: browser.close()
    images=[Image.open(BytesIO(b)).convert('RGB') for _,b in captures]
    clip,proc,vlm,processor=models()
    with torch.inference_mode():
        inputs=proc(text=[question],images=images,return_tensors='pt',padding=True,truncation=True)
        idx=clip(**inputs).logits_per_image[:,0].topk(2).indices.tolist()
        messages=[{'role':'user','content':[{'type':'image'} for _ in idx]+[{'type':'text','text':f'Responde en español usando solo las imágenes. Si no puedes leer un valor, indícalo. Pregunta: {question}'}]}]
        prompt=processor.apply_chat_template(messages,add_generation_prompt=True)
        inputs=processor(text=prompt,images=[images[i] for i in idx],return_tensors='pt')
        output=vlm.generate(**inputs,max_new_tokens=180,do_sample=False)
        answer=processor.batch_decode(output[:,inputs['input_ids'].shape[1]:],skip_special_tokens=True)[0]
    return {'answer':answer,'evidence':[{'name':captures[i][0],'image':base64.b64encode(captures[i][1]).decode()} for i in idx]}
