from langchain_core.output_parsers import JsonOutputParser

from how.core.schema import Result

PARSER = JsonOutputParser(pydantic_object=Result)
