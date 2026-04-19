import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './utils/AuthContext';
import Navigation from './components/Navigation';
import Home from './pages/Home';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Documents from './pages/Documents';
import DocumentPreview from './pages/DocumentPreview';
import PaymentResult from './pages/PaymentResult';
import './App.css';

function App() {
  return (
    <Router>
      <AuthProvider>
        <div className="app">
          <Navigation />
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />
            <Route path="/documents" element={<Documents />} />
            <Route path="/documents/:id" element={<DocumentPreview />} />
            <Route path="/payment/success" element={<PaymentResult status="success" />} />
            <Route path="/payment/failed" element={<PaymentResult status="failed" />} />
            <Route path="/payment/pending" element={<PaymentResult status="pending" />} />
          </Routes>
        </div>
      </AuthProvider>
    </Router>
  );
}

export default App;
