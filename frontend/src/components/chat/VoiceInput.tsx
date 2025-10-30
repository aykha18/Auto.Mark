import React, { useEffect, useRef, useState } from 'react';
import { VoiceRecognitionState } from '../../types';

interface VoiceInputProps {
  voiceState: VoiceRecognitionState;
  onVoiceStateChange: (state: VoiceRecognitionState) => void;
  onTranscript: (transcript: string) => void;
}

const VoiceInput: React.FC<VoiceInputProps> = ({
  voiceState,
  onVoiceStateChange,
  onTranscript
}) => {
  const recognitionRef = useRef<any>(null);
  const [interimTranscript, setInterimTranscript] = useState('');

  useEffect(() => {
    if (!voiceState.isSupported) return;

    // Initialize speech recognition
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    recognitionRef.current = new SpeechRecognition();
    
    const recognition = recognitionRef.current;
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    recognition.onstart = () => {
      onVoiceStateChange({
        ...voiceState,
        isListening: true,
        transcript: '',
        confidence: 0
      });
      setInterimTranscript('');
    };

    recognition.onresult = (event: any) => {
      let finalTranscript = '';
      let interim = '';

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;
        const confidence = event.results[i][0].confidence;

        if (event.results[i].isFinal) {
          finalTranscript += transcript;
          onVoiceStateChange({
            ...voiceState,
            transcript: finalTranscript,
            confidence: confidence || 0,
            isListening: false
          });
        } else {
          interim += transcript;
        }
      }

      setInterimTranscript(interim);
    };

    recognition.onend = () => {
      onVoiceStateChange({
        ...voiceState,
        isListening: false
      });
      
      // Send final transcript if available
      if (voiceState.transcript.trim()) {
        onTranscript(voiceState.transcript);
      }
    };

    recognition.onerror = (event: any) => {
      console.error('Speech recognition error:', event.error);
      onVoiceStateChange({
        ...voiceState,
        isListening: false
      });
      setInterimTranscript('');
    };

    return () => {
      if (recognition) {
        recognition.stop();
      }
    };
  }, []);

  const startListening = () => {
    if (recognitionRef.current && !voiceState.isListening) {
      recognitionRef.current.start();
    }
  };

  const stopListening = () => {
    if (recognitionRef.current && voiceState.isListening) {
      recognitionRef.current.stop();
    }
  };

  if (!voiceState.isSupported) {
    return null;
  }

  return (
    <div className="flex items-center space-x-2">
      <button
        onClick={voiceState.isListening ? stopListening : startListening}
        className={`p-2 rounded-full transition-all duration-200 ${
          voiceState.isListening
            ? 'bg-red-100 text-red-600 animate-pulse'
            : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
        }`}
        aria-label={voiceState.isListening ? 'Stop voice input' : 'Start voice input'}
        title={voiceState.isListening ? 'Click to stop recording' : 'Click to start voice input'}
      >
        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z" clipRule="evenodd" />
        </svg>
      </button>

      {(voiceState.isListening || interimTranscript) && (
        <div className="flex-1 min-w-0">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-2">
            <div className="flex items-center space-x-2">
              {voiceState.isListening && (
                <div className="flex space-x-1">
                  <div className="w-1 h-4 bg-blue-500 rounded-full animate-pulse"></div>
                  <div className="w-1 h-4 bg-blue-500 rounded-full animate-pulse" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-1 h-4 bg-blue-500 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
                </div>
              )}
              <div className="flex-1 min-w-0">
                <p className="text-sm text-blue-800 truncate">
                  {voiceState.isListening ? (
                    interimTranscript || 'Listening...'
                  ) : (
                    voiceState.transcript || 'Voice input ready'
                  )}
                </p>
                {voiceState.confidence > 0 && (
                  <p className="text-xs text-blue-600">
                    Confidence: {Math.round(voiceState.confidence * 100)}%
                  </p>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default VoiceInput;