// src/pages/CriarSalinha.jsx
import React, { useState } from 'react';

const CriarSalinha = () => {
    const [titulo, setTitulo] = useState('');
    const [horario, setHorario] = useState('');
    const [professor, setProfessor] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault();
        // Aqui você pode adicionar o código para salvar a nova salinha no banco de dados
        console.log("Nova Salinha Criada:", { titulo, horario, professor });
    };

    return (
        <div className="min-h-screen bg-gray-100 p-6">
            <h1 className="text-2xl font-semibold text-center">Criar Nova Salinha</h1>

            <form onSubmit={handleSubmit} className="max-w-md mx-auto bg-white p-6 rounded-lg shadow-lg mt-6">
                <div className="mb-4">
                    <label htmlFor="titulo" className="block text-sm font-medium text-gray-700">Título</label>
                    <input
                        id="titulo"
                        type="text"
                        value={titulo}
                        onChange={(e) => setTitulo(e.target.value)}
                        className="w-full px-4 py-2 mt-1 border border-gray-300 rounded-lg"
                        placeholder="Título da salinha"
                        required
                    />
                </div>

                <div className="mb-4">
                    <label htmlFor="horario" className="block text-sm font-medium text-gray-700">Horário</label>
                    <input
                        id="horario"
                        type="text"
                        value={horario}
                        onChange={(e) => setHorario(e.target.value)}
                        className="w-full px-4 py-2 mt-1 border border-gray-300 rounded-lg"
                        placeholder="Ex: 10:00 - 12:00"
                        required
                    />
                </div>

                <div className="mb-4">
                    <label htmlFor="professor" className="block text-sm font-medium text-gray-700">Professor</label>
                    <input
                        id="professor"
                        type="text"
                        value={professor}
                        onChange={(e) => setProfessor(e.target.value)}
                        className="w-full px-4 py-2 mt-1 border border-gray-300 rounded-lg"
                        placeholder="Nome do professor"
                        required
                    />
                </div>

                <button type="submit" className="w-full bg-indigo-600 text-white py-2 rounded-lg hover:bg-indigo-700">
                    Criar Salinha
                </button>
            </form>
        </div>
    );
};

export default CriarSalinha;
