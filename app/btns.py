import json
def btns(user_id: int):
  btns = {
    "one_time": False,
    "buttons":[
      [
        {
          "action":{
            "type":"text",
            "payload":"{\"button\": \"1\"}",
            "label":"💰 Рассчитать стоимость"
          },
          "color":"negative"
        },
        {
          "action":{
            "type":"text",
            "payload":"{\"button\": \"2\"}",
            "label":"🚚 Доставка и забор"
          },
          "color":"positive"
        },
        {
          "action":{
            "type":"text",
            "payload":"{\"button\": \"2\"}",
            "label":"🔥 Акции и скидки"
          },
          "color":"primary"
        },
        {
          "action":{
            "type":"callback",
            "payload": json.dumps({"button": "2", "user_id": user_id}),
            "label":"Позвать оператора"
          },
          "color":"secondary"
        }
      ]
    ]
  }
  return json.dumps(btns)


def get_kbs_adm(user_id: int):
  btns_adm = {
    "inline": True,
    "buttons":[
      [
        {
          "action":{
            "type":"callback",
            "payload": json.dumps({"button": "end", "target_user_id": user_id}),
            "label":"Завершить разговор"
          },
          "color":"secondary"
        }
      ]
    ]
  }
  return json.dumps(btns_adm)