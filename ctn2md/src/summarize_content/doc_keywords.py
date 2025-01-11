"""Document keywords generation module for content analysis"""
from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator
from typing import List

load_dotenv()

class DocumentKeywords(BaseModel):
    """Document keywords structure for LLM-generated content analysis"""
    title: str = Field(
        description="Document title extracted from content"
    )
    
    summary: str = Field(
        description="Comprehensive summary of the document content"
    )
    
    keywords_primary: List[str] = Field(
        description="Primary keywords representing core topics and main concepts",
        example=["seat spacing", "design requirements", "measurement parameters"]
    )
    
    keywords_technical: List[str] = Field(
        description="Technical keywords including specifications, parameters, and technical terms",
        example=["seat centerline", "vertical section", "floor distance 620mm"]
    )
    
    keywords_context: List[str] = Field(
        description="Contextual keywords about industry, standards, and application scenarios",
        example=["automotive industry", "regulatory requirements", "design standards"]
    )
    
    keywords_general: List[str] = Field(
        description="General keywords covering broader categories and concepts",
        example=["vehicle seating", "comfort design", "safety standards"]
    )

    @field_validator('keywords_primary', 'keywords_technical', 'keywords_context', 'keywords_general', mode='before')
    @classmethod
    def split_comma_separated(cls, v):
        """Convert string to list if needed, handling multiple separators: , 、 ； ;"""
        if isinstance(v, str):
            # Replace all possible separators with a common one
            normalized = v.replace('、', ',').replace('；', ',').replace(';', ',')
            return [item.strip() for item in normalized.split(',') if item.strip()]
        return v

