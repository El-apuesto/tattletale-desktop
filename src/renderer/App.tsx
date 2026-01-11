import React, { useState, useRef, useEffect } from 'react';

interface AppState {
  currentTier: 'free' | 'unlimited' | 'student';
  usage: {
    minutesUsed: number;
    nextResetDate: string;
  };
  license: any;
}

const App: React.FC = () => {
  const [files, setFiles] = useState<File[]>([]);
  const [appState, setAppState] = useState<AppState | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [showUpgradeModal, setShowUpgradeModal] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    // Load app state
    if (window.electron) {
      window.electron.getAppState().then(setAppState);
    }
  }, []);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const droppedFiles = Array.from(e.dataTransfer.files);
    setFiles(droppedFiles);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleFileSelect = async () => {
    if (window.electron) {
      const filePath = await window.electron.selectFile();
      if (filePath) {
        // Add selected file to list
        console.log('Selected file:', filePath);
      }
    }
  };

  const startRecording = async () => {
    // Check if user has access to recording feature
    if (appState?.currentTier === 'free') {
      setShowUpgradeModal(true);
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data);
        }
      };

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
        const file = new File([blob], `recording-${Date.now()}.webm`, { type: 'audio/webm' });
        setFiles([file]);
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
      setRecordingTime(0);

      // Start timer
      timerRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);
    } catch (error) {
      console.error('Failed to start recording:', error);
      alert('Could not access microphone. Please check your permissions.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const closeUpgradeModal = () => {
    setShowUpgradeModal(false);
  };

  return (
    <div className="app">
      <h1>Tattletale Desktop</h1>
      <p>Privacy-first transcription app using Whisper AI</p>
      
      {/* Recording Controls */}
      <div className="recording-controls">
        {!isRecording ? (
          <button className="record-btn" onClick={startRecording}>
            🎤 Start Recording
            {appState?.currentTier === 'free' && ' (Premium)'}
          </button>
        ) : (
          <div className="recording-active">
            <button className="stop-btn" onClick={stopRecording}>
              ⏹ Stop Recording
            </button>
            <div className="recording-timer">
              <span className="recording-dot"></span>
              {formatTime(recordingTime)}
            </div>
          </div>
        )}
      </div>

      <div className="divider">OR</div>
      
      {/* File Drop Zone */}
      <div 
        className="drop-zone"
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onClick={handleFileSelect}
      >
        <p>Drop audio files here or click to browse</p>
        {files.length > 0 && (
          <div>
            <h3>Files:</h3>
            <ul>
              {files.map((file, idx) => (
                <li key={idx}>{file.name}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Upgrade Modal */}
      {showUpgradeModal && (
        <div className="modal-overlay" onClick={closeUpgradeModal}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>🔒 Premium Feature</h2>
            <p>Audio recording is available for Unlimited and Student tiers.</p>
            <div className="modal-actions">
              <button className="btn-primary" onClick={closeUpgradeModal}>
                Upgrade Now
              </button>
              <button className="btn-secondary" onClick={closeUpgradeModal}>
                Maybe Later
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default App;
