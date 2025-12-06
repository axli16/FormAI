import React, { useState, useEffect, useRef } from 'react';
import { Video, VideoOff, Upload, Play, Pause, RotateCcw, Activity } from 'lucide-react';

// NOTE: You'll need to install @mediapipe/pose and @mediapipe/camera_utils
// Run: npm install @mediapipe/pose @mediapipe/camera_utils @mediapipe/drawing_utils

import { Pose } from '@mediapipe/pose';
import { Camera } from '@mediapipe/camera_utils';
import { drawConnectors, drawLandmarks } from '@mediapipe/drawing_utils';
import { POSE_CONNECTIONS } from '@mediapipe/pose';

// Header Component
const Header = () => {
    return (
        <header className="bg-black/20 backdrop-blur-sm border-b border-red-500/20 p-4">
            <div className="max-w-6xl mx-auto">
                <h1 className="text-2xl font-bold text-white text-center tracking-wide">
                    <span className="text-red-500">CALIS</span>THENIC TRACKER
                    <span className="text-xs ml-2 text-green-400">● STREAMING</span>
                </h1>
            </div>
        </header>
    );
};

// Skill Info Sidebar Component
const SkillInfoSidebar = ({ skillName, feedback, score, isStreaming }) => {
    return (
        <div className="bg-black/40 backdrop-blur-sm rounded-2xl border border-red-500/30 p-6 h-full">
            {/* Streaming Status */}
            <div className="mb-4">
                <div className={`flex items-center gap-2 px-3 py-2 rounded-lg ${isStreaming ? 'bg-green-500/20 border border-green-500/30' : 'bg-gray-500/20 border border-gray-500/30'}`}>
                    <Activity size={16} className={isStreaming ? 'text-green-400' : 'text-gray-400'} />
                    <span className={`text-sm font-medium ${isStreaming ? 'text-green-400' : 'text-gray-400'}`}>
                        {isStreaming ? 'Streaming to Kafka' : 'Not Streaming'}
                    </span>
                </div>
            </div>

            {/* Skill Name Section */}
            <div className="mb-8">
                <h2 className="text-lg font-semibold text-red-400 mb-3">Current Skill</h2>
                <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4">
                    <p className="text-white font-medium text-xl">
                        {skillName || "No skill selected"}
                    </p>
                </div>
            </div>

            {/* Score Section */}
            <div className="mb-8">
                <h3 className="text-lg font-semibold text-red-400 mb-3">Score</h3>
                <div className="bg-gray-800/50 border border-gray-600 rounded-lg p-4">
                    {score !== null && score !== undefined ? (
                        <div className="text-center">
                            <div className="text-3xl font-bold text-white mb-2">{score}</div>
                            <div className="w-full bg-gray-700 rounded-full h-2">
                                <div
                                    className="bg-gradient-to-r from-red-500 to-red-400 h-2 rounded-full transition-all duration-500"
                                    style={{ width: `${score}` }}
                                ></div>
                            </div>
                        </div>
                    ) : (
                        <p className="text-gray-400 text-center">No score available</p>
                    )}
                </div>
            </div>

            {/* Feedback Section */}
            <div>
                <h3 className="text-lg font-semibold text-red-400 mb-3">Feedback</h3>
                <div className="bg-gray-800/50 border border-gray-600 rounded-lg p-4 min-h-[200px]">
                    {feedback && feedback.length > 0 ? (
                        <div className="space-y-2">
                            {feedback.map((line, index) => (
                                <p key={index} className="text-gray-300 text-sm leading-relaxed">
                                    - {line}
                                </p>
                            ))}
                        </div>
                    ) : (
                        <p className="text-gray-400 text-sm">Waiting for AI feedback...</p>
                    )}
                </div>
            </div>
        </div>
    );
};

