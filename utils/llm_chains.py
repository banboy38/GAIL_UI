from langchain.prompts import PromptTemplate

from utils.schemas import MetaDataSchema, ExtractionSchema, CurrencyExtractionSchema, DescriptionEnhanceMent, FieldClassification

def get_metadata_qa_chain(llm):
    print("Getting MetaData QA Chain...")
    meta_template = PromptTemplate.from_template(
        ''' You are a helpful assistant. You are working for GAIL to extract bidding information provided by Bidder ({bidder}).
        
        Extract Information from the given context which will help in Evaluating the bid.
        Some information like can be extracted. Example
        - GST No
        - PAN no
        - Email ID
        - Phone Number/ mobile number

        Some of the Categories are defined as follows -
        - Address - A full street address with City, State and ZIP Code
        - Phone Number - A 10 digit phone/mobile number
        - Email - An email address
        - Company/Firm Name - The name of a company or firm like pvt. ltd., inc., co., llc., corp.
        - Person Name - The name of a person
        - Accountant Information - Information regarding chartered accountants mentioned
            
        Context
        ---
        {context}
        
        
        ''')
    meta_qachain = meta_template | llm.with_structured_output(MetaDataSchema)
    print("Done!")
    return meta_qachain

def get_extraction_qa_chains(llm):
    print("Getting Extraction QA Chains...")
    extract_template = PromptTemplate.from_template(
        ''' You are a helpful assistant. You are working for GAIL to extract bidding information provided by Bidder ({bidder})
        
        You are given `Context` form which you need to get information for the following `Field` given the `Field Type` and `Field Definition`
        
        Extracted_infomation:
        ---
        {tab_information}
        
        
        Context
        ---
        {context}
        
        Output Field Information
        ---
        Field: {field}
        Field Type: {field_type}
        Field Definition: {field_desc}
        
        
        // NOTE : Answer only in the given Field Type, No verbose requried
        '''
        )
    extract_qachain = extract_template | llm.with_structured_output(ExtractionSchema)
    currency_extract_qachain = extract_template | llm.with_structured_output(CurrencyExtractionSchema)
    print("Done!")
    return {"extract_qachain" : extract_qachain, "currency_extract_qachain" : currency_extract_qachain}

def get_description_qa_chain(llm):
    print("Getting Description QA Chain...")
    desc_template = PromptTemplate.from_template(
        '''
        Given the information below. Can you expand on the Field Description? The following fields are required to evaluate the bidder.
        
        
        ### Field Definition: {field_desc}
        ### Field: {field}
        ### Field Type: {field_type}
        
        '''
        )
    desc_qachain = desc_template | llm.with_structured_output(DescriptionEnhanceMent)
    print("Done!")
    return desc_qachain

def get_classification_qa_chain(llm):
    print("Getting Classifiation QA Chain...")
    class_template = PromptTemplate.from_template(
        '''
        Classify the Field into the given categories
        
        Field Definition: {field_desc}
        Field: {field}
        Field Type : {field_type}
        
        '''
        )
    class_qachain = class_template | llm.with_structured_output(FieldClassification)
    print("Done!")
    return class_qachain