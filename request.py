import json
import requests
import random
from flask import Flask, request, make_response, jsonify
from responses import PRECIO_PARTE, INFO_PARTE, PART_TECH
from config import (LOGON_ID, LOGON_PASSWORD, PARTNER_ID, PARTNER_KEY)

app = Flask(__name__)
log = app.logger

auth = None


@app.route('/', methods=['POST', 'GET'])
def webhook():
    """This method handles the http requests for the Dialogflow webhook
    """
    req = request.get_json(silent=True, force=True)
    try:
        action = req.get('queryResult').get('action')
    except AttributeError:
        return 'json error'

    parameters = req['queryResult']['parameters']

    part_number = parameters['any']
    part_tech = parameters['any']

    if part_tech != "":

        if action == 'part_tech':
            res = get_part_tech(part_tech)
        elif action == 'precio_parte':
            res = get_part_price(part_number)
        else:
            log.error('Unexpected action.')

    else:
        res = {"fulfillmentText": 'Favor de especificar el número de parte'}

    
    print('Action: ' + action)
    print(res)

    return make_response(jsonify(res))


def get_part_price(part_number):
    response = part_request(part_number)

    if response is None:
        text = "El numero de parte es incorrecto"
    else:

        precio = response['PriceINMXN']
        nombre = response['shortDescription']

        output_string = random.choice(PRECIO_PARTE)

        text = output_string.format(nombre=nombre, precio=precio)

    res = {"fulfillmentText": text,
            "fulfillmentMessages": [
            {
                "text": {
                  "text": [text]
                },
                "platform": "FACEBOOK"
              },
            {
                "text": {
                  "text": [text]
                },
                "platform": "SLACK"
              },
            {"text": {
                    "text": [text]
                    }
            }
      ]
      }

    return res



# Test function for part tech test


def get_part_tech(part_tech):
    response = part_tech_request(part_tech)
    print(response)
    print(part_tech + 'Esto es una prueba')

    if response is None:
        text = "El numero de parte es incorrecto"
    else:

        parttech = response['partName']

        output_string = random.choice(PART_TECH)

        text = output_string.format(partName=parttech)

    res = {"fulfillmentText": text,
            "fulfillmentMessages": [


            {
                "text": {
                  "text": [text]
                },
                "platform": "FACEBOOK"
              },
              {
                "text": {
                  "text": [text]
                },
                "platform": "SLACK"
              },
            {"text": {
                    "text": [text]
                    }
            }
      ]
      }

    return res

# PartTech Request


def part_tech_request(part_tech):
    global auth
    if auth is None:
        auth = authenticate()

    url = "https://api.beta.partstech.com/catalog/search"
    payload = auth
    headers = {
        'Content-Type': "application/json",
        'cache-control': "no-cache"
        }

    response = requests.request("POST", url, json=payload, headers=headers)

    auth = None
    if response.status_code == 200 or response.status_code == 201:
        return response.json()
    else:
        return None


def part_request(part_number):
    global auth
    if auth is None:
        auth = authenticate()

    url = "https://api.beta.partstech.com/catalog/parts/{}".format(part_number)
    payload = auth
    headers = {
        'Content-Type': "application/json",
        'cache-control': "no-cache"
        }

    response = requests.request("POST", url, json=payload, headers=headers)

    auth = None
    if response.status_code == 200 or response.status_code == 201:
        return response.json()
    else:
        return None


def authenticate():

    url = "https://api.beta.partstech.com/oauth/access"
    payload = {
  "accessType": "user",
  "credentials": {
    "user": {
      "id": LOGON_ID,
      "key": LOGON_PASSWORD
    },
    "partner": {
      "id": PARTNER_ID,
      "key": PARTNER_KEY
    }
  }
}


    headers = {
        'Content-Type': "application/json",
        'cache-control': "no-cache"
        }

    response = requests.request("POST", url, json=payload, headers=headers)

    print(response.status_code)
    print(response.content)

    if response.status_code == 200 or response.status_code == 201:
        return response.json()
    else:
        print("FALTAN CREDENCIALES")


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
