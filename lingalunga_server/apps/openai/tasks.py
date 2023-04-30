import httpx
import os
# from lingalunga_server.celery import app

TIMEOUT = 240

api_key = os.getenv("OPENAI_API_KEY")

complation_url = "https://api.openai.com/v1/chat/completions"
image_url = "https://api.openai.com/v1/images/generations"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}",
}


def data_chat(messages): return {
    "model": "gpt-3.5-turbo",
    "messages": messages,
    "temperature": 0.8,  # Adjust the temperature value to your preference
}


def data_image(prompt): return {
    "model": "image-alpha-001",
    "prompt": prompt,
    "num_images": 1,
    "size": "256x256",
}


def get_image_prompt(title, theme, characters):
    return f"An illustration representing the story {title} with the theme {theme} and the characters {characters}."


async def send_request(data, url, headers):
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await client.post(url, headers=headers, json=data)
        response_json = response.json()

    return response_json


async def get_request(url, headers):
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await client.get(url, headers=headers)
        response_json = response.json()
    return response_json


async def generate_image_url(title, theme, characters):
    prompt = get_image_prompt(title, theme, characters)
    data = data_image(prompt)
    response_json = await send_request(data, image_url, headers)
    get_image_url = response_json["data"][0]["url"]

    return get_image_url


def get_story_prompt_both_languages(l1, l2, level, theme, characters, length):
    level_text = 'intermediate'
    if level == "a1":
        level_text = "beginner"
    elif level == "a2":
        level_text = "elementary"
    elif level == "b1":
        level_text = "intermediate"
    elif level == "b2":
        level_text = "upper intermediate"
    elif level == "c1":
        level_text = "advanced"

    prompt = f"""Format:
title in {l1}
title in {l2}
{l1} sentence
{l2} sentence
...
{l1} sentence
{l2} sentence

Write a {level_text} level {length} sentences long story in {l1} and {l2} with the theme {theme} and the characters {characters}.
Each sentence has to be in a new line.
"""
    return prompt


async def generate_story_in_both_languages_async(l1, l2, level, theme, characters, length):
    prompt = get_story_prompt_both_languages(
        l1, l2, level, theme, characters, length)
    messages = [{"role": "user", "content": prompt}]

    data = data_chat(messages)

    response_json = await send_request(data, complation_url, headers)
    story = response_json["choices"][0]["message"]["content"].strip()
    story_splited = story.replace("\n\n", "\n")

    return story_splited.split('\n'), story


async def generate_story(l1, l2, level, theme, characters, length, with_image):
    story_splited, story = await generate_story_in_both_languages_async(l1, l2, level, theme, characters, length)

    result = [(story_splited[i], story_splited[i + 1])
              for i in range(0, len(story_splited) - 1, 2)]
    title = result.pop(0)

    image_url = None
    if with_image:
        image_url = await generate_image_url(title[0], theme, characters)
    return title, image_url, result, story
