from config import *
import redis.asyncio as redis
from loguru import logger
import re
import html

redis_client = redis.Redis.from_url(settings.url_redis, encoding="utf-8", decode_responses=True)

def decode_html(text_html):
    return html.unescape(text_html)

async def get_thread_id(user_id, client) -> str:
    thread_id = await redis_client.get(f"user:{user_id}:thread_id")
    if thread_id:
        return thread_id

    thread = await client.beta.threads.create()
    await redis_client.setex(f"user:{user_id}:thread_id", 18000, thread.id)

    return thread.id

async def create_user_act(user_id: int):
    """Ограничиваем"""
    logger.info("ограничиваееееееем")
    await redis_client.setex(  
            f"users:vk:ogr:{user_id}", 10800, user_id, 
    )
    return True

async def check_user_act(user_id: int): 
    """Проверяем ограничение"""
    ogr_user = await redis_client.get(f"users:vk:ogr:{user_id}")  
    if ogr_user:  
        return False
    return True

async def delete_ogr_by_user(user_id):
    """Удаляем ограничение"""
    await redis_client.delete(f"users:vk:ogr:{user_id}")