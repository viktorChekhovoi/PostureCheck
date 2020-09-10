from sys import stdout
from makeup_artist import Makeup_artist
import logging
from flask import Flask, render_template, Response
from flask_socketio import SocketIO
from camera import Camera
from utils import base64_to_pil_image, pil_image_to_base64
from flask_sqlalchemy import SQLAlchemy
from webpush_handler import trigger_push_notifications_for_subscriptions

app = Flask(__name__)
app.logger.addHandler(logging.StreamHandler(stdout))
app.config['SECRET_KEY'] = 'secret!'
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite://"
app.config.from_pyfile('application.cfg.py')
socketio = SocketIO(app)
camera = Camera(Makeup_artist())
db = SQLAlchemy(app)


class PushSubscription(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    subscription_json = db.Column(db.Text, nullable=False)

db.create_all()

@socketio.on('input image', namespace='/test')
def test_message(input):
    input = input.split(",")[1]
    camera.enqueue_input(input)
    #camera.enqueue_input(base64_to_pil_image(input))


@socketio.on('connect', namespace='/test')
def test_connect():
    app.logger.info("client connected")


@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')


def gen():
    """Video streaming generator function."""

    app.logger.info("starting to generate frames!")
    while True:
        frame = camera.get_frame() #pil_image_to_base64(camera.get_frame())
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

    
@app.route("/api/push-subscriptions", methods=["POST"])
def create_push_subscription():
    json_data = request.get_json()
    subscription = PushSubscription.query.filter_by(
        subscription_json=json_data['subscription_json']
    ).first()
    if subscription is None:
        subscription = PushSubscription(
            subscription_json=json_data['subscription_json']
        )
        db.session.add(subscription)
        db.session.commit()
    return jsonify({
        "status": "success",
        "result": {
            "id": subscription.id,
            "subscription_json": subscription.subscription_json
        }
    })


@app.route("/admin")
def admin_page():
    return render_template("admin.html")


@app.route("/admin-api/trigger-push-notifications", methods=["POST"])
def trigger_push_notifications():
    json_data = request.get_json()
    subscriptions = PushSubscription.query.all()
    results = trigger_push_notifications_for_subscriptions(
        subscriptions,
        json_data.get('title'),
        json_data.get('body')
    )
    return jsonify({
        "status": "success",
        "result": results
    })


if __name__ == '__main__':
    socketio.run(app)
