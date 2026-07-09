from pydantic import BaseModel, Field


class CopilotQueryRequest(BaseModel):
    query: str = Field(min_length=3, max_length=1000)


class CopilotSuggestedQuestion(BaseModel):
    category: str
    question: str


class CopilotQueryResponse(BaseModel):
    mode: str
    title: str
    answer: str
    supporting_facts: list[str]
    recommended_actions: list[str]
    inspected_sources: list[str]
