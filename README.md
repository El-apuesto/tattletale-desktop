# Tattletale - Privacy-First Desktop Transcription App

A desktop transcription application that processes audio and video files locally and offline using Whisper AI via @xenova/transformers.

## Features

- **Privacy-First**: All processing happens locally on your device
- **AI-Powered**: Uses OpenAI's Whisper model for accurate transcriptions
- **Speaker Detection**: Automatically detects and labels different speakers
- **Multiple Export Formats**: TXT, SRT, PDF, DOCX
- **Usage Tracking**: Monitor your transcription usage
- **License System**: Free and paid tiers with different features

## Tech Stack

- **Electron 28+**: Desktop app framework
- **React 18**: UI framework with TypeScript
- **Tailwind CSS**: Styling
- **@xenova/transformers**: ML/transcription engine
- **Electron Store**: Local data storage

## Prerequisites

- Node.js 16+ 
- npm or yarn

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd tattletale
```

2. Install dependencies:
```bash
npm install
```

3. Build the application:
```bash
npm run build
```

4. Start the application:
```bash
npm start
```

## Development

To run in development mode:

```bash
npm run dev
```

## Building Installers

To create installers for all platforms:

```bash
npm run make
```

This will create installers in the `out` directory:
- Windows: `.exe` installer
- macOS: `.dmg` or `.pkg`
- Linux: `.deb`, `.rpm`, and AppImage

## Project Structure

```
tattletale/
├── src/
│   ├── main.ts              # Electron main process
│   ├── preload.ts           # IPC bridge
│   ├── renderer/            # React UI
│   │   ├── components/      # React components
│   │   ├── App.tsx          # Main app component
│   │   └── styles.css       # Tailwind styles
│   ├── services/            # Business logic
│   │   ├── whisper.ts       # Whisper integration
│   │   └── export.ts        # Export functionality
│   └── types/               # TypeScript types
├── assets/                  # Static assets
├── webpack.*.js            # Webpack configs
└── package.json            # Dependencies and scripts
```

## Usage

1. **Free Tier**: 60 minutes/month, up to 3 speakers, TXT/SRT exports with watermark
2. **Unlimited ($6.99/month)**: Unlimited transcription, all speakers, all export formats
3. **Student Plans**: Discounted pricing with .edu email verification

## License System

- Free tier requires no license
- Paid tiers require license key activation
- License validation happens via backend API
- Keys are stored securely using Electron's safe storage

## Privacy & Security

- All audio processing happens locally
- No audio files are uploaded to external servers
- User data is stored locally using Electron Store
- License keys are encrypted at rest

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For support, please visit: https://tattletale.app