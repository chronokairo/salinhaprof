from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename
from datetime import datetime
import os
from utils import allowed_file

uploads_bp = Blueprint('uploads', __name__, url_prefix='/api')

@uploads_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_file():
    """Upload de arquivos (vídeos, materiais, avatares)"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400
        
        file = request.files['file']
        file_type = request.form.get('type', 'material')  # material, video, avatar
        
        if file.filename == '':
            return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Adicionar timestamp para evitar conflitos
            name, ext = os.path.splitext(filename)
            filename = f"{name}_{int(datetime.now().timestamp())}{ext}"
            
            # Determinar subdiretório baseado no tipo
            subdir = {
                'video': 'videos',
                'avatar': 'avatars', 
                'material': 'materials'
            }.get(file_type, 'materials')
            
            # Criar diretório se não existir
            upload_path = os.path.join('uploads', subdir)
            os.makedirs(upload_path, exist_ok=True)
            
            filepath = os.path.join(upload_path, filename)
            file.save(filepath)
            
            # URL relativa para o arquivo
            file_url = f"/uploads/{subdir}/{filename}"
            
            return jsonify({
                'message': 'Arquivo enviado com sucesso',
                'file_url': file_url,
                'filename': filename
            }), 200
        
        return jsonify({'error': 'Tipo de arquivo não permitido'}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@uploads_bp.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """Servir arquivos estáticos de upload"""
    try:
        return send_file(
            os.path.join('uploads', filename),
            as_attachment=False
        )
    except Exception as e:
        return jsonify({'error': 'Arquivo não encontrado'}), 404