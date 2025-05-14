import React, { useState } from "react";
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Home from './pages/Home';
import CriarSalinha from './pages/CriarSalinha';
import SalaCard from './components/SalaCard';

function App() {
  const [showModal, setShowModal] = useState(false);
  const [videoUrl, setVideoUrl] = useState("");

  const salinhas = [
    { titulo: 'Matemática Avançada', horario: 'Seg e Qua - 18h', professor: 'Prof. João Silva' },
    { titulo: 'Matemática Básica', horario: 'Seg e Qua - 18h', professor: 'Prof. Ana Lima' },
    { titulo: 'Redação ENEM', horario: 'Ter e Qui - 19h', professor: 'Prof. Ricardo Souza' },
    { titulo: 'Química Avançada', horario: 'Sex - 20h', professor: 'Profa. Camila Oliveira' },
  ];

  return (
    <Router>
      <div className="min-h-screen bg-gradient-to-br from-indigo-100 via-white to-purple-100 p-6">
        <div className="max-w-6xl mx-auto">
          <header className="mb-8 text-center">
            <h1 className="text-4xl font-extrabold text-indigo-700 drop-shadow">🎓 Plataforma de Salinhas</h1>
            <p className="text-lg text-gray-600 mt-2">Aulas organizadas por professores. Participe e aprenda com qualidade!</p>
          </header>

          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/criar-salinha" element={<CriarSalinha />} />
          </Routes>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {salinhas.map((sala, index) => (
              <SalaCard
                key={index}
                titulo={sala.titulo}
                horario={sala.horario}
                professor={sala.professor}
              />
            ))}
          </div>
        </div>

        {showModal && (
          <div className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50">
            <div className="bg-white rounded-2xl shadow-lg p-6 w-[90%] max-w-2xl relative">
              <button
                onClick={() => setShowModal(false)}
                className="absolute top-2 right-2 text-gray-500 hover:text-gray-800 text-xl"
              >
                ×
              </button>
              <h2 className="text-2xl font-bold mb-4">Aula Gravada</h2>
              <div className="aspect-w-16 aspect-h-9">
                <iframe
                  className="w-full h-64 rounded-lg"
                  src={videoUrl}
                  title="Vídeo da aula"
                  frameBorder="0"
                  allowFullScreen
                />
              </div>
            </div>
          </div>
        )}
      </div>
    </Router>
  );
}

export default App;

