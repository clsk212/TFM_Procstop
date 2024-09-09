def get_user_settings(mongo, user_id):
    # Asumiendo que el ID del usuario se almacena en la sesión o se pasa de alguna manera
    user = mongo.db.users.find_one({"_id": user_id})
    if user:
        return user.get('settings', {})  # Suponiendo que 'settings' es un diccionario
    return {}

def update_user_settings(mongo, user_id, form_data):
    # Actualizar la configuración del usuario en la base de datos
    settings_to_update = {
        'settings.preference': form_data['preference'],  # Ejemplo de campo del formulario
        # Agrega más campos según sea necesario
    }
    result = mongo.db.users.update_one({"_id": user_id}, {'$set': settings_to_update})
    return result.modified_count > 0  # Devuelve True si la actualización fue exitosa
