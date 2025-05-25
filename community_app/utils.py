def get_attachment_type(attachment):
    """
    Determine the file type of an attachment based on its extension.
    Returns None if no attachment, or a string like 'pdf', 'image', 'document', or 'unknown'.
    """
    if not attachment:
        return None
        
    # Handle both filename string and FieldFile object
    filename = attachment.name if hasattr(attachment, 'name') else str(attachment)
    filename = filename.lower()
    
    if filename.endswith('.pdf'):
        return 'pdf'
    elif filename.endswith(('.jpg', '.jpeg', '.png', '.gif')):
        return 'image'
    elif filename.endswith(('.doc', '.docx')):
        return 'document'
    return 'unknown'