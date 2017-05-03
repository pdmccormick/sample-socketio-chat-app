Sample chat app using [socket.io](https://socket.io/)
=================================

## What is this?

A toy chat application written in Python demonstrating the use of WebSockets
via socket.io and Flask.


## Getting started

1. Setup a Python 3 venv with the requirements:

    ```shell
    $ python3 -m venv env-chatapp
    $ ln -s env-chatapp/bin/activate .
    $ source activate
    $ pip install -r requirements.pip
    ```

2. Run the chat server:

    ```shell
    $ python chatapp.py
    ```

3. Open <http://localhost:5000/> twice and start chatting!


## Links

 * [socket.io](https://socket.io/)
 * [Flask](http://flask.pocoo.org/)
 * [flask-socketio](https://flask-socketio.readthedocs.io/en/latest/) 
 * [gevent](http://www.gevent.org/)
 * [GitHub repository](https://github.com/pdmccormick/sample-socketio-chat-app)


## Afterword

Thanks to Waterluvian for the inspiration to put this together.

Peter McCormick - Toronto, May 2017
