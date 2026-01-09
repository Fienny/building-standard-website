import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navigation from './components/Navigation';
import Home from './pages/Home';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Documents from './pages/Documents';
import DocumentPreview from './pages/DocumentPreview';
import './App.css';

function App() {
  return (
    <Router>
      <div className="app">
        <Navigation />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="/documents" element={<Documents />} />
          <Route path="/documents/:id" element={<DocumentPreview />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
