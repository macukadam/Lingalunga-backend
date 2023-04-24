import aioboto3
import aiohttp
import mimetypes

AWS_DEFAULT_REGION = os.getenv("AWS_DEFAULT_REGION", "eu-central-1")


async def synthesize_speech_and_upload_to_s3(text, output_format="mp3",
                                             bucket_name="lingagunga",
                                             key_prefix="audio/",
                                             voice_id="Joanna",
                                             engine="neural"):
    async with aioboto3.Session().client("polly", region_name=AWS_DEFAULT_REGION) as polly:
        response = await polly.start_speech_synthesis_task(
            OutputFormat=output_format,
            Text=text,
            VoiceId=voice_id,
            Engine=engine,
            OutputS3BucketName=bucket_name,
            OutputS3KeyPrefix=key_prefix,
        )

    task_id = 'audio/.' + response["SynthesisTask"]["TaskId"] + '.mp3'
    output_uri = response["SynthesisTask"]["OutputUri"]
    return output_uri, task_id


async def upload_image_to_s3(image_url, name, bucket_name="lingagunga", key_prefix="images/"):
    async with aiohttp.ClientSession() as session:
        async with session.get(image_url) as resp:
            if resp.status != 200:
                return None
            extention = mimetypes.guess_extension(resp.content_type)

            image = await resp.read()
            async with aioboto3.Session().client("s3", region_name=AWS_DEFAULT_REGION) as s3:
                response = await s3.put_object(Body=image, Bucket=bucket_name,
                                               Key=key_prefix + name
                                               + extention)
            print(response)
            return response
