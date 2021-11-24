#!/usr/bin/env python

import connexion
Nothing = connexion.NoContent

def play():
    return Nothing, 200

def pause():
    return Nothing, 200

def stop():
    return Nothing, 200

def skip():
    return Nothing, 200

def status():
    return Nothing, 200

app = connexion.App('sonicad')
print('Loading spec')
app.add_api('../sonica.yml')
print('Starting server')
app.run(port = 8080)
