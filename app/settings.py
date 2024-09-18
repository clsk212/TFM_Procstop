# Third party imports
from bson import ObjectId

def get_user_settings(db, user_id):
    """
    Import user settings from Mongo
    """
    user = db.users.find_one({'_id': ObjectId(user_id)})
    
    if user is None:
        return {
            'name': '',
            'username': '',
            'language': 'es',
        }
    
    return {
        'name': user.get('fullname', ''),
        'username': user.get('username', ''),
        'language': user.get('language', 'es'),
    }

def update_user_settings(db, user_id, form_data):
    """
    Update user configuration to MongoDB
    """
    name = form_data.get('name')
    language = form_data.get('language')
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