import pandas as pd
import os
from utils import doc_processor
from utils import llm_chains
from configarations.config import all_config
from langchain_community.vectorstores import Chroma




def bid_eval_doc_processor(info_data):
    cba_path=info_data['cba_path']
    pdf_file=info_data['pdf_file']
    bidder_name=info_data['bidder_name']
    bidder_id=info_data['bidder_id']
    bidder_path=info_data['bidder_path']

    cba_doc=doc_processor.get_field_info(cba_path=cba_path)
    imgs=doc_processor.create_and_save_imgs(pdf_file=pdf_file)
    info=doc_processor.format_and_create_documents(imgs)
    qa_chain=llm_chains.get_metadata_qa_chain(llm=all_config["llm"])
    
    docs,meta_info=doc_processor.convert_to_doc(info,get_meta_flag=True,bidder_name=bidder_name,qachain=qa_chain)
    midf=pd.DataFrame(meta_info)
    meta_df=midf[midf.value_of_fields!=""]
    meta_df=meta_df[~meta_df.value_of_fields.str.contains("Not provided",case=False)]
    meta_df=meta_df[~meta_df.value_of_fields.str.contains("Not Available",case=False)]
    meta_df=meta_df[~meta_df.value_of_fields.str.contains("N/A",case=False)]
    if os.path.exist(bidder_path+"/meta_info.csv"):
        _prev_meta_info=pd.read_csv(bidder_path+"/meta_info.csv")
        meta_df=_prev_meta_info.append(meta_df,ignore_index=True)
    meta_df.to_csv(bidder_path+"/meta_info.csv",index=False)
    vdb=Chroma.from_documents(documents=docs,embedding=all_config["embedding"],collection_name=bidder_id,persist_directory="DataBases")
    #all_info=doc_processor.extract(vdb,field_info=cba_doc,bidder_name="HPCL",actual_df=meta_df,extract_qachains=extract_qachains,desc_qachain=desc_qachain,class_qachain=class_qachain)
    return {
        "meta_df":bidder_path+"/meta_info.csv"
    }

def bid_eval_doc_extractor():
    extract_qachains=llm_chains.get_extraction_qa_chains(llm=all_config["llm"])
    desc_qachain = llm_chains.get_description_qa_chain(llm=all_config["llm"])
    class_qachain = llm_chains.get_classification_qa_chain(llm=all_config["llm"])
    #all_info=doc_processor.extract(vdb,field_info=cba_doc,bidder_name="HPCL",actual_df=meta_df,extract_qachains=extract_qachains,desc_qachain=desc_qachain,class_qachain=class_qachain)


