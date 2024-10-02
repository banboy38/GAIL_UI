from pydantic import BaseModel, Field
from typing import Literal

class Information(BaseModel):
    name_of_fields:str=Field(description="Field Name, with proper information")
    value_of_fields:str=Field(description="Field Value")
    description_of_field:str=Field(description="Description of the Field")
    field_type:Literal["Contact Information",
                       "Identification Number",
                       "Document Identification",
                       "Financials",
                       "Address",
                       "Phone Number",
                       "Email",
                       "Company/Firm Name",
                       "Person Name",
                       "Date",
                       "Other",
                       "Accountant Information",
                       "Legal Information"]=Field(description="Type of the Field")
    document_name:str=Field(description="Name of the document or Form Number")
    contextual_meaning:str=Field(description="Contextual Understanding of the Field Value")
    
class MetaDataSchema(BaseModel):
    value:list[Information]=Field(description="Value for the given Field")

class ExtractionSchema(BaseModel):
    value:str=Field(description="Value for the given Field")

class CurrencyExtractionSchema(BaseModel):
    value:float=Field(description="Value for the given Field in Floating Point format")
        
class FieldClassification(BaseModel):
    classi:Literal["Contact Information",
                    "Identification Number",
                    "Document Identification",
                    "Financials",
                    "Address",
                    "Phone Number",
                    "Email",
                    "Company/Firm Name",
                    "Person Name",
                    "Date",
                    "Other",
                    "Accountant Information",
                    "Legal Information"]=Field(description="Type of the Field, Example: Documents, Address, etc")
        
class DescriptionEnhanceMent(BaseModel):
    desc:str=Field(description="Given the Field name, type and description, expand on the description")