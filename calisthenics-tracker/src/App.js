import React, { useState, useEffect } from 'react';
import { Video, VideoOff, Upload, Play, Pause, RotateCcw } from 'lucide-react';

// Header Component
const Header = () => {
  return (
    <header className="bg-black/20 backdrop-blur-sm border-b border-red-500/20 p-4">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-2xl font-bold text-white text-center tracking-wide">
          <span className="text-red-500">CALIS</span>THENIC TRACKER
        </h1>
      </div>
    </header>
  );
};

// Skill Info Sidebar Component
const SkillInfoSidebar = ({ skillName, feedback, score }) => {
  return (
    <div className="bg-black/40 backdrop-blur-sm rounded-2xl border border-red-500/30 p-6 h-full">
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
          {feedback ? (
            <div className="space-y-2">
              {feedback.map((line, index) => (
                <p key={index} className="text-gray-300 text-sm leading-relaxed">
                  {line}
                </p>
              ))}
            </div>
          ) : (
            <p className="text-gray-400 text-sm">No feedback available</p>
          )}
        </div>
      </div>
    </div>
  );
};

// Video Display Component
const VideoDisplay = ({ src, isRecording, hasRecordedVideo, isPlaying, onPlayToggle }) => {
  return (
    <div className="relative bg-black rounded-2xl shadow-2xl overflow-hidden border-2 border-red-500/30">
      <img
        src={src}
        alt="Live Feed"
        className="w-full aspect-video object-cover bg-gray-800"
      />

      {/* Recording Indicator */}
      {isRecording && (
        <div className="absolute top-4 right-4 flex items-center gap-2 bg-red-500 text-white px-3 py-1 rounded-full text-sm font-medium">
          <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div>
          REC
        </div>
      )}

      {/* Live Indicator */}
      {!hasRecordedVideo && !isRecording && (
        <div className="absolute top-4 right-4 flex items-center gap-2 bg-green-500 text-white px-3 py-1 rounded-full text-sm font-medium">
          <div className="w-2 h-2 bg-white rounded-full"></div>
          LIVE
        </div>
      )}

      {/* Video Controls Overlay */}
      {hasRecordedVideo && (
        <div className="absolute inset-0 bg-black/20 flex items-center justify-center opacity-0 hover:opacity-100 transition-opacity duration-300">
          <button
            onClick={onPlayToggle}
            className="bg-red-500 hover:bg-red-600 text-white p-4 rounded-full shadow-lg transition-all duration-200 transform hover:scale-110"
          >
            {isPlaying ? <Pause size={32} /> : <Play size={32} />}
          </button>
        </div>
      )}
    </div>
  );
};

// Status Text Component
const StatusText = ({ hasRecordedVideo, isRecording }) => {
  const getStatusText = () => {
    if (hasRecordedVideo) return 'Recorded Video';
    if (isRecording) return 'Recording in progress...';
    return 'Live Camera Feed';
  };

  return (
    <div className="text-center mt-4">
      <p className="text-white/80 text-sm">{getStatusText()}</p>
    </div>
  );
};

// Control Buttons Component with Skill Selector
const ControlButtons = ({
  isRecording,
  hasRecordedVideo,
  onRecordToggle,
  onUpload,
  onReset,
  selectedSkill,
  onSkillChange
}) => {
  const skills = [
    { value: 'handstand', label: 'Handstand' },
    { value: 'front_lever', label: 'Front Lever' },
    { value: 'planche', label: 'Planche' },
    { value: '90_hold', label: '90 Hold' },
    { value: 'vertical_jump', label: 'Vertical Jump' }
  ];

  return (
    <footer className="bg-black/30 backdrop-blur-sm border-t border-red-500/20 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Skill Selector */}
        <div className="flex justify-center mb-6">
          <div className="w-full max-w-md">
            <label className="block text-white text-sm font-semibold mb-2 text-center">
              Select Exercise
            </label>
            <select
              value={selectedSkill}
              onChange={(e) => onSkillChange(e.target.value)}
              className="w-full px-6 py-4 bg-gray-800 text-white rounded-xl border-2 border-red-500/30 focus:border-red-500 focus:outline-none font-semibold text-lg cursor-pointer hover:bg-gray-700 transition-all"
            >
              {skills.map((skill) => (
                <option key={skill.value} value={skill.value}>
                  {skill.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex justify-center gap-6">
          {/* Reset Button */}
          {hasRecordedVideo && (
            <button
              onClick={onReset}
              className="flex items-center gap-3 px-6 py-4 bg-gray-700 hover:bg-gray-600 text-white rounded-xl font-semibold transition-all duration-200 transform hover:scale-105"
            >
              <RotateCcw size={20} />
              Back to Live
            </button>
          )}
        </div>
      </div>
    </footer>
  );
};

// Main App Component
export default function App() {
  // UI State
  const [isRecording, setIsRecording] = useState(false);
  const [hasRecordedVideo, setHasRecordedVideo] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [selectedSkill, setSelectedSkill] = useState('handstand');

  // Skill info state
  const [feedback, setFeedback] = useState({ skill: selectedSkill, grade: "80", tips: [] });

  // Send selected skill to backend whenever it changes
  useEffect(() => {
    fetch("http://localhost:5000/set-skill", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ skill: selectedSkill })
    }).catch(err => console.error("Failed to set skill:", err));
  }, [selectedSkill]);

  // Poll for feedback
  useEffect(() => {
    const interval = setInterval(() => {
      fetch("http://localhost:5000/feedback")
        .then(res => res.json())
        .then(data => setFeedback(data));
    }, 500);

    return () => clearInterval(interval);
  }, []);

  // Handler functions
  const handleRecordToggle = () => {
    setIsRecording(!isRecording);
  };

  const handleUpload = () => {
    console.log('Upload clicked');
  };

  const handlePlayToggle = () => {
    setIsPlaying(!isPlaying);
  };

  const handleReset = () => {
    setHasRecordedVideo(false);
    setIsPlaying(false);
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
                src='http://127.0.0.1:5000/video_feed'
                isRecording={isRecording}
                hasRecordedVideo={hasRecordedVideo}
                isPlaying={isPlaying}
                onPlayToggle={handlePlayToggle}
              />

              <StatusText
                hasRecordedVideo={hasRecordedVideo}
                isRecording={isRecording}
              />

              {/* Mobile Skill Info - Shows below video on small screens */}
              <div className="block lg:hidden mt-6">
                <SkillInfoSidebar
                  skillName={feedback.skill}
                  feedback={feedback.tips}
                  score={feedback.grade}
                />
              </div>
            </div>

            {/* Right Sidebar - Skill Info (20% width) */}
            <div className="w-1/5 min-w-[280px] hidden lg:block">
              <SkillInfoSidebar
                skillName={feedback.skill}
                feedback={feedback.tips}
                score={feedback.grade}
              />
            </div>
          </div>
        </div>
      </main>

      <ControlButtons
        isRecording={isRecording}
        hasRecordedVideo={hasRecordedVideo}
        onRecordToggle={handleRecordToggle}
        onUpload={handleUpload}
        onReset={handleReset}
        selectedSkill={selectedSkill}
        onSkillChange={handleSkillChange}
      />
    </div>
  );
}