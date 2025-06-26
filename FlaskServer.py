from flask import Flask, Response, jsonify
import os
from flask_cors import CORS
import VideoFeed


app = Flask(__name__)
CORS(app)
feed = VideoFeed.VideoCamera()
feedback = {"skill": "", "grade": "", "tips":[]}

def generate_frames():
    while True:
        frame = feed.get_frame()
        if frame is None:
            continue 
        # update_feedback()
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
    
    print(feedback)
    feedback["skill"] = skill_name
    feedback["grade"] = accuracy
    feedback["tips"] = tips

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)