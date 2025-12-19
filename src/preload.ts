import { contextBridge, ipcRenderer } from 'electron';

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  // App state
  getAppState: () => ipcRenderer.invoke('get-app-state'),
  
  // Usage tracking
  updateUsage: (minutes: number) => ipcRenderer.invoke('update-usage', minutes),
  
  // License management
  validateLicense: (licenseKey: string) => ipcRenderer.invoke('validate-license', licenseKey),
  getLicense: () => ipcRenderer.invoke('get-license'),
  storeLicense: (license: any) => ipcRenderer.invoke('store-license', license),
  clearLicense: () => ipcRenderer.invoke('clear-license'),
  
  // File operations
  selectFile: () => ipcRenderer.invoke('select-file'),
  
  // Transcription
  startTranscription: (filePath: string) => ipcRenderer.invoke('start-transcription', filePath),
  cancelTranscription: () => ipcRenderer.invoke('cancel-transcription'),
  
  // Export
  exportTranscript: (data: { format: string; content: string; filename: string }) => 
    ipcRenderer.invoke('export-transcript', data),
  
  // External links
  openExternal: (url: string) => ipcRenderer.invoke('open-external', url),
  
  // Messages
  showMessage: (options: any) => ipcRenderer.invoke('show-message', options),
  
  // Event listeners
  onTranscriptionProgress: (callback: (progress: number) => void) => {
    ipcRenderer.on('transcription-progress', (event, progress) => callback(progress));
  },
  
  onTranscriptionComplete: (callback: (result: any) => void) => {
    ipcRenderer.on('transcription-complete', (event, result) => callback(result));
  },
  
  onShowSettings: (callback: () => void) => {
    ipcRenderer.on('show-settings', callback);
  },
  
  onNewTranscription: (callback: () => void) => {
    ipcRenderer.on('new-transcription', callback);
  },
  
  onFileSelected: (callback: (filePath: string) => void) => {
    ipcRenderer.on('file-selected', (event, filePath) => callback(filePath));
  },
  
  // Remove listeners
  removeAllListeners: (channel: string) => {
    ipcRenderer.removeAllListeners(channel);
  }
});