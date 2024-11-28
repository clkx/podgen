from pydantic import BaseModel, Field
from typing import List

class SearchQuery(BaseModel):
    search_query: str = Field(None, description="Search query for retrieval.")

class Analyst(BaseModel):
    affiliation: str = Field(description="Primary affiliation of the analyst.")
    name: str = Field(description="Name of the analyst.")
    role: str = Field(description="Role of the analyst in the context of the topic.")
    description: str = Field(description="Description of the analyst focus, concerns, and motives.")
    
    @property
    def persona(self) -> str:
        return f"Name: {self.name}\nRole: {self.role}\nAffiliation: {self.affiliation}\nDescription: {self.description}\n"


class Perspectives(BaseModel):
    analysts: List[Analyst] = Field(description="Comprehensive list of analysts with their roles and affiliations.")

class ArxivScriptRequest(BaseModel):
    arxiv_url: str = Field(..., description="arXiv 論文的 URL")
    host_name: str = Field(..., description="主持人名稱")
    host_background: str = Field(..., description="主持人背景")
    guest_name: str = Field(..., description="來賓名稱")
    guest_background: str = Field(..., description="來賓背景")