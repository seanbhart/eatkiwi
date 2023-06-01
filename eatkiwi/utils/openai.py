import openai
import logging
from decouple import config
from transformers import GPT2Tokenizer
from eatkiwi.utils.strings import reduce_word_count, truncate_string_by_character

openai.api_key = config("OPEN_AI_API_KEY")


def trim_to_token_max(text):
    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
    max_length = 1024 # tokenizer.max_len_single_sentence
    
    # Tokenize the text
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

def generate_webpage_title(page_content):
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

def generate_webpage_summary(page_content):
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

def generate_webpage_title_and_summary(page_content):

    # Reduce the content length to reduce token cost
    # trimmed_content = trim_to_token_max(page_content)
    # trimmed_content = reduce_word_count(page_content, max_words=350)
    trimmed_content = truncate_string_by_character(page_content, max_characters=4000)

    messages = [
        {
            "role": "system",
            "content": "You are a very unique, original, and creative author. You love sarcasm and wit. Your first task is to suggest a very creative and catchy title based on the provided text. The title should not exceed 80 characters. Your second task is to summarize the text in the style of The New Yorker, within a limit of 320 bytes."
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

    # Splitting the content into parts by '\n\n'
    parts = response['choices'][0]['message']['content'].split('\n\n')

    # Assigning the values to their respective keys
    title = parts[0] if len(parts) > 0 else None
    summary = parts[1] if len(parts) > 1 else None

    return title, summary