// Video Display Component with MediaPipe
const VideoDisplay = ({ videoRef, canvasRef, isStreaming, landmarkCount }) => {
    return (
        <div className="relative bg-black rounded-2xl shadow-2xl overflow-hidden border-2 border-red-500/30">
            {/* Hidden video element for MediaPipe */}
            <video
                ref={videoRef}
                className="absolute opacity-0"
                playsInline
            />

            {/* Canvas for drawing pose landmarks */}
            <canvas
                ref={canvasRef}
                className="w-full aspect-video object-cover bg-gray-800"
            />

            {/* Streaming Indicator */}
            {isStreaming && (
                <div className="absolute top-4 right-4 flex items-center gap-2 bg-green-500 text-white px-3 py-1 rounded-full text-sm font-medium">
                    <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div>
                    STREAMING
                </div>
            )}

            {/* Landmark Count */}
            {landmarkCount > 0 && (
                <div className="absolute top-4 left-4 bg-black/60 text-white px-3 py-1 rounded-lg text-xs font-medium">
                    {landmarkCount} landmarks detected
                </div>
            )}
        </div>
    );
};

// Control Buttons Component
const ControlButtons = ({
    isStreaming,
    onStreamToggle,
    selectedSkill,
    onSkillChange
}) => {
    const skills = ['Handstand', 'Front Lever', 'Planche', '90 Hold'];

    return (
        <footer className="bg-black/30 backdrop-blur-sm border-t border-red-500/20 p-6">
            <div className="max-w-6xl mx-auto">
                {/* Skill Selector */}
                <div className="flex justify-center mb-4">
                    <div className="flex gap-2">
                        {skills.map((skill) => (
                            <button
                                key={skill}
                                onClick={() => onSkillChange(skill)}
                                className={`px-4 py-2 rounded-lg font-medium transition-all ${selectedSkill === skill
                                        ? 'bg-red-500 text-white'
                                        : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                                    }`}
                            >
                                {skill}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Stream Control */}
                <div className="flex justify-center gap-6">
                    <button
                        onClick={onStreamToggle}
                        className={`flex items-center gap-3 px-8 py-4 rounded-xl font-semibold transition-all duration-200 transform hover:scale-105 shadow-lg ${isStreaming
                                ? 'bg-red-600 hover:bg-red-700 text-white shadow-red-500/30'
                                : 'bg-green-500 hover:bg-green-600 text-white shadow-green-500/30'
                            }`}
                    >
                        {isStreaming ? <VideoOff size={24} /> : <Video size={24} />}
                        {isStreaming ? 'Stop Streaming' : 'Start Streaming'}
                    </button>
                </div>
            </div>
        </footer>
    );
};

// Main App Component
export default function App() {
    const [isStreaming, setIsStreaming] = useState(false);
    const [selectedSkill, setSelectedSkill] = useState('Handstand');
    const [feedback, setFeedback] = useState({ skill: "", grade: "0", tips: [] });
    const [landmarkCount, setLandmarkCount] = useState(0);

    const videoRef = useRef(null);
    const canvasRef = useRef(null);
    const poseRef = useRef(null);
    const cameraRef = useRef(null);
    const lastStreamTime = useRef(0);

    // Initialize MediaPipe Pose
    useEffect(() => {
        const pose = new Pose({
            locateFile: (file) => {
                return `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${file}`;
            }
        });

        pose.setOptions({
            modelComplexity: 1,
            smoothLandmarks: true,
            enableSegmentation: false,
            smoothSegmentation: false,
            minDetectionConfidence: 0.5,
            minTrackingConfidence: 0.5
        });

        pose.onResults(onPoseResults);
        poseRef.current = pose;

        // Initialize camera
        if (videoRef.current) {
            const camera = new Camera(videoRef.current, {
                onFrame: async () => {
                    if (poseRef.current && videoRef.current) {
                        await poseRef.current.send({ image: videoRef.current });
                    }
                },
                width: 1280,
                height: 720
            });
            cameraRef.current = camera;
            camera.start();
        }

        return () => {
            if (cameraRef.current) {
                cameraRef.current.stop();
            }
        };
    }, []);

    // Handle pose detection results
    const onPoseResults = (results) => {
        if (!canvasRef.current) return;

        const canvasCtx = canvasRef.current.getContext('2d');
        const canvas = canvasRef.current;

        // Set canvas size
        canvas.width = results.image.width;
        canvas.height = results.image.height;

        // Draw the image
        canvasCtx.save();
        canvasCtx.clearRect(0, 0, canvas.width, canvas.height);
        canvasCtx.drawImage(results.image, 0, 0, canvas.width, canvas.height);

        // Draw pose landmarks
        if (results.poseLandmarks) {
            setLandmarkCount(results.poseLandmarks.length);

            // Draw connections
            drawConnectors(canvasCtx, results.poseLandmarks, POSE_CONNECTIONS, {
                color: '#00FF00',
                lineWidth: 4
            });

            // Draw landmarks
            drawLandmarks(canvasCtx, results.poseLandmarks, {
                color: '#FF0000',
                lineWidth: 2,
                radius: 6
            });

            // Stream to Kafka if enabled
            if (isStreaming) {
                streamLandmarksToKafka(results.poseLandmarks);
            }
        } else {
            setLandmarkCount(0);
        }

        canvasCtx.restore();
    };

    // Stream landmarks to Flask/Kafka (throttled to ~5 FPS)
    const streamLandmarksToKafka = (landmarks) => {
        const now = Date.now();
        const THROTTLE_MS = 200; // 5 FPS

        if (now - lastStreamTime.current < THROTTLE_MS) {
            return; // Skip this frame
        }

        lastStreamTime.current = now;

        // Convert MediaPipe landmarks to our format
        const landmarkData = convertLandmarks(landmarks);

        // Send to Flask backend
        fetch('http://localhost:5000/stream-pose', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_id: 'user_1', // You can make this dynamic
                timestamp: now,
                exercise: selectedSkill.toLowerCase().replace(' ', '_'),
                landmarks: landmarkData
            })
        })
            .then(res => res.json())
            .then(data => {
                console.log('Streamed to Kafka:', data);
            })
            .catch(err => {
                console.error('Streaming error:', err);
            });
    };

    // Convert MediaPipe landmarks to simplified format
    const convertLandmarks = (landmarks) => {
        const landmarkNames = {
            0: 'nose',
            11: 'left_shoulder',
            12: 'right_shoulder',
            13: 'left_elbow',
            14: 'right_elbow',
            15: 'left_wrist',
            16: 'right_wrist',
            23: 'left_hip',
            24: 'right_hip',
            25: 'left_knee',
            26: 'right_knee',
            27: 'left_ankle',
            28: 'right_ankle'
        };

        return Object.entries(landmarkNames).map(([idx, name]) => {
            const landmark = landmarks[parseInt(idx)];
            return {
                part: name,
                x: parseFloat(landmark.x.toFixed(4)),
                y: parseFloat(landmark.y.toFixed(4)),
                z: parseFloat(landmark.z.toFixed(4)),
                visibility: parseFloat(landmark.visibility.toFixed(4))
            };
        });
    };

    const handleStreamToggle = () => {
        setIsStreaming(!isStreaming);
    };

    const handleSkillChange = (skill) => {
        setSelectedSkill(skill);
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-900 via-red-900 to-black flex flex-col">
            <Header />
            <main className="flex-1 p-4">
                <div className="max-w-7xl mx-auto h-full">
                    <div className="flex gap-4 h-full">
                        {/* Left Side - Video Display (80% width) */}
                        <div className="flex-1 lg:w-4/5 flex flex-col justify-center">
                            <VideoDisplay
                                videoRef={videoRef}
                                canvasRef={canvasRef}
                                isStreaming={isStreaming}
                                landmarkCount={landmarkCount}
                            />

                            <div className="text-center mt-4">
                                <p className="text-white/80 text-sm">
                                    {isStreaming ? 'Streaming pose data to Confluent Cloud' : 'Ready to stream'}
                                </p>
                            </div>

                            {/* Mobile Skill Info */}
                            <div className="block lg:hidden mt-6">
                                <SkillInfoSidebar
                                    skillName={selectedSkill}
                                    feedback={feedback.tips}
                                    score={feedback.grade}
                                    isStreaming={isStreaming}
                                />
                            </div>
                        </div>

                        {/* Right Sidebar - Skill Info (20% width) */}
                        <div className="w-1/5 min-w-[280px] hidden lg:block">
                            <SkillInfoSidebar
                                skillName={selectedSkill}
                                feedback={feedback.tips}
                                score={feedback.grade}
                                isStreaming={isStreaming}
                            />
                        </div>
                    </div>
                </div>
            </main>

            <ControlButtons
                isStreaming={isStreaming}
                onStreamToggle={handleStreamToggle}
                selectedSkill={selectedSkill}
                onSkillChange={handleSkillChange}
            />
        </div>
    );
}
