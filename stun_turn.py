import os

from twilio.rest import Client

from dotenv import load_dotenv

load_dotenv()


# Find your Account SID and Auth Token at twilio.com/console

# and set the environment variables. See http://twil.io/secure

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")

client = Client(account_sid, auth_token)


token = client.tokens.create()


print(token.ice_servers)

# Example output:
[{'url': 'stun:global.stun.twilio.com:3478', 'urls': 'stun:global.stun.twilio.com:3478'},
 {'credential': 'eccGMyyVUVTw/YsS/G//3WA7ysWzg7G4Jqnjndamf1c=', 'url': 'turn:global.turn.twilio.com:3478?transport=udp', 'urls': 'turn:global.turn.twilio.com:3478?transport=udp', 'username': 'fecf7f37917475768b25c30c7861ae6c0736c380538749f34db1c55c592a3ab8'},
 {'credential': 'eccGMyyVUVTw/YsS/G//3WA7ysWzg7G4Jqnjndamf1c=', 'url': 'turn:global.turn.twilio.com:3478?transport=tcp', 'urls': 'turn:global.turn.twilio.com:3478?transport=tcp', 'username': 'fecf7f37917475768b25c30c7861ae6c0736c380538749f34db1c55c592a3ab8'},
 {'credential': 'eccGMyyVUVTw/YsS/G//3WA7ysWzg7G4Jqnjndamf1c=', 'url': 'turn:global.turn.twilio.com:443?transport=tcp', 'urls': 'turn:global.turn.twilio.com:443?transport=tcp', 'username': 'fecf7f37917475768b25c30c7861ae6c0736c380538749f34db1c55c592a3ab8'}]