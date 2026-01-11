import { app, BrowserWindow, ipcMain, dialog, shell, Menu } from 'electron';
import path from 'path';
import { spawn } from 'child_process';
import Store from 'electron-store';
import { AppState, UsageStats, License, TranscriptionResult } from './types';
import os from 'os';
import { promises as fs } from 'fs';

// Electron Forge webpack entry point
declare const MAIN_WINDOW_WEBPACK_ENTRY: string;
declare const MAIN_WINDOW_PRELOAD_WEBPACK_ENTRY: string;

// Handle Squirrel.Windows installer events
if (process.platform === 'win32') {
  const squirrelCommand = process.argv[1];
  if (squirrelCommand === '--squirrel-install' || squirrelCommand === '--squirrel-updated') {
    app.quit();
  } else if (squirrelCommand === '--squirrel-uninstall') {
    app.quit();
  } else if (squirrelCommand === '--squirrel-obsolete') {
    app.quit();
  }
}

class TattletaleApp {
  private mainWindow: BrowserWindow | null = null;
  private store: Store;
  private transcriptionProcess: any = null;

  constructor() {
    this.store = new Store();
    this.initializeApp();
  }

  private async initializeApp() {
    await app.whenReady();
    
    this.createMenu();
    await this.createMainWindow();
    this.setupIpcHandlers();
    this.setupAppEvents();
  }

  private async createMainWindow() {
    this.mainWindow = new BrowserWindow({
      width: 1200,
      height: 800,
      minWidth: 1000,
      minHeight: 600,
      webPreferences: {
        nodeIntegration: false,
        contextIsolation: true,
        preload: MAIN_WINDOW_PRELOAD_WEBPACK_ENTRY,
      },
      icon: path.join(__dirname, '../assets/icon.png'),
      show: false,
      titleBarStyle: process.platform === 'darwin' ? 'hiddenInset' : 'default',
    });

    this.mainWindow.loadURL(MAIN_WINDOW_WEBPACK_ENTRY);
    
    if (process.env.NODE_ENV === 'development') {
      this.mainWindow.webContents.openDevTools();
    }

    this.mainWindow.once('ready-to-show', () => {
      this.mainWindow?.show();
    });

    this.mainWindow.on('closed', () => {
      this.mainWindow = null;
    });
  }

  private createMenu() {
    const template = [
      {
        label: 'Tattletale',
        submenu: [
          {
            label: 'About Tattletale',
            click: () => {
              this.showAboutDialog();
            }
          },
          { type: 'separator' },
          {
            label: 'Settings',
            accelerator: 'CmdOrCtrl+,',
            click: () => {
              this.mainWindow?.webContents.send('show-settings');
            }
          },
          { type: 'separator' },
          {
            role: 'hide'
          },
          {
            role: 'hideothers'
          },
          {
            role: 'unhide'
          },
          { type: 'separator' },
          {
            role: 'quit'
          }
        ]
      },
      {
        label: 'File',
        submenu: [
          {
            label: 'New Transcription',
            accelerator: 'CmdOrCtrl+N',
            click: () => {
              this.mainWindow?.webContents.send('new-transcription');
            }
          },
          {
            label: 'Open File...',
            accelerator: 'CmdOrCtrl+O',
            click: async () => {
              const result = await dialog.showOpenDialog(this.mainWindow!, {
                properties: ['openFile'],
                filters: [
                  {
                    name: 'Audio/Video Files',
                    extensions: ['mp3', 'mp4', 'wav', 'm4a', 'mov', 'webm']
                  }
                ]
              });
              if (!result.canceled && result.filePaths.length > 0) {
                this.mainWindow?.webContents.send('file-selected', result.filePaths[0]);
              }
            }
          },
          { type: 'separator' },
          {
            role: 'close'
          }
        ]
      },
      {
        label: 'Edit',
        submenu: [
          { role: 'undo' },
          { role: 'redo' },
          { type: 'separator' },
          { role: 'cut' },
          { role: 'copy' },
          { role: 'paste' },
          { role: 'selectall' }
        ]
      },
      {
        label: 'View',
        submenu: [
          { role: 'reload' },
          { role: 'forceReload' },
          { role: 'toggleDevTools' },
          { type: 'separator' },
          { role: 'resetZoom' },
          { role: 'zoomIn' },
          { role: 'zoomOut' },
          { type: 'separator' },
          { role: 'togglefullscreen' }
        ]
      },
      {
        label: 'Window',
        submenu: [
          { role: 'minimize' },
          { role: 'close' }
        ]
      },
      {
        label: 'Help',
        submenu: [
          {
            label: 'Learn More',
            click: () => {
              shell.openExternal('https://tattletale.app');
            }
          }
        ]
      }
    ];

    const menu = Menu.buildFromTemplate(template as any);
    Menu.setApplicationMenu(menu);
  }

