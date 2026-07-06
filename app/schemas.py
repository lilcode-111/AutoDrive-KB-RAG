from typing import List
from pydantic import BaseModel

#表示服务是否正常运行
class HealthResponse(BaseModel):  
    status: str
    project: str
    week: str
    message: str

#这是给api/v1/info接口用的
class ProjectInfoResponse(BaseModel):
    project: str
    description: str
    current_stage: str
    completed_modules: List[str]
    next_modules: List[str]

#这是给文档模块接口用的 
class DocumentServiceStatusResponse(BaseModel):
    status:str
    module:str
    message:str

class SupportedFileTypesResponse(BaseModel):
    supported_file_types:List[str]
    note:str

class ParseDocumentResponse(BaseModel):
    filename:str
    file_type:str
    text_length:int
    preview:str
    status:str



