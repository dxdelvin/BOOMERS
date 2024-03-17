from flask import Flask, request, jsonify, render_template, Response
from twilio.rest import Client
import cv2
from flask import Flask
from pyngrok import ngrok
import requests
import time

# Set your Ngrok authentication token
ngrok.set_auth_token("2dEU3eIpJUK8n05fQGdsr0AZsT4_2AsWNMcuYM4nGSBLmp6pX")


app = Flask(__name__)

# Twilio credentials

account_sid = 'ACb0fadebfe86f9c859ef7d9f33734a43f'
auth_token = 'd284a433d1bcb10317e3fcfef96e3816'
client = Client(account_sid, auth_token)




camera = cv2.VideoCapture(0)

def gen_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video')
def cam():
    return render_template('cam.html')

@app.route('/no')
def no():
    return render_template('no.html')

@app.route('/yes')
def yes():
    return render_template('yes.html')


@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/home')
def index():
    
    return render_template('index.html')

@app.route('/send_sms', methods=['POST'])
def send_sms():
    data = request.get_json()
    message = data.get('message')
    to_number = data.get('to_number')

    if not message or not to_number:
        return jsonify({'success': False, 'error': 'Message or to_number is missing'}), 400

    try:
        # Send SMS
        client.messages.create(
            body=message,
            from_='+14157277405',  # Your Twilio phone number for SMS
            to=to_number
        )
        return jsonify({'success': True, 'message': 'SMS sent successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/send_whatsapp', methods=['POST'])
def send_whatsapp():
    message = request.form.get('message')
    to_number = request.form.get('to_number')

    if not message or not to_number:
        return jsonify({'success': False, 'error': 'Message or to_number is missing'}), 400

    try:
        # Send SMS
        sms_data = {'message': message, 'to_number': to_number}
        sms_response = requests.post('http://127.0.0.1:5000/send_sms', json=sms_data)  # Adjust URL accordingly

        # Check if the SMS was sent successfully
        if sms_response.status_code == 200:
            # Send WhatsApp message
            client.messages.create(
                body=message,
                from_='whatsapp:+14155238886',  # Your Twilio WhatsApp number
                to='whatsapp:' + to_number
            )
            
            # return jsonify({'success': True, 'message': 'WhatsApp message sent successfully'})
            return render_template('sos.html')
        else:
            return jsonify({'success': False, 'error': 'Failed to send SMS'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    

# Set up the ngrok tunnel with a different port, for example, 8080
new_port = 5000
public_url = ngrok.connect(new_port)

print(" * ngrok tunnel \"{}\" -> \"http://127.0.0.1:{}/\" ".format(public_url, new_port))

# dummy_data = ["1234567890", "0987654321", "1357924680"]

# @app.route('/login', methods=['POST'])
# def login():
#     rsiv_code = request.form['code']
#     if rsiv_code in dummy_data:
#         return render_template('yes.html')
#     else:
#         return render_template('no.html')


if __name__ == "__main__":
    app.run(debug=False)


