from flask import Flask, Response, jsonify, request
import os
from flask_cors import CORS
from werkzeug.utils import secure_filename
from urllib.parse import urlparse
import boto3
import uuid

import VideoFeed

BUCKET = 'calivideo'
s3 = boto3.client('s3')

app = Flask(__name__)
CORS(app)

feed = VideoFeed.VideoCamera()
feedback = {"skill": "", "grade": "", "tips":[]}

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

    if 'video' not in request.files:
        return "Np video file", 400

    skill = request.form['skill']
    file = request.files['video']

    filename = secure_filename(file.filename)

    local_path = os.path.join('uploads', filename)
    file.save(local_path)
    s3_key = f"processed/{uuid.uuid4()}_{filename}"

    s3.upload_file(local_path, BUCKET, s3_key)


    feed.switch_video_source(local_path)
    feed.process(skill)

    print(feed.feed_back(skill))
    
    return jsonify({"url": s3_key})


@app.route('/reset', methods=['POST'])
def reset():
    # url = request.form['url']
    # parsed = urlparse(url)
    # key = parsed.path.lstrip('/') 

    # feed.delete(key)
    os.remove("./uploads")
    return jsonify({"Reset":"Success"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)