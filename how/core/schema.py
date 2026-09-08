from pydantic import BaseModel, Field


class Result(BaseModel):
    commands: list[str] = Field(description="Commands to run in sequential order")
    confidence: float = Field(
        description="Value between 0-1 (with precision of two decimal places) representing a confidence score about the success rate, not leading to any errors or interventions."
    )
    status: str = Field(
        description="Status of the response (can be 'success' or anything else in case of error)"
    )
