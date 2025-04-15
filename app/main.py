from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse, PlainTextResponse
from config import *
import uvicorn
import aiohttp
# from loguru import logger
from random import randint
from openai import Client
import redis.asyncio as redis
import asyncio
from chatgpt.app import *
import time
from btns import *
import json
from chatgpt.delay import *
from utils.utils import *
from loguru import logger
from send_email.services import *


# async def rate_limiter(request: Request, limit: int = 2, window: int = 10):
#     """
#     Ограничитель запросов: max `limit` запросов за `window` секундs
#     """
#     data = await request.json()
#     message = data.get("object", {}).get("message", {})
#     user_id = message.get("from_id")
#     if user_id:
#         key = f"rate-limit:{user_id}"
#         logger.info(key)

#         requests = await redis_client.get(key)

#         if requests is None:
#             logger.info("Создали ключ для запроса")
#             await redis_client.setex(key, window, 1)
#             return "ok"
#         else:
#             logger.info("Нашли ключ, и теперь смотрим, кол-во запросов")
#             requests_limit = int(requests)
#             logger.info(requests_limit)
#             if requests_limit >= limit:
#                 logger.info("Выкидываем ошибку - Слишком много запросов, попробуйте позже")
#                 return "too more query"
#             await redis_client.incr(key)
#     else:
#         return "too more query"

client_gpt = Client(api_key=settings.openai_api_key)
app = FastAPI()

async def send_vk_message_to_adm(user_id: str, btns):
    try:
        async with aiohttp.ClientSession() as session:
            url = settings.url_for_send_operator + str(user_id)
            logger.info(url)
            text = f"{url} - ВАМ ПРИШЛО УВЕДОМЛЕНИЕ, {url} - сыллка на диалог"
            params = {
                "user_id": settings.operator_id,
                "message": text,
                "access_token": settings.group_access_token,
                "v": "5.199",
                "random_id": randint(1, 1000000),
                "keyboard": btns
            }
            
            async with session.get(
                "https://api.vk.com/method/messages.send",
                params=params
            ) as response:
                result = await response.json()
                
                if "error" in result:
                    logger.error(f"VK API error: {result['error']}")
                return JSONResponse(result)
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        raise

async def send_vk_message_after_click_button(user_id: int, peer_id: int, event_id: str, btns: dict):
    try:
        async with aiohttp.ClientSession() as session:
            params = {
                "access_token": settings.group_access_token,
                "v": "5.199",
                "random_id": randint(1, 1000000),
                "event_id": event_id,
                "user_id": user_id,
                "peer_id": peer_id,
                "message": "💤Вы позвали оператора, в течении 15 минут ожидайте оператора, и он вам ответит.",
                "keyboard": json.dumps(btns)
            }
            
            async with session.get(
                "https://api.vk.com/method/messages.send",
                params=params
            ) as response:
                result = await response.json()
                
                if "error" in result:
                    logger.error(f"VK API error: {result['error']}")
                return JSONResponse(result)
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        raise

async def send_vk_forward_message(frwd_id: int):
    """Пересылаем сообщение от бота админа, через VK API"""
    try:
        async with aiohttp.ClientSession() as session:
            params = {
                "user_id": settings.operator_id,
                "message": "Вам пришло уведомление!",
                "access_token": settings.group_access_token,
                "v": "5.199",
                "random_id": randint(1, 1000000),
                "forward_messages": [frwd_id]
            }
            
            async with session.get(
                "https://api.vk.com/method/messages.send",
                params=params
            ) as response:
                result = await response.json(content_type=None)
                
                if "error" in result:
                    logger.error(f"VK API error: {result['error']}")
                return JSONResponse(result)
                
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        raise

async def send_vk_message(user_id: int, text: str, btns):
    """Отправка сообщения через VK API"""
    try:
        async with aiohttp.ClientSession() as session:
            params = {
                "user_id": user_id,
                "message": text,
                "access_token": settings.group_access_token,
                "v": "5.199",
                "random_id": randint(1, 1000000),
                "keyboard": btns
            }
            
            async with session.get(
                "https://api.vk.com/method/messages.send",
                params=params
            ) as response:
                result = await response.json(content_type=None)
                
                if "error" in result:
                    logger.error(f"VK API error: {result['error']}")
                return JSONResponse(result)
                
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        raise

