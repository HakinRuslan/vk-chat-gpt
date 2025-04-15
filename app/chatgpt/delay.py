from config import *
from utils.utils import *
import asyncio


async def check_user_delay(user_id: int):  
    last_message_time = await redis_client.get(f"users_vk:{user_id}")  
    if last_message_time:  
        time_since_last_message = asyncio.get_event_loop().time() - float(  
            last_message_time  
        )
    else:
        await redis_client.setex(  
            f"users_vk:{user_id}", 8, asyncio.get_event_loop().time(), 
        )
        return True
    if time_since_last_message <  4:  
        return False
    return True