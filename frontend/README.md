# Book Creator Frontend

A modern, responsive web interface for the AI-powered Book Creator application. Built with Node.js, Express, and vanilla JavaScript.

## Features

- 🎨 **Modern UI/UX**: Responsive design with gradient themes and smooth animations
- 📚 **Book Type Selection**: Interactive cards showing 8 specialized book types
- 🔧 **Real-time Configuration**: Live estimates for cost, time, and pages
- 📊 **Generation Progress**: Real-time progress tracking during book creation
- 📁 **File Upload**: Support for source content integration
- 📈 **Results Dashboard**: Comprehensive generation statistics and download links
- 🚀 **System Status**: Real-time backend health monitoring

## Quick Start

### Prerequisites
- Node.js 16+ 
- Book Creator Backend running on port 8000

### Installation

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Configure environment:**
   ```bash
   cp env.example .env
   # Edit .env if needed (default settings work for local development)
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```

4. **Open your browser:**
   Navigate to `http://localhost:3000`

## Production Deployment

### Using Node.js

```bash
# Install production dependencies
npm install --production

# Start the server
npm start
```

### Using PM2 (Recommended)

```bash
# Install PM2 globally
npm install -g pm2

# Start with PM2
pm2 start server.js --name "book-creator-frontend"

# Save PM2 configuration
pm2 save
pm2 startup
```

### Using Docker

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install --production
COPY . .
EXPOSE 3000
CMD ["npm", "start"]
```

## API Integration

The frontend communicates with the backend through these endpoints:

- `GET /api/health` - System status and configuration
- `GET /api/book-types` - Available book types and specifications  
- `POST /api/generate-book` - Generate a new book
- `POST /api/upload` - Upload source content files

## Book Types Supported

The interface supports all 8 book types from the backend:

1. **Quick Guide** - Concise overviews (3 chapters, ~800 words/chapter)
2. **Tutorial** - Step-by-step learning (5 chapters, ~1200 words/chapter)
3. **Comprehensive Guide** - In-depth coverage (8 chapters, ~2000 words/chapter)
4. **Professional Handbook** - Practical reference (10 chapters, ~1800 words/chapter)
5. **University Textbook** - Academic content (12 chapters, ~3000 words/chapter)
6. **Technical Manual** - Implementation details (15 chapters, ~2500 words/chapter)
7. **Interactive Workbook** - Exercises and practice (6 chapters, ~1500 words/chapter)
8. **Research Compendium** - Academic research (20 chapters, ~4000 words/chapter)

## Configuration

### Environment Variables

```bash
# Server Configuration
PORT=3000                    # Frontend server port
BACKEND_URL=http://127.0.0.1:8000  # Backend API URL

# Optional Production Settings
NODE_ENV=production          # Environment mode
SESSION_SECRET=your-secret   # Session encryption key
CORS_ORIGIN=https://yourdomain.com  # CORS origin for production
```

### Customization

#### Styling
- Edit `public/styles.css` for visual customization
- CSS variables are defined in `:root` for easy theming
- Responsive breakpoints: 768px (tablet), 480px (mobile)

#### Content
- Modify `public/index.html` for structure changes
- Update `public/app.js` for functionality changes
- Icons use Lucide React icon library

## File Structure

```
frontend/
├── package.json           # Dependencies and scripts
├── server.js             # Express server
├── env.example           # Environment template
├── public/               # Static assets
│   ├── index.html       # Main HTML file
│   ├── styles.css       # CSS styling
│   └── app.js           # JavaScript application
└── uploads/             # File upload directory (auto-created)
```

## Development

### Scripts

```bash
npm start              # Start production server
npm run dev            # Start with nodemon (auto-reload)
npm run build          # Build assets (placeholder)
npm test               # Run tests (placeholder)
```

### Adding Features

1. **New API Endpoints**: Add routes in `server.js`
2. **UI Components**: Add HTML in `index.html`, styles in `styles.css`
3. **JavaScript Logic**: Extend the `BookCreatorApp` class in `app.js`
4. **Styling**: Use CSS variables for consistent theming

## Security

The frontend implements several security measures:

- **Helmet.js**: Security headers
- **CORS**: Configurable cross-origin resource sharing
- **File Upload Limits**: 10MB maximum file size
- **Input Validation**: Client and server-side validation
- **CSP**: Content Security Policy for XSS prevention

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Troubleshooting

### Common Issues

1. **Backend Connection Failed**
   - Verify backend is running on port 8000
   - Check `BACKEND_URL` in environment variables
   - Ensure no firewall blocking connections

2. **File Upload Not Working**
   - Check file size (max 10MB)
   - Verify file format (`.md`, `.txt` supported)
   - Ensure `uploads/` directory exists and is writable

3. **Generation Stuck**
   - Check backend logs for errors
   - Verify API key is configured in backend
   - Try with smaller book parameters

### Development Issues

1. **Port Already in Use**
   ```bash
   # Kill process on port 3000
   lsof -ti:3000 | xargs kill -9
   ```

2. **Nodemon Not Working**
   ```bash
   # Install nodemon globally
   npm install -g nodemon
   ```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make changes and test thoroughly
4. Submit a pull request with clear description

## License

MIT License - see the main project LICENSE file for details.

## Support

For issues and questions:
- Check the main project documentation
- Review backend API documentation
- Check browser console for JavaScript errors
- Verify network requests in browser DevTools
