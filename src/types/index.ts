export interface AppState {
  currentTier: 'free' | 'unlimited' | 'student';
  usage: UsageStats;
  license: License | null;
  currentTranscript: TranscriptionResult | null;
  isTranscribing: boolean;
  transcriptionProgress: number;
}

export interface UsageStats {
  minutesUsed: number;
  lastResetDate: string;
  nextResetDate: string;
}

export interface License {
  key: string;
  tier: 'unlimited' | 'student';
  status: 'active' | 'expired' | 'invalid';
  isStudent?: boolean;
  expiryDate?: string;
}

export interface TranscriptionSegment {
  timestamp: string;
  speaker: string;
  text: string;
  startTime: number;
  endTime: number;
}

export interface TranscriptionResult {
  segments: TranscriptionSegment[];
  totalDuration: number;
  speakers: number;
}
