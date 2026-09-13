from pydantic import BaseModel, ConfigDict


class LanguageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str
    name: str
    native_name: str
