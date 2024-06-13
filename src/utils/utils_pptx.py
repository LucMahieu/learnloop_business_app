from dotenv import load_dotenv
import os
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE
from openai import OpenAI
import streamlit as st
import base64
import requests
import pandas as pd
import sys
import comtypes.client
from pdf2image import convert_from_path
from io import BytesIO
import io
import pythoncom
import json
import altair as alt
from PIL import Image
import tempfile
import pathlib

load_dotenv()
client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"), 
            organization=os.getenv("ORG_ID"))


def pptx_to_pdf(input_file_path, output_file_path):
    pythoncom.CoInitialize()
    input_file_path = os.path.abspath(input_file_path)
    output_file_path = os.path.abspath(output_file_path)
    powerpoint = comtypes.client.CreateObject("Powerpoint.Application")
    powerpoint.Visible = 2
    slides = powerpoint.Presentations.Open(input_file_path)
    slides.SaveAs(output_file_path, 32)
    slides.Close()
    powerpoint.Quit()
    pythoncom.CoUninitialize()

def pdf_to_base64_images(pdf_path):
    images = convert_from_path(pdf_path)
    base64_images = []
    for image in images:
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        base64_image = base64.b64encode(buffered.getvalue()).decode('utf-8')
        base64_images.append(base64_image)
    return base64_images

def json_to_df(json_data, columns ):
    try:
        data = json.loads(json_data)
        df = pd.DataFrame(list(data.items()), columns=columns)
        return df
    except:
        data = [['No Response', 0]]
        df = pd.DataFrame([], columns=columns)
        return df


class PowerPoint:
    def __init__(self, uploaded_file):
        self.uploaded_file = uploaded_file
    
    def save_uploaded_file(self):
        temp_dir = tempfile.TemporaryDirectory(delete = False)
        uploaded_file_path = os.path.join(temp_dir.name,'temp.pptx')
        with open(uploaded_file_path, 'wb') as f:
            f.write(self.uploaded_file)
            f.close()
        return temp_dir.name

    def pptx_image_base64_list(self, input_file_path, output_file_path):
        pptx_to_pdf(input_file_path, output_file_path)
        image_base64_list = pdf_to_base64_images(output_file_path)
        return image_base64_list

    def response_image_base64_list_openai(self,  template, image_base64_list):
        f = open(  f"assets/prompts/{template}.txt", "r" ).read()
        response_list = []
        for image_base64 in image_base64_list:
            system_content = [ {"type": "text", "text": f}  ]
            user_content =  [{
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}]
            if template == "pptx_scores":
                response_format = { "type": "json_object" }
            else:
                response_format = { "type": "text"}
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[ {   "role": "system", "content":  system_content },
                          {   "role": "user", "content": user_content}],
                response_format=response_format)
            response_list.append(  response.choices[0].message.content )
        return response_list
