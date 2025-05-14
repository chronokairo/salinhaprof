// src/components/Sidebar.jsx
export default function Sidebar() {
    return (
        <aside className="w-64 bg-indigo-700 text-white p-6 hidden md:block">
            <h2 className="text-2xl font-bold mb-6">Painel</h2>
            <nav className="space-y-4">
                <a href="#" className="block hover:text-indigo-200">Minhas Salas</a>
                <a href="#" className="block hover:text-indigo-200">Nova Sala</a>
                <a href="#" className="block hover:text-indigo-200">Configurações</a>
            </nav>
        </aside>
    );
}

import { Home, BookOpen, Settings } from "lucide-react";

<ul className="space-y-2">
    <li className="flex items-center gap-2"><Home size={18} /> Início</li>
    <li className="flex items-center gap-2"><BookOpen size={18} /> Minhas Salas</li>
    <li className="flex items-center gap-2"><Settings size={18} /> Configurações</li>
</ul>
// src/components/Sidebar.jsx
