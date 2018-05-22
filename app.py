
from flask import Flask, request
import requests

# create a Flask app instance
app = Flask(__name__)
app.config.from_object('settings')

# method to reply to a message from the sender
def reply(data):
    # Post request using the Facebook Graph API v2.6
    resp = requests.post("https://graph.facebook.com/v2.6/me/messages?access_token=" +
                         app.config["ACCESS_TOKEN"], json=data)
    print(resp.content)


def welcome_message(fn):
    return {
        "text": "Hi " + fn + ", welcome to MyFood.\n\nLet's start ordering by click button below.",
        "quick_replies": [
            {
                "content_type": "text",
                "title": "Show Commands",
                "payload": "help",
            }
        ]
    }


def show_menu():
    return {
        "attachment": {
            "type": "template",
            "payload": {
                    "template_type": "list",
                    "top_element_style": "compact",
                    "elements": [
                        {
                            "title": "Donut (Code: 001)",
                            "subtitle": "RM1 / Set (3 Pieces)",
                            "image_url": app.config["IMG_DONUT"],
                            "buttons": [
                                {
                                    "type": "postback",
                                    "title": "Buy Donut",
                                    "payload": "buy 001",
                                }
                            ]
                        },
                        {
                            "title": "Chicken (Code: 002)",
                            "subtitle": "RM3 / Piece \n",
                            "image_url": app.config["IMG_CHICKEN"],
                            "buttons": [
                                {
                                    "title": "Buy Chicken",
                                    "type": "postback",
                                    "payload": "buy 002",
                                }
                            ]
                        }
                    ]
            }
        }
    }


def receipt():
    return {
        # "text": "my receipt",
        "attachment": {
            "type": "template",
            "payload": {
                "template_type": "receipt",
                "recipient_name": "Fadzil Jusri",
                "order_number": "<ORDER_NUMBER>",
                "currency": "MYR",
                "payment_method": "Visa 1234",
                "order_url": "https://fadzil.win",
                "timestamp": 1428444852,
                "address": {
                    "street_1": "<SHIPPING_STREET_ADDRESS>",
                    "city": "<SHIPPING_CITY>",
                    "postal_code": "<SHIPPING_POSTAL_CODE>",
                    "state": "<SHIPPING_STATE>",
                    "country": "<SHIPPING_COUNTRY>"
                },
                "summary": {
                    "subtotal": 7,
                    "shipping_cost": 0,
                    "total_tax": 0,
                    "total_cost": 7
                },
                "elements": [
                    {
                        "title": "Donut",
                        "subtitle": "Code: 001",
                        "quantity": 1,
                        "price": 1,
                        "currency": "MYR",
                        "image_url": app.config["IMG_DONUT"]
                    },
                    {
                        "title": "Chicken",
                        "subtitle": "Code: 002",
                        "quantity": 2,
                        "price": 6,
                        "currency": "MYR",
                        "image_url": app.config["IMG_CHICKEN"]
                    },
                ]
            }
        }
    }


def user_need_help():
    return {
        "attachment": {
            "type": "template",
            "payload": {
                    "template_type": "button",
                    "text": "What can I do to help?",
                    "buttons": [
                        {
                            "type": "postback",
                            "title": "Show Menu",
                            "payload": "menu",
                        },
                        {
                            "type": "phone_number",
                            "title": "Call Me",
                            "payload": "+60106505576",
                        }
                    ]
            }
        }
    }


def help():
    return {
        "text": "menu \n* show our list of available foods\n\n" +
        "buy [food_code] \n* ordering our food\n\n" +
        "help \n* show list of commands"
    }


# GET request to handle the verification of tokens
@app.route('/', methods=['GET'])
def handle_verification():
    if request.args['hub.verify_token'] == app.config['VERIFY_TOKEN']:
        return request.args['hub.challenge']
    else:
        return "Invalid verification token"

# POST request to handle in coming messages then call reply()
@app.route('/', methods=['POST'])
def handle_incoming_messages():
    data = request.json
    # print(data)
    sender = data['entry'][0]['messaging'][0]['sender']['id']
    reply_data = {"recipient": {"id": sender}}

    try:
        msg = data['entry'][0]['messaging'][0]['message']['text']
    except KeyError:
        try:
            msg = data['entry'][0]['messaging'][0]['postback']['payload']
        except KeyError:
            # location received
            reply_data["message"] = {"text": "Location received."}
            reply(reply_data)

            msg = "receipt"

    # determine what to do when user send message
    if (msg.lower().find("hi") >= 0) or (msg.lower().find("hello") >= 0):
        resp = requests.get("https://graph.facebook.com/v2.6/" + sender + "/?access_token=" +
                            app.config["ACCESS_TOKEN"] + "&fields=first_name")
        sender_dtls = resp.json()
        reply_data["message"] = welcome_message(sender_dtls["first_name"])

    elif (msg.lower().find("menu") >= 0):
        reply_data["message"] = show_menu()

    elif (msg.lower().find("buy") >= 0):
        reply_data["message"] = {
            "text": "Your order has been received. To continue please send your location.",
            "quick_replies": [
                {
                    "content_type": "location"
                }
            ]
        }

    elif (msg.lower().find("receipt") >= 0):
        reply_data["message"] = receipt()

    elif (msg.lower().find("help") >= 0) or msg == "Show Commands":
        reply_data["message"] = help()

    else:
        reply_data["message"] = user_need_help()

    # print(reply_data)
    reply(reply_data)

    return "ok"


if __name__ == '__main__':
    app.run(debug="true")
