ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi', 'doc', 'docx', 'ppt', 'pptx'}

def allowed_file(filename):
    """Verifica se o tipo de arquivo é permitido para upload"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
