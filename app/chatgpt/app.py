from openai import AsyncOpenAI  
import asyncio
from config import * 
import time
import httpx
from utils.utils import *
from loguru import logger

async def get_thread_id(user_id, client) -> str:
    thread_id = await redis_client.get(f"user:{user_id}:thread_id")
    if thread_id:
        return thread_id

    thread = await client.beta.threads.create()
    await redis_client.setex(f"user:{user_id}:thread_id", 18000, thread.id)

    return thread.id

async def get_gpt_client():
    http_client = httpx.AsyncClient(  
    limits=httpx.Limits(max_connections=150, max_keepalive_connections=20)  
    )  
    client = AsyncOpenAI(  
        api_key=settings.openai_api_key,  
        http_client=http_client,  
        base_url="https://api.openai.com/v1",  
        
    )
    return client

async def get_chat_completion_cons(dict_data: dict):
    client = await get_gpt_client()
    thread_id = await get_thread_id(dict_data["user_id"], client)

    await client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=dict_data["message"]
    )
    run = await client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id="ur ass id"
    )

    while True:
        run = await client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
        if run.status == "completed":
            break

    messages = client.beta.threads.messages.list(thread_id=thread_id)
    async for message in messages:
        if message.role == "assistant":
            return message.content[0].text.value