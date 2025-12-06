from pydantic import BaseModel, ConfigDict

class BaseDataModel(BaseModel):
    """Base data model"""
    model_config = ConfigDict(populate_by_name=True)
