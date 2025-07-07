from flask import Flask, Response, jsonify, request
import os
from flask_cors import CORS
import tempfile

import VideoFeed



app = Flask(__name__)
CORS(app)

feed = VideoFeed.VideoCamera()
feedback = {"skill": "", "grade": "", "tips":[]}
streaming = True

def generate_frames():
    while True:
        
        frame = feed.get_frame()
        if frame is None:
            continue 

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/feedback')        
def getfeedback():
    update_feedback()
    return jsonify({
        "skill": str(feedback["skill"]) or "Detecting...",
        "grade": str(feedback["grade"]) or "Pending",
        "tips": list(feedback["tips"]) or "Looking"
    })

def update_feedback():
    global feedback
    skill_detected = feed.detect_skill()
    skill_feedback = feed.feed_back(skill_detected)
    accuracy = skill_feedback[-2] 
    skill_name = skill_feedback[-1]

    tips = []
    for i in range(0, len(skill_feedback) - 2):
        tips.append(skill_feedback[i])
    
    feedback["skill"] = skill_name
    feedback["grade"] = accuracy
    feedback["tips"] = tips

@app.route('/upload', methods=['POST'])
def upload_video():
    global video_file 

    if 'video' not in request.files:
        return "Np video file", 400
    
    file = request.files['video']
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    file.save(tmp_file.name)

    video_file = tmp_file.name

    feed.switch_video_source(video_file)
    streaming = False
    return "Upload successful", 200

@app.route('/reset', methods=['POST'])
def reset_live():
    streaming = True
    feed.switch_video_source(0)
    return "Live Feed Reset", 200

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)