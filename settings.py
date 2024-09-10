from bson import ObjectId

def get_user_settings(db, user_id):
    user = db.users.find_one({'_id': ObjectId(user_id)})
    
    if user is None:
        return {
            'name': '',
            'username': '',
            'language': 'es',  # Valor por defecto
        }
    
    return {
        'name': user.get('fullname', ''),
        'username': user.get('username', ''),
        'language': user.get('language', 'es'),
    }

def update_user_settings(db, user_id, form_data):
    name = form_data.get('name')
    language = form_data.get('language')

    # Actualizar solo el nombre y el idioma del usuario
    db.users.update_one(
        {'_id': user_id},
        {
            '$set': {
                'fullname': name,
                'language': language
            }
        }
    )
    return True