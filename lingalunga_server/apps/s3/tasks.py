import aioboto3


async def synthesize_speech_and_upload_to_s3(text, output_format="mp3", voice_id="Joanna", bucket_name="lingagunga", key_prefix=""):
    async with aioboto3.Session().client("polly") as polly:
        response = await polly.start_speech_synthesis_task(
            OutputFormat=output_format,
            Text=text,
            VoiceId=voice_id,
            OutputS3BucketName=bucket_name,
            OutputS3KeyPrefix=key_prefix,
        )

    task_id = response["SynthesisTask"]["TaskId"]
    output_uri = response["SynthesisTask"]["OutputUri"]
    return output_uri, task_id
