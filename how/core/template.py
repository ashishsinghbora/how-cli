from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate

from how.core.parser import PARSER
from how.core.prompts import FEW_SHOT_EXAMPLES, SYSTEM_PROMPT

example_template = ChatPromptTemplate.from_messages(
    [("human", "How to {task}?"), ("ai", "{output}")]
)

few_shot_examples_template = FewShotChatMessagePromptTemplate(
    example_prompt=example_template, examples=FEW_SHOT_EXAMPLES
)

PROMPT_TEMPLATE = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT + "\n{context}\n{format_instructions}"),
        few_shot_examples_template,
        ("human", "How to {task}?"),
    ]
).partial(
    format_instructions=PARSER.get_format_instructions(),
    context="",
)
