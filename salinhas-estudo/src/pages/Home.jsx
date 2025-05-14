// src/pages/Home.jsx
import React, { useState, useEffect } from 'react';

const Home = () => {
    const [salas, setSalas] = useState([
        { id: 1, titulo: "Matemática Avançada", horario: "10:00 - 12:00", professor: "Professor João" },
        { id: 2, titulo: "Física para Iniciantes", horario: "14:00 - 16:00", professor: "Professor Ana" },
        // Adicione mais salas conforme necessário
    ]);

    return (
        <div className="min-h-screen bg-gray-100 p-6">
            {/* Cabeçalho */}
            <header className="flex justify-between items-center bg-indigo-600 text-white p-4 rounded-lg">
                <h1 className="text-2xl font-semibold">Salinhas de Estudo</h1>
                <button className="bg-indigo-800 p-2 rounded-lg text-white">Criar Salinha</button>
            </header>

            {/* Lista de Salinhas */}
            <div className="mt-6 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
                {salas.map((sala) => (
                    <div key={sala.id} className="bg-white p-4 rounded-lg shadow hover:shadow-lg transition">
                        <h2 className="text-xl font-semibold text-indigo-700">{sala.titulo}</h2>
                        <p className="text-gray-600">Horário: {sala.horario}</p>
                        <p className="text-gray-600">Professor: {sala.professor}</p>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default Home;
