from celery import shared_task
from nltk.tokenize import sent_tokenize
import httpx
import asyncio
import os

api_key = os.getenv("OPENAI_API_KEY")


def generate_prompt(l1, level, theme, characters, length):
    prompt = f"""Please write me a story in {l1} at the {level} level about the theme '{theme}' with the characters {characters}.
The story should be approximately {length} words long."""

    return prompt


async def generate_story_in_target_language_async(l1, level, theme, characters, length):
    story = ""
    previous_answers = None

    while len(story.split()) < length:
        prompt = generate_prompt(l1, level, theme, characters, length)
        messages = [{"role": "user", "content": prompt}]

        if previous_answers:
            for _, answer in enumerate(previous_answers):
                messages.append({"role": "assistant", "content": answer})
                messages.append(
                    {"role": "user", "content": "please continue the story"})

        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }

        data = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.8,  # Adjust the temperature value to your preference
        }

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(url, headers=headers, json=data)
            response_json = response.json()

        print(response_json)
        new_story_part = response_json["choices"][0]["message"]["content"].strip(
        )

        if previous_answers is None:
            previous_answers = [new_story_part]
        else:
            previous_answers.append(new_story_part)

        story += " " + new_story_part

    return story.strip()


async def translate_story_part_async(l1, l2, story_part):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    prompt = f"Translate the following text from {l1} to {l2}:\n\n{story_part}"
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.8,  # Adjust the temperature value to your preference
    }

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(url, headers=headers, json=data)
        response_json = response.json()

    print(response_json)
    translated_story_part = response_json["choices"][0]["message"]["content"].strip(
    )

    return translated_story_part


async def call_openai(l1, l2, level, theme, characters, length):
    story = await generate_story_in_target_language_async(
        l1, level, theme, characters, length)

    # Split the story into smaller parts (e.g., paragraphs or sections)
    story_parts = story.split('\n\n')

    # Translate each part of the story
    translated_story_parts = []
    for part in story_parts:
        translation = await translate_story_part_async(l1, l2, part)
        translated_story_parts.append(translation)

    # Combine the translated story parts
    translated_story = '\n\n'.join(translated_story_parts)

    return story, translated_story


def split_text_into_sentences(text, language="english"):
    # Tokenize the text into sentences
    sentences = sent_tokenize(text, language=language)

    # Remove any empty lines
    sentences = [sentence.strip()
                 for sentence in sentences if sentence.strip()]

    return sentences


@shared_task
def generate_story():
    l1 = "French"
    l2 = "English"
    level = "B2"
    theme = "mystery"
    characters = "Carol and Bob"
    length = 100
    story, translate_story = asyncio.run(call_openai(
        l1, l2, level, theme, characters, length))

    split_french = split_text_into_sentences(story, language="french")
    split_english = split_text_into_sentences(
        translate_story, language="english")

    # zip the sentences together
    result = list(zip(split_french, split_english))
    print(result)
    return result
