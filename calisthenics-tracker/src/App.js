import React, { useState, useEffect, useRef } from 'react';
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
                  - {line}
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
      {/* {hasRecordedVideo && (
        <div className="absolute inset-0 bg-black/20 flex items-center justify-center opacity-0 hover:opacity-100 transition-opacity duration-300">
          <button
            onClick={onPlayToggle}
            className="bg-red-500 hover:bg-red-600 text-white p-4 rounded-full shadow-lg transition-all duration-200 transform hover:scale-110"
          >
            {isPlaying ? <Pause size={32} /> : <Play size={32} />}
          </button>
        </div>
      )} */}
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

// Control Buttons Component
const ControlButtons = ({ 
  isRecording, 
  hasRecordedVideo, 
  onRecordToggle, 
  onUpload, 
  onReset,
  handleClick,
  inputRef
}) => {
  return (
    <footer className="bg-black/30 backdrop-blur-sm border-t border-red-500/20 p-6">
      <div className="max-w-6xl mx-auto flex justify-center gap-6">
        {/* Record Button */}
        {/* <button
          onClick={onRecordToggle}
          disabled={hasRecordedVideo}
          className={`flex items-center gap-3 px-8 py-4 rounded-xl font-semibold transition-all duration-200 transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed ${
            isRecording 
              ? 'bg-red-600 hover:bg-red-700 text-white shadow-lg shadow-red-500/30' 
              : 'bg-red-500 hover:bg-red-600 text-white shadow-lg shadow-red-500/30'
          }`}
        >
          {isRecording ? <VideoOff size={24} /> : <Video size={24} />}
          {isRecording ? 'Stop Recording' : 'Start Recording'}
        </button> */}

        {/* Upload Button */}
        <button
          onClick={handleClick}
          className="flex items-center gap-3 px-8 py-4 bg-white hover:bg-gray-100 text-gray-900 rounded-xl font-semibold transition-all duration-200 transform hover:scale-105 shadow-lg"
        >
          <Upload size={24} />
          Upload Video
        </button>
        <input
          type="file"
          accept="video/*"
          ref={inputRef}
          onChange={onUpload}
          style={{ display: 'none' }}
        />

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
    </footer>
  );
};

// Main App Component
export default function App() {
  // UI State (you can manage this with your backend integration)
  const [isRecording, setIsRecording] = useState(false);
  const [hasRecordedVideo, setHasRecordedVideo] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [videoKey, setVideoKey] = useState(Date.now());
  const [skill, setSkill] = useState("Handstand");

  // Skill info state - connect these to your backend
  const [feedback, setFeedback] = useState({ skill: "", grade: "0", tips: [] });

  useEffect(() => {
    handleReset();
  }, []); 

  // useEffect(() => {
  //   const interval = setInterval(() => {
  //     fetch("http://localhost:5000/feedback")
  //       .then(res => res.json())
  //       .then(data => setFeedback(data));
  //   }, 500); // every 0.5s

  //   return () => clearInterval(interval);
  // }, []);

  // Handler functions - connect these to your backend
  const handleRecordToggle = () => {
    setIsRecording(!isRecording);
    // TODO: Integrate with your backend recording logic
  };


  const inputRef = useRef(null);

  const handleClick = () => {
    inputRef.current.click();
  }
  const handleUpload = async (e) => {
    // TODO: Integrate with your backend upload logic
    console.log('Upload clicked');
    const file = e.target.files[0];
    if (!file) {
      console.log("No file selected")
      return;
    }

    const formData = new FormData(); 
    formData.append('video', e.target.files[0]);
    formData.append('skill', skill);

    await fetch("http://localhost:5000/upload", {
      method: "POST",
      body: formData
    })
      .then(res => res.text())
      .then(msg => {
        console.log("Upload success:", msg);
        setHasRecordedVideo(true);
      })
      .catch(err => console.error("Upload failed:", err));
  };

  const handlePlayToggle = () => {
    setIsPlaying(!isPlaying);
    // TODO: Integrate with your backend playback logic
  };

  const handleReset = async () => {
    setHasRecordedVideo(false);
    setIsPlaying(false);
    await fetch("http://localhost:5000/reset", {
      method: "POST",
    })
      .then(res => res.text())
      .then(msg => {
        console.log("Reset success:", msg);
        setVideoKey(Date.now());
      })
      .catch(err => console.error("Reset failed:", err));
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
                src = {`http://localhost:5000/video_feed?${videoKey}`}
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
        handleClick={handleClick}
        inputRef={inputRef}
      />
    </div>
  );
}