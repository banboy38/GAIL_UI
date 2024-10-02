import pandas as pd
import tqdm
from azure.ai.documentintelligence.models import ContentFormat
import os
import shutil
from pdf2image import convert_from_path
from langchain_core.documents import Document


from configarations.config import all_config
from pathlib import Path

def get_field_info(cba_path):
    print("Getting Field Info...")
    cba_df = pd.read_excel(cba_path)
    field_info = []
    for _,row in cba_df.iterrows():
        field_info.append((row["Type of Parameter"],row["Parameter"], row["Type of Answer"], row["Answer Description"]))
    return field_info


def create_and_save_imgs(pdf_file):
    print("Creating Images...")
    folder_path="TBD_IMGS"
    if os.path.exists(folder_path):
        for root, dirs, files in os.walk(folder_path, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
            
        ##os.makedirs(folder_path)
    else:
        os.makedirs(folder_path)
    IMGS=convert_from_path(pdf_file,poppler_path="TBD/poppler-24.07.0/Library/bin")
    all_imgs=[]
    for idx,img in enumerate(IMGS):
        file_name=f"{folder_path}/img_{idx}.jpg"
        img.save(file_name)
        all_imgs.append({
            "pdf_path":pdf_file,
            "img_path":file_name,
            "page_no":idx+1
        })
    print("Done!")
    return all_imgs

def format_and_create_documents(files):
    print("Formatting and Creating Documents...")
    document_intelligence_client = all_config['doc_intelligence']
    all_doc_info=[]
    for f_path in tqdm.tqdm(files):
        with open(f_path["img_path"], "rb") as f:
    
            poller = document_intelligence_client.begin_analyze_document(
                "prebuilt-layout",
                analyze_request=f,
                output_content_format=ContentFormat.MARKDOWN,
                content_type="application/octet-stream",
            )
        result=poller.result()
        md_data=result.content
        all_doc_info.append(
            {
                "path": f_path['pdf_path'],
                "page_no":f_path["page_no"],
                "content": md_data
            }
        )
    print("Done!")
    return all_doc_info

def convert_to_doc(data,get_meta_flag=False,bidder_name=None,qachain=None):
    print("Converting to Documents...")
    all_docs=[]
    meta_info=[]
    for d in tqdm.tqdm(data):
        metadata={k:v for k,v in d.items() if k!="content"}
        if get_meta_flag == True:
            out=qachain.invoke({
                "context":d['content'],
                "bidder": bidder_name
            })
            meta_info.extend([i.dict() for i in out.value])
        
        all_docs.append(
            Document(page_content=d['content'],metadata=metadata)
        )
    print("Done!")
    return all_docs,meta_info


def extract(vdb,field_info,bidder_name,actual_df,extract_qachains,desc_qachain,class_qachain):
    extracted_data = []
    k_value = 8
    for  info in tqdm.tqdm(field_info):
        field_name = info[1]
        field_type = info[2]
        field_desc = info[3]
        #print("FIELD : " + field_name)
        
        rephrased=desc_qachain.invoke({
                "field":field_name,
                "field_type" : field_type,
                "field_desc": field_desc,
            })
        question=rephrased.desc
        #print("REPHRASED DESCRIPTION : " + str(question))
        
        try:
            
            out=class_qachain.invoke({
                "field" : field_name,
                "field_desc": question,
                "field_type" : field_type
            })
            #print("CLASSIFICATION : " + str(out.classi))
            if out.classi!="Address":
                actual_df_=actual_df[actual_df.field_type==out.classi]
                actual_df_=actual_df_.to_markdown()
            else:
                actual_df_=""
            
        except:
            actual_df_=""
        docs = vdb.similarity_search(query=field_name,k=k_value)
        #print("DOCS : " + str(docs))
        if field_type == "Currency":
            selected_qachain = extract_qachains["currency_extract_qachain"]
        else:
            selected_qachain = extract_qachains["extract_qachain"]

        out = selected_qachain.invoke({
            "context":"\n\n".join([d.page_content for d in docs]),
            "field":field_name,
            "field_type" : field_type,
            "field_desc": question,
            "bidder":bidder_name,
            "tab_information":actual_df_
        })
        extracted_data.append({
            "field":field_name,
            "value":out.value
        })
    return extracted_data