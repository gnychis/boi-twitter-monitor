from twython import Twython
import requests
import zmq

APP_KEY = '6LTEgHCBchKPIQdXb3IH6kJSI'
APP_SECRET = 'waHGTlmTVKQmsm485tf5WPWpUShQkTecvdvwKOBB7DA8nQlnSB'

twitter = Twython(APP_KEY, APP_SECRET)

auth = twitter.get_authentication_tokens()

OAUTH_TOKEN = auth['oauth_token']
OAUTH_TOKEN_SECRET = auth['oauth_token_secret']

twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

print(auth['auth_url'])
pin = input("Give your pin: ").strip()
print(pin)
final_tokens = twitter.get_authorized_tokens(pin)

f_oauth_token = final_tokens['oauth_token']
f_oauth_token_secret = final_tokens['oauth_token_secret']

print(f_oauth_token)
print(f_oauth_token_secret)

twitter = Twython(APP_KEY, APP_SECRET, f_oauth_token, f_oauth_token_secret)

#print(r.text)
#print(r.json()['oauth_verifier'])
#print(OAUTH_TOKEN)
#print(OAUTH_TOKEN_SECRET)

twitter.verify_credentials()

user_timeline = twitter.get_home_timeline()

for tweet in user_timeline:
    print(tweet['text'])

#auth = twitter.get_authentication_tokens()
#
#context = zmq.Context()
#socket = context.socket(zmq.REQ)
#port = "5555"
#socket.connect ("tcp://localhost:%s" % port)
#
#for i in range (1,10):
#    socket.send ("saying hello from python")
#    message = socket.recv()
#    print("Received reply from server:", message)
