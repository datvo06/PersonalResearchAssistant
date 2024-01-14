from langchain.chat_models import ChatOpenAI
from settings import OPENAI_API_KEY, PDF_DICT_PATH, PDF_DB_DIR, PDF_RESULT_PATH, PDF_RESULT_DIR, OBSIDIAN_PATH, PDF_RESULT_DIR_LIGHT, PDF_RESULT_PATH_LIGHT
openai.api_key = OPENAI_API_KEY


def get_gpt4_llm():
    return ChatOpenAI(model_name = "gpt-4")


def get_gpt35_turbo_llm():
    return ChatOpenAI(model_name = "gpt-3.5-turbo")



@backoff.on_exception(backoff.expo, openai.error.OpenAIError, giveup=giveup_if_invalid_request, logger=utils_logger)
def call_gpt_with_backoff(messages: List, model: str = "gpt-4", temperature: float = 0.7, max_length: int = 256) -> str:
    """
    Function to call GPT and handle exceptions with an exponential backoff. This is best used when retrying during high demand.
    """
    try:
        response = call_gpt(
            model=model,
            messages=messages,
            temperature=temperature,
            max_length=max_length
        )
        return response
    except openai.error.InvalidRequestError as e:
        utils_logger.exception(e)      
        raise e


def call_gpt(messages: List, model: str = "gpt-4", temperature: float = 0.7, max_length: int = 256) -> str:
    """
    Generic function to call GPT4 with specified messages
    """
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_length,
        frequency_penalty=0.0,
        top_p=1
    )
    return response['choices'][0]['message']['content']

