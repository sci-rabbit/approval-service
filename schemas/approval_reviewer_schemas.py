from pydantic import BaseModel, ConfigDict


class ReviewerResponse(BaseModel):
    reviewer_user_id: str

    model_config = ConfigDict(from_attributes=True)