async def send_vk_message_chat_gpt(user_id: int, text: str, btns):
    """Отправка сообщения через VK API"""
    try:
        data_dict = {"user_id": user_id, "message": text}
        resp_text = await get_chat_completion_cons(dict_data=data_dict)
        async with aiohttp.ClientSession() as session:
            text = decode_html(resp_text)
            logger.info(text)
            params = {
                "user_id": user_id,
                "message": text,
                "access_token": settings.group_access_token,
                "v": "5.199",
                "random_id": randint(1, 1000000),
                "keyboard": btns
            }
            
            async with session.get(
                "https://api.vk.com/method/messages.send",
                params=params,
            ) as response:
                result = await response.json()
                
                if "error" in result:
                    logger.error(f"VK API error: {result['error']}")
                return JSONResponse(result)
                
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        raise


@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}


@app.post("/callback/xE4sA")
async def read_root(request: Request):
    try:
        data = await request.json()
        logger.info(f"Received data: {data}")
        event_type = data.get("type")

        if event_type == "confirmation":
            return PlainTextResponse(content=settings.CONFIRMATION_TOKEN)

        if not data.get("group_id") == settings.GROUP_ID:
            raise HTTPException(status_code=403, detail="Invalid group_id")
            
        if not data["secret"] == settings.SECRET_KEY:
            raise HTTPException(status_code=403, detail="Invalid secret key")

        if event_type == "message_event":
            logger.info("ивент от копки")
            object = data.get("object", {})
            payload = object.get("payload", {})
            target_user_id = payload.get("target_user_id", None)
            if target_user_id is None:
                user_id_call = object.get("user_id")
                event_id = object.get("event_id")
                # conversation_message_id = object.get("conversation_message_id")
                peer_id = object.get("peer_id")
                    
                logger.info(f"New message from {user_id_call}")

                response = PlainTextResponse(content="ok")
                    
                asyncio.create_task(send_vk_message_after_click_button(user_id_call, peer_id, event_id, btns(user_id_call)))
                asyncio.create_task(send_vk_message_to_adm(user_id_call, get_kbs_adm(user_id_call)))
                asyncio.create_task(create_user_act(user_id_call))

                return response
            else:
                await delete_ogr_by_user(target_user_id)
                text = "Вы снова можете писать, задавайте вопросы, и наш консультант ответит!"
                asyncio.create_task(send_vk_message(target_user_id, text, btns=btns(target_user_id)))
                    
                response = PlainTextResponse(content="ok")

                return response

        if event_type == "message_new":
            message_obj = data.get("object", {}).get("message", {})
            text = message_obj.get("text")
            user_id = message_obj.get("from_id")
            if await check_user_act(user_id) is False:
                return PlainTextResponse(content="ok")
            if await check_user_delay(user_id):
                timestamp = message_obj.get("date")
                now = int(time.time())
                max_age = 45

                if now - timestamp > max_age:
                    logger.info(f"❌ Старое сообщение от {user_id} (игнорировано): {text}")
                    return JSONResponse({"status": "ok"})

                logger.info(f"New message from {user_id}: {text}")

                response = PlainTextResponse(content="ok")

                asyncio.create_task(send_vk_message_chat_gpt(user_id, text, btns(user_id)))

                return response

            else:
                text = "Не спамьте!"
                asyncio.create_task(send_vk_message(user_id, text, btns(user_id)))
                response = PlainTextResponse(content="ok")
                return response
            
        if event_type == "message_reply":
            message_obj = data.get("object", {})
            list_forward_messages = message_obj.get("fwd_messages", [])
            id_msg = message_obj.get("id", None)
            text = message_obj.get("text", None)
            if list_forward_messages:
                return PlainTextResponse(content="ok")
            if "\n" in text:
                text = text.split("\n")

            if "-ЗАЯВКА СОЗДАНА-" in text:
                full_text = message_obj.get("text", None)
                asyncio.create_task(send_vk_forward_message(id_msg))
                asyncio.create_task(send_email_with_appl_async(appls=full_text, email_to=settings.email_to))
                asyncio.create_task(send_email_with_appl_async(appls=text, email_to=settings.email_to_another))
                return PlainTextResponse(content="ok")
            return PlainTextResponse(content="ok")
                
        return PlainTextResponse(content="ok")
    
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Запуск сервера с командой:
# uvicorn main:app --reload
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=4242)