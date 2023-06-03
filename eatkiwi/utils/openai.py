"""
This module provides functions for working with the OpenAI API and the GPT-2 tokenizer.

Functions:
    trim_to_token_max(text: str) -> str:
        Trims the input text to the maximum number of tokens allowed by the GPT-2 tokenizer.

    generate_webpage_summary(page_content: str) -> str:
        Generates a summary of the provided text using the OpenAI API.

    generate_webpage_title_and_summary(page_content: str) -> Tuple[str, str]:
        Generates a title and summary of the provided text using the OpenAI API.

"""
import openai
from typing import Tuple
from decouple import config
from transformers import GPT2Tokenizer
from eatkiwi.utils.strings import remove_substrings, truncate_string_by_character


def trim_to_token_max(text) -> str:
    """
    Trims the input text to the maximum number of tokens allowed by the GPT-2 tokenizer.

    Args:
        text (str): The input text to be trimmed.

    Returns:
        str: The trimmed text.

    """
    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
    max_length = 1024 # tokenizer.max_len_single_sentence
    
    tokens = tokenizer.encode(text, add_special_tokens=False)
    
    if len(tokens) <= max_length:
        return text
    
    # If more than max_length tokens, trim to the last full stop before max_lengthth token
    trimmed_tokens = tokens[:max_length]
    last_full_stop_index = "".join(tokenizer.decode(trimmed_tokens)).rfind(".")
    
    # If there's no full stop in the trimmed text, just cut off at max_length tokens
    if last_full_stop_index == -1:
        return tokenizer.decode(trimmed_tokens)
    
    # Cut off the text at the last full stop
    return tokenizer.decode(trimmed_tokens[:last_full_stop_index + 1])


def generate_pithy_reply() -> str:
    """
    Generates a pithy reply

    Args:
        page_content (str): The text content of the webpage.

    Returns:
        str: The generated reply

    """
    messages = [
        {
            "role": "system",
            "content": "You are a very unique, original, creative and humorous writer. You love sarcasm and wit. Write a very brief (100 characters or less) but creative and sarcastic reply about how you're not hungry or interested right now."
        },
    ]
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages
    )
    return response['choices'][0]['message']['content']


def generate_webpage_title(page_content) -> str:
    """
    Generates a catchy and accurate title for a webpage based on the provided text.

    Args:
        page_content (str): The text content of the webpage.

    Returns:
        str: The generated title.

    """
    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant. Your task is to suggest a catchy and accurate title based on the provided text. The title should not exceed 80 characters."
        },
        {
            "role": "user",
            "content": f"{page_content}"
        }
    ]
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages
    )
    return response['choices'][0]['message']['content']


def generate_webpage_summary(page_content) -> str:
    """
    Generates a summary of the provided text using the OpenAI API.

    Args:
        page_content (str): The text content of the webpage.

    Returns:
        str: The generated summary.

    """
    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant with the style of a New York Times tweet author. Your task is to summarize the following text in no more than 320 bytes."
        },
        {
            "role": "user",
            "content": f"{page_content}"
        }
    ]
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages
    )
    return response['choices'][0]['message']['content']


def generate_webpage_title_and_summary(page_content, writing_style) -> Tuple[str, str]:
    """
    Generates a title and summary of the provided text using the OpenAI API.

    Args:
        page_content (str): The text content of the webpage.

    Returns:
        Tuple[str, str]: A tuple containing the generated title and summary.

    """
    # Reduce the content length to reduce token cost
    trimmed_content = truncate_string_by_character(page_content, max_characters=4000)

    messages = [
        {
            "role": "system",
            "content": "You are a very unique, original, and creative author. You love sarcasm and wit. Your first task is to suggest a very creative and catchy title based on the provided text. The title should not exceed 80 characters. Your second task is to summarize the text in the style of The New Yorker, within a limit of 220 bytes."
        },
        {
            "role": "system",
            "content": "Just return the title and summary separated by new lines, don't introduce them or add extra text. Don't add things like 'Title:' or 'Summary:'."
        },
        {
            "role": "user",
            "content": f"{trimmed_content}"
        }
    ]
    if writing_style is not None:
        messages = [
            {
                "role": "system",
                "content": f"You are a very experienced and creative author. Your first task is to suggest a title in the style of {writing_style} based on the provided text. The title should not exceed 80 characters. Your second task is to summarize the text in the style of {writing_style}, within a limit of 220 characters."
            },
            {
                "role": "system",
                "content": "Just return the title and summary separated by new lines, don't introduce them or add extra text. Don't add things like 'Title:' or 'Summary:'."
            },
            {
                "role": "user",
                "content": f"{trimmed_content}"
            }
        ]
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages
    )

    # The title and summary should be separated by newline spacing
    parts = response['choices'][0]['message']['content'].split('\n\n')

    # Ensure the title and summary exist before assigning
    title = parts[0] if len(parts) > 0 else None
    summary = parts[1] if len(parts) > 1 else None

    # chatgpt adds unwanted substrings in the title and summary
    substrings_to_remove = ["Title: ", "Summary: "]
    title = remove_substrings(title, substrings_to_remove)
    summary = remove_substrings(summary, substrings_to_remove)
    if title is None or title == "" or title == " " or title == "Access denied":
        raise ValueError("Title generation failed.")

    return title, summary