  private showAboutDialog() {
    dialog.showMessageBox(this.mainWindow!, {
      type: 'info',
      title: 'About Tattletale',
      message: 'Tattletale',
      detail: 'Privacy-first desktop transcription app using Whisper AI\n\nVersion 1.0.0',
      buttons: ['OK']
    });
  }

  private setupIpcHandlers() {
    ipcMain.handle('get-app-state', () => {
      return this.getAppState();
    });

    ipcMain.handle('update-usage', (event, minutes: number) => {
      return this.updateUsage(minutes);
    });

    ipcMain.handle('validate-license', async (event, licenseKey: string) => {
      return this.validateLicense(licenseKey);
    });

    ipcMain.handle('get-license', () => {
      return this.store.get('license') as License | null;
    });

    ipcMain.handle('store-license', (event, license: License) => {
      this.store.set('license', license);
      return true;
    });

    ipcMain.handle('clear-license', () => {
      this.store.delete('license');
      return true;
    });

    ipcMain.handle('select-file', async () => {
      const result = await dialog.showOpenDialog(this.mainWindow!, {
        properties: ['openFile'],
        filters: [
          {
            name: 'Audio/Video Files',
            extensions: ['mp3', 'mp4', 'wav', 'm4a', 'mov', 'webm']
          }
        ]
      });
      
      if (!result.canceled && result.filePaths.length > 0) {
        return result.filePaths[0];
      }
      return null;
    });

    ipcMain.handle('save-dropped-file', async (event, data: { fileName: string; buffer: ArrayBuffer }) => {
      try {
        const tempDir = path.join(os.tmpdir(), 'tattletale-temp');
        await fs.mkdir(tempDir, { recursive: true });
        
        const filePath = path.join(tempDir, data.fileName);
        const buffer = Buffer.from(data.buffer);
        await fs.writeFile(filePath, buffer);
        
        console.log('Saved dropped file to:', filePath);
        return filePath;
      } catch (error) {
        console.error('Failed to save dropped file:', error);
        throw error;
      }
    });

    ipcMain.handle('start-transcription', async (event, filePath: string) => {
      return this.startTranscription(filePath);
    });

    ipcMain.handle('cancel-transcription', () => {
      if (this.transcriptionProcess) {
        this.transcriptionProcess.kill();
        this.transcriptionProcess = null;
      }
      return true;
    });

    ipcMain.handle('export-transcript', async (event, data: { format: string; content: string; filename: string }) => {
      return this.exportTranscript(data.format, data.content, data.filename);
    });

    ipcMain.handle('open-external', async (event, url: string) => {
      await shell.openExternal(url);
      return true;
    });

    ipcMain.handle('show-message', async (event, options: any) => {
      const result = await dialog.showMessageBox(this.mainWindow!, options);
      return result;
    });
  }

  private setupAppEvents() {
    app.on('window-all-closed', () => {
      if (process.platform !== 'darwin') {
        app.quit();
      }
    });

    app.on('activate', async () => {
      if (BrowserWindow.getAllWindows().length === 0) {
        await this.createMainWindow();
      }
    });

    app.on('before-quit', () => {
      if (this.transcriptionProcess) {
        this.transcriptionProcess.kill();
      }
    });
  }

  private getAppState(): AppState {
    const usage = this.store.get('usage', {
      minutesUsed: 0,
      lastResetDate: new Date().toISOString(),
      nextResetDate: this.getNextMonthDate().toISOString()
    }) as UsageStats;

    const license = this.store.get('license') as License | null;
    
    const now = new Date();
    const nextReset = new Date(usage.nextResetDate);
    if (now >= nextReset) {
      usage.minutesUsed = 0;
      usage.lastResetDate = now.toISOString();
      usage.nextResetDate = this.getNextMonthDate().toISOString();
      this.store.set('usage', usage);
    }

    return {
      currentTier: license?.tier || 'free',
      usage,
      license,
      currentTranscript: null,
      isTranscribing: false,
      transcriptionProgress: 0
    };
  }

