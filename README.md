# SmartDoc AI - Futuristic UI Edition

SmartDoc AI is an advanced backend API and frontend architecture. This project has been fully rewritten into a decoupled monolithic structure featuring a **React + Vite** frontend and **Flask API** backend with Endee Vector capabilities!

## 1. Project Folder Structure

```
SmartDoc AI/
│
├── app.py                      # Main Backend FastAPI / Flask Server
├── requirements.txt            # Python dependencies
├── smartdoc_history.db         # SQLite storage for doc histories
├── utils/                      # Document chunking extractors
├── embeddings/                 # SentenceTransformer local embeddings wrapper
├── endee_integration/          # local mock of Endee Vector Database
├── auth/                       # Local bcrypt database handlers
│
└── client/                     # Brand new React / Vite frontend
    ├── package.json
    ├── vite.config.js
    ├── tailwind.config.js
    ├── src/
    │   ├── App.jsx             # React Router
    │   ├── main.jsx            # Entry point
    │   ├── index.css           # Tailwind + Custom UI Classes
    │   ├── components/
    │   │   └── ParticleBackground.jsx # Neural animated background (tsParticles)
    │   └── pages/
    │       ├── Login.jsx       # Glassmorphism futuristic login
    │       └── Dashboard.jsx   # Grid based dashboard UI
```

## 2. Installation Commands

You need to spin up both the Frontend and the Backend locally. Open two separate terminal windows.

### Backend Setup
```bash
# Ensure you are situated in the root folder /SmartDoc AI
pip install -r requirements.txt

# Run the Flask backend
python app.py
```
> The API will be exposed on **http://localhost:5000** allowing CORS connections.

### Frontend Setup
```bash
# Navigate to the client directory
cd client

# Install NPM dependencies
npm install

# Start the Vite development server
npm run dev
```
> The React GUI will be exposed on **http://localhost:5173**.

## Architecture & Features Built
- **Backend:** Flask abstracts away complex python modules (like SentenceTransformers and the OpenAI API logic) gracefully exposing endpoints.
- **Frontend Design:** Completely relies on standard web features like CSS flexbox and grids coupled with `Framer Motion` smooth animations. `tsParticles` is used to execute the neural network background requested.
- **Styling:** Custom configured `#0f172a` themes and glassmorphism boxes logic utilizing `backdrop-filter: blur(x)` attributes.
