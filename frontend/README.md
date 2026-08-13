# Plagiarism Detector Frontend

Modern React frontend for the AI-Powered Plagiarism Detection System.

## Tech Stack

- **React 18** - UI library
- **Vite** - Build tool and dev server
- **React Router** - Client-side routing
- **Axios** - HTTP client
- **CSS3** - Styling

## Project Structure

```
frontend/
├── src/
│   ├── components/      # Reusable UI components
│   ├── pages/          # Page components
│   ├── services/       # API service layer
│   ├── App.jsx         # Main app component
│   ├── main.jsx        # Entry point
│   └── index.css       # Global styles
├── public/             # Static assets
├── index.html          # HTML template
├── vite.config.js      # Vite configuration
└── package.json        # Dependencies
```

## Installation

### Prerequisites

- Node.js 16+ and npm

### Steps

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Start development server:
```bash
npm run dev
```

The app will be available at `http://localhost:5173`

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Features

- **Text Analysis** - Paste or type text for plagiarism checking
- **File Upload** - Support for TXT, PDF, and DOCX files
- **Real-time Results** - View detailed similarity analysis
- **History** - Access previous analysis results
- **Document Management** - Manage reference documents
- **Report Generation** - Download PDF reports
- **Responsive Design** - Works on desktop, tablet, and mobile

## API Integration

The frontend communicates with the FastAPI backend via REST APIs. The base URL is configured in `src/services/api.js`.

Default backend URL: `http://localhost:8000/api`

## Configuration

### Proxy Setup

Vite is configured to proxy API requests to the backend:

```javascript
// vite.config.js
proxy: {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true,
  },
}
```

### Environment Variables

Create a `.env` file for custom configuration:

```env
VITE_API_URL=http://localhost:8000/api
```

## Building for Production

```bash
npm run build
```

Build output will be in the `dist/` directory.

## Deployment

The built frontend can be deployed to:
- Netlify
- Vercel
- GitHub Pages
- Any static hosting service

Ensure the API URL is configured for production environment.

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

## Contributing

1. Create a feature branch
2. Make changes
3. Test thoroughly
4. Submit a pull request

## License

Educational project for BTech CSE demonstration....
