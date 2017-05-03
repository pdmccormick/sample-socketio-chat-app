#
# Sample chat app using socket.io, Flask, flask-socketio and gevent
#
# (c) Peter McCormick. MIT licensed.
#

import logging
from datetime import datetime

import gevent
from gevent.lock import Semaphore
from flask import Flask, Response, request, jsonify
from flask_socketio import SocketIO, emit

log = logging.getLogger('chatapp')

INDEX_HTML = r'''
<!doctype html>
<html lang='en'>
    <head>
        <meta charset='utf-8'>
        <meta http-equiv='X-UA-Compatible' content='IE=edge'>
        <meta name='viewport' content='width=device-width, initial-scale=1'>
        <title>Chat App</title>
        <link rel='stylesheet' href='https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css' integrity='sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u' crossorigin='anonymous'>
        <script src='https://cdnjs.cloudflare.com/ajax/libs/socket.io/1.7.3/socket.io.min.js' integrity='sha256-WKvqiY0jZHWQZIohYEmr9KUC5rEaYEOFTq+ByllJK8w=' crossorigin='anonymous'></script>
        <script src='https://cdnjs.cloudflare.com/ajax/libs/jquery/3.2.1/jquery.min.js' integrity='sha256-hwg4gsxgFZhOsEEamdOYGBf13FyQuiTwlAQgxVSNgt4=' crossorigin='anonymous'></script>
        <script>
$(function() {
    var socket = io('/ws/chat');

    socket.on('connect', function() {
        console.log('CONNECTED', socket.id);
    });

    socket.on('messages', function(data) {
        for (var i = 0; i < data.length; i++) {
            var msg = data[i];
            var snippet = $('<div><pre>' + msg[0] + ' <strong>@' + msg[1] + '</strong> ' + msg[2] + '</pre></div>');
            snippet.hide();
            $('#messages').prepend(snippet);
            snippet.slideDown();
        }
    });

    $('#chatForm').on('submit', function(ev) {
        ev.preventDefault();

        var msg = $('#chatMessage');
        var txt = msg.val();
        msg.val('');

        socket.emit('message', txt);
    });

    $('#chatMessage').focus();
});
        </script>
        <style>
html {
    position: relative;
    min-height: 100%;
}

body {
    /* Margin bottom by footer height */
    margin-bottom: 60px;
}

.footer {
    position: absolute;
    bottom: 0;
    width: 100%;
    /* Set the fixed height of the footer here */
    height: 60px;
    background-color: #f5f5f5;
}

.container {
    width: auto;
    max-width: 680px;
    padding: 0 15px;
}

.container .text-muted {
    margin: 20px 0;
}
        </style>
    </head>
    <body>
        <div class='container'>
            <div class='page-header'>
                <h1><a href='https://github.com/pdmccormick/sample-socketio-chat-app' target='_blank'>Let's chat!</a></h1>
            </div>
            <p>Built using
            <a href='https://socket.io/' target='_blank'>socket.io</a>,
            <a href='http://flask.pocoo.org/' target='_blank'>Flask</a>,
            <a href='https://flask-socketio.readthedocs.io/en/latest/' target='_blank'>flask-socketio</a>,
            <a href='http://www.gevent.org/' target='_blank'>gevent</a>,
            <a href='https://getbootstrap.com/' target='_blank'>Bootstrap</a> and <a href='https://jquery.com/' target='_blank'>jQuery</a>.
            </p>
            <p>
                <form id='chatForm' class='form-inline'>
                    <div class='form-group'>
                        <input type='text' class='form-control' id='chatMessage' placeholder='Speak your mind!' autocomplete='off'>
                    </div>
                    <button class='btn btn-primary' id='chatSend'>Send</button>
                </form>
            </p>
            <div id='messages'>
            </div>
            <p><small><a href='/recent' target='_blank'>&raquo; Recent messages as JSON</a></small></p>
        </div>

        <footer class='footer'>
            <div class='container'>
                <p class='text-muted'>&copy; <a href='https://github.com/pdmccormick'>Peter McCormick</a>. MIT licensed.</p>
            </div>
        </footer>
    </body>
</html>
'''.strip()

class ChatApp(SocketIO):
    NAMESPACE = '/ws/chat'
    MAX_RECENT = 10

    def __init__(self):
        flask = self.flask = Flask('ChatApp')

        super().__init__(self.flask)

        self.lock = Semaphore()
        self.recent_messages = []
        self.clients = {}
        self.next_user_id = 0

        @flask.route('/')
        def index():
            return Response(INDEX_HTML, mimetype='text/html')

        @flask.route('/recent')
        def recent_messages():
            with self.lock:
                recent = list(self.recent_messages)

            return jsonify(recent)

        @self.on('connect', namespace=self.NAMESPACE)
        def on_connect():
            log.info('client connect %s', request.sid)

            with self.lock:
                user_id = self.next_user_id
                self.clients[request.sid] = user_id
                self.next_user_id += 1

                recent = list(self.recent_messages)

            if len(recent) > 0:
                emit('messages', recent, namespace=self.NAMESPACE)

            self.send_message('has joined the chat')

        @self.on('disconnect', namespace=self.NAMESPACE)
        def on_disconnect():
            self.send_message('has left the room')

            with self.lock:
                self.clients.pop(request.sid, None)

            log.info('client disconnect %s', request.sid)

        @self.on('message', namespace=self.NAMESPACE)
        def on_message(msg):
            self.send_message(msg)

    def send_message(self, msg):
        with self.lock:
            user_id = self.clients.get(request.sid)

            data = ( datetime.now().strftime('%H:%M:%S'), 'user{}'.format(user_id), msg )

            self.recent_messages.append(data)

            if len(self.recent_messages) > self.MAX_RECENT:
                self.recent_messages = self.recent_messages[-self.MAX_RECENT:]

        self.emit('messages', [ data ], namespace=self.NAMESPACE)

    def run(self, *args, **kwargs):
        super().run(self.flask)

if __name__ == '__main__':
    logging.basicConfig()
    log.setLevel(logging.INFO)
    app = ChatApp()
    app.run()