  private updateUsage(minutes: number): boolean {
    const usage = this.store.get('usage', {
      minutesUsed: 0,
      lastResetDate: new Date().toISOString(),
      nextResetDate: this.getNextMonthDate().toISOString()
    }) as UsageStats;

    const license = this.store.get('license') as License | null;
    
    if (license?.tier === 'unlimited' || license?.tier === 'student') {
      return true;
    }

    const now = new Date();
    const nextReset = new Date(usage.nextResetDate);
    if (now >= nextReset) {
      usage.minutesUsed = 0;
      usage.lastResetDate = now.toISOString();
      usage.nextResetDate = this.getNextMonthDate().toISOString();
    }

    if (usage.minutesUsed + minutes > 60) {
      return false;
    }

    usage.minutesUsed += minutes;
    this.store.set('usage', usage);
    return true;
  }

  private async validateLicense(licenseKey: string): Promise<License | null> {
    if (licenseKey.startsWith('UNLIMITED-')) {
      return {
        key: licenseKey,
        tier: 'unlimited',
        status: 'active'
      };
    } else if (licenseKey.startsWith('STUDENT-')) {
      return {
        key: licenseKey,
        tier: 'student',
        status: 'active',
        isStudent: true,
        expiryDate: this.getSixMonthsFromNow().toISOString()
      };
    }
    
    return null;
  }

  private async startTranscription(filePath: string): Promise<boolean> {
    try {
      const audioBuffer = await fs.readFile(filePath);
      const stats = await fs.stat(filePath);
      const fileSizeInMB = stats.size / (1024 * 1024);
      
      return new Promise((resolve) => {
        let progress = 0;
        const interval = setInterval(() => {
          progress += Math.random() * 8 + 2;
          progress = Math.min(progress, 100);
          
          this.mainWindow?.webContents.send('transcription-progress', Math.round(progress));
          
          if (progress >= 100) {
            clearInterval(interval);
            
            const segmentCount = Math.max(2, Math.min(8, Math.floor(fileSizeInMB / 5)));
            const segments: any[] = [];
            
            for (let i = 0; i < segmentCount; i++) {
              const startTime = i * 8;
              
              const sampleTexts = [
                'Welcome to this transcription example. This demonstrates how Tattletale processes audio files.',
                'The Whisper AI model provides highly accurate speech recognition with speaker detection.',
                'All processing happens locally on your device, ensuring complete privacy and security.',
                'You can edit the transcript directly in the interface and export to multiple formats.',
                'Speaker changes are detected automatically based on pauses in the conversation.',
                'Thank you for using Tattletale for your transcription needs.',
                'This is a sample transcription to demonstrate the app functionality.',
                'Upgrade to unlock unlimited transcription and additional export formats.'
              ];
              
              segments.push({
                timestamp: this.formatTimestamp(startTime),
                speaker: `Speaker ${(i % 3) + 1}`,
                text: sampleTexts[i % sampleTexts.length],
                startTime: startTime,
                endTime: startTime + 3 + Math.random() * 4
              });
            }
            
            const mockResult: TranscriptionResult = {
              segments,
              totalDuration: segmentCount * 8,
              speakers: Math.min(3, segmentCount)
            };
            
            this.mainWindow?.webContents.send('transcription-complete', mockResult);
            resolve(true);
          }
        }, 300);
      });
    } catch (error) {
      console.error('Transcription failed:', error);
      throw error;
    }
  }

  private formatTimestamp(seconds: number): string {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    
    if (hours > 0) {
      return `[${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}]`;
    } else {
      return `[${minutes}:${secs.toString().padStart(2, '0')}]`;
    }
  }

  private async exportTranscript(format: string, content: string, filename: string): Promise<boolean> {
    try {
      const result = await dialog.showSaveDialog(this.mainWindow!, {
        defaultPath: filename,
        filters: this.getFileFilters(format)
      });
      
      if (!result.canceled && result.filePath) {
        await fs.writeFile(result.filePath, content, 'utf8');
        return true;
      }
      return false;
    } catch (error) {
      console.error('Export error:', error);
      return false;
    }
  }

  private getFileFilters(format: string) {
    switch (format) {
      case 'txt':
        return [{ name: 'Text Files', extensions: ['txt'] }];
      case 'srt':
        return [{ name: 'Subtitle Files', extensions: ['srt'] }];
      case 'pdf':
        return [{ name: 'PDF Files', extensions: ['pdf'] }];
      case 'docx':
        return [{ name: 'Word Documents', extensions: ['docx'] }];
      default:
        return [{ name: 'All Files', extensions: ['*'] }];
    }
  }

  private getNextMonthDate(): Date {
    const date = new Date();
    date.setMonth(date.getMonth() + 1);
    date.setDate(1);
    return date;
  }

  private getSixMonthsFromNow(): Date {
    const date = new Date();
    date.setMonth(date.getMonth() + 6);
    return date;
  }
}

new TattletaleApp();
