from pydantic import BaseModel

def to_camel(string: str) -> str:
    components = string.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


class RequestResponseBaseModel(BaseModel):

    class Config:
        alias_generator = to_camel
        populate_by_name = True
        arbitrary_types_allowed = True