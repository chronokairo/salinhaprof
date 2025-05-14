import { useState } from 'react';
import { BookOpenIcon, ClockIcon, UserIcon } from 'lucide-react';

export default function SalaCard({ titulo, horario, professor }) {
    const [videoUrl, setVideoUrl] = useState('');
    const [showModal, setShowModal] = useState(false);

    return (
        <div className="bg-white border-l-4 border-indigo-600 p-5 rounded-2xl shadow hover:shadow-lg transition-all duration-300">
            <h3 className="text-lg font-bold text-gray-800 flex items-center mb-2">
                <BookOpenIcon className="h-5 w-5 mr-2 text-indigo-600" />
                {titulo}
            </h3>
            <p className="text-sm text-gray-600 flex items-center">
                <ClockIcon className="h-4 w-4 mr-2 text-indigo-400" />
                {horario}
            </p>
            <p className="text-sm text-gray-600 flex items-center mt-1">
                <UserIcon className="h-4 w-4 mr-2 text-indigo-400" />
                {professor}
            </p>
            <button
                onClick={() => {
                    setVideoUrl("https://www.youtube.com/embed/dQw4w9WgXcQ"); // Substitua pela URL desejada
                    setShowModal(true);
                }}
                className="bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-700 mt-4"
            >
                Ver aula gravada
            </button>

            {showModal && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
                    <div className="bg-white p-5 rounded-lg shadow-lg">
                        <iframe
                            width="560"
                            height="315"
                            src={videoUrl}
                            title="Aula Gravada"
                            frameBorder="0"
                            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                            allowFullScreen
                        ></iframe>
                        <button
                            onClick={() => setShowModal(false)}
                            className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 mt-4"
                        >
                            Fechar
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}
