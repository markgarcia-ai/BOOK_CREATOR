const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const compression = require('compression');
const morgan = require('morgan');
const path = require('path');
const axios = require('axios');
const multer = require('multer');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;
const BACKEND_URL = process.env.BACKEND_URL || 'http://127.0.0.1:8000';

// Middleware
app.use(helmet({
    contentSecurityPolicy: {
        directives: {
            defaultSrc: ["'self'"],
            styleSrc: ["'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net", "https://fonts.googleapis.com"],
            scriptSrc: ["'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net"],
            fontSrc: ["'self'", "https://fonts.gstatic.com"],
            imgSrc: ["'self'", "data:", "https:"],
            connectSrc: ["'self'", BACKEND_URL]
        }
    }
}));
app.use(compression());
app.use(morgan('combined'));
app.use(cors());
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Serve static files
app.use(express.static(path.join(__dirname, 'public')));

// Configure multer for file uploads
const upload = multer({ 
    dest: 'uploads/',
    limits: { fileSize: 10 * 1024 * 1024 } // 10MB limit
});

// API Routes
app.get('/api/health', async (req, res) => {
    try {
        const response = await axios.get(`${BACKEND_URL}/health`);
        res.json({
            frontend: 'healthy',
            backend: response.data,
            timestamp: new Date().toISOString()
        });
    } catch (error) {
        res.status(500).json({
            frontend: 'healthy',
            backend: 'unhealthy',
            error: error.message,
            timestamp: new Date().toISOString()
        });
    }
});

app.get('/api/book-types', async (req, res) => {
    try {
        // Proxy to backend to get updated book types with 10x costs
        const response = await axios.get(`${BACKEND_URL}/book-types`);
        res.json(response.data);
    } catch (error) {
        console.error('Book types proxy error:', error.message);
        res.status(500).json({ 
            error: 'Failed to fetch book types',
            details: error.message 
        });
    }
});

app.post('/api/generate-book', async (req, res) => {
    try {
        const response = await axios.post(`${BACKEND_URL}/simple-workflow`, req.body, {
            timeout: 300000 // 5 minute timeout for book generation
        });
        res.json(response.data);
    } catch (error) {
        console.error('Book generation error:', error.message);
        res.status(500).json({ 
            error: 'Book generation failed', 
            details: (error.response && error.response.data) || error.message 
        });
    }
});

app.post('/api/upload-html', upload.single('file'), async (req, res) => {
    try {
        if (!req.file) {
            return res.status(400).json({ error: 'No file uploaded' });
        }

        // Create form data for backend
        const FormData = require('form-data');
        const form = new FormData();
        form.append('file', req.file.buffer, {
            filename: req.file.originalname,
            contentType: req.file.mimetype
        });

        const response = await axios.post(`${BACKEND_URL}/upload-html`, form, {
            headers: {
                ...form.getHeaders(),
            },
            timeout: 60000 // 1 minute timeout for HTML processing
        });

        res.json(response.data);
    } catch (error) {
        console.error('HTML upload proxy error:', error.message);
        res.status(500).json({ 
            error: 'Failed to process HTML file',
            details: (error.response && error.response.data) || error.message
        });
    }
});

app.post('/api/upload', upload.single('file'), async (req, res) => {
    try {
        if (!req.file) {
            return res.status(400).json({ error: 'No file uploaded' });
        }
        
        // In a real implementation, you'd process the file here
        // For now, just return file info
        res.json({
            success: true,
            filename: req.file.originalname,
            size: req.file.size,
            message: 'File uploaded successfully'
        });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Serve the main app
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Error handling middleware
app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).json({ error: 'Something went wrong!' });
});

// 404 handler
app.use((req, res) => {
    res.status(404).json({ error: 'Not found' });
});

// Start server
app.listen(PORT, () => {
    console.log(`🚀 Book Creator Frontend running on http://localhost:${PORT}`);
    console.log(`📡 Backend URL: ${BACKEND_URL}`);
    console.log(`📁 Serving static files from: ${path.join(__dirname, 'public')}`);
});

module.exports = app;
