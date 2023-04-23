from nltk.tokenize import sent_tokenize
import httpx
import os
# from lingalunga_server.celery import app

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
    "temperature": 0.9,  # Adjust the temperature value to your preference
}


def data_image(prompt): return {
    "model": "image-alpha-001",
    "prompt": prompt,
    "num_images": 1,
    "size": "256x256",
}


def get_story_prompt(title, l1, level, theme, characters, length):
    prompt = f"""Please write me a story titled {title} in {l1} at the {level} level about the theme {theme} with the characters {characters}.
The story should be approximately {length} words long."""

    return prompt


def get_image_prompt(title, theme, characters):
    return f"An illustration representing the story {title} with the theme {theme} and the characters {characters}."


def get_title_prompt(lang, theme, characters):
    return f"Generate a creative title for a story with the theme {theme} and the characters {characters} in {lang}."


def get_translate_story_prompt(l1, l2, story_part):
    return f"Translate the following text from {l1} to {l2}:\n\n{story_part}"


async def send_request(data, url, headers):
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(url, headers=headers, json=data)
        response_json = response.json()

    return response_json


async def get_request(url, headers):
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.get(url, headers=headers)
        response_json = response.json()
    return response_json


async def generate_story_in_target_language_async(title, l1, level, theme, characters, length):
    story = ""
    previous_answers = None

    while len(story.split()) < length:
        prompt = get_story_prompt(title, l1, level, theme, characters, length)
        messages = [{"role": "user", "content": prompt}]

        if previous_answers:
            for _, answer in enumerate(previous_answers):
                messages.append({"role": "assistant", "content": answer})
                messages.append(
                    {"role": "user", "content": "please continue the story"})

        data = data_chat(messages)

        response_json = await send_request(data, complation_url, headers)
        new_story_part = response_json["choices"][0]["message"]["content"].strip(
        )

        if previous_answers is None:
            previous_answers = [new_story_part]
        else:
            previous_answers.append(new_story_part)

        story += " " + new_story_part

    return story.strip()


async def translate_story_part_async(l1, l2, story_part):
    prompt = get_translate_story_prompt(l1, l2, story_part)
    data = data_chat([{"role": "user", "content": prompt}])
    response_json = await send_request(data, complation_url, headers)
    return response_json["choices"][0]["message"]["content"].strip(
    )


async def call_openai(title, l1, l2, level, theme, characters, length):
    story = await generate_story_in_target_language_async(title,
                                                          l1, level, theme,
                                                          characters, length)

    story_parts = story.split('\n\n')

    translated_story_parts = []
    for part in story_parts:
        translation = await translate_story_part_async(l1, l2, part)
        translated_story_parts.append(translation)

    translated_story = '\n\n'.join(translated_story_parts)

    return story, translated_story


def split_text_into_sentences(text, language):
    sentences = sent_tokenize(text, language=language)
    sentences = [sentence.strip()
                 for sentence in sentences if sentence.strip()]

    return sentences


async def generate_image_url(title, theme, characters):
    prompt = get_image_prompt(title, theme, characters)
    data = data_image(prompt)
    response_json = await send_request(data, image_url, headers)
    get_image_url = response_json["data"][0]["url"]

    return get_image_url


async def generate_title(lang, theme, characters):
    prompt = get_title_prompt(lang, theme, characters)
    data = data_chat([{"role": "user", "content": prompt}])
    response_json = await send_request(data, complation_url, headers)
    title = response_json["choices"][0]["message"]["content"].strip()[1:-1]
    return title


async def generate_story(l1, l2, level, theme, characters, length, with_image):
    title = await generate_title(l1, theme, characters)
    get_image_url = None
    if with_image:
        get_image_url = await generate_image_url(title, theme, characters)

    story, translate_story = await call_openai(title, l1, l2, level, theme,
                                               characters, length)

    split_l1 = split_text_into_sentences(story, language=l1.lower())
    split_l2 = split_text_into_sentences(translate_story, language=l2.lower())

    result = list(zip(split_l1, split_l2))
    return title, result, get_image_url
