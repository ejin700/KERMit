from flask_restful import Resource
from server.models.user import User
from server.server import app
from flask import request
from server.resources.google_auth import GoogleAuth
from flask import g


@app.before_request
def authorize_token():
    """
    Method to run before all requests; determines if a user has a valid
    Google OAuth2 token and uses the token to discover who the user making the request is.
    The user is then loaded in from the database and stored in a special flask object called 'g'.
    While g is not appropriate for storing data across requests, it provides a global namespace
    for holding any data you want during a single app context.
    """
    if 'Authorization' not in request.headers:
        return {'message': 'Request denied access',
                'reason': 'Authorization header missing. Please provide an '
                           'OAuth2 Token with your request'}, 400

    auth_header = request.headers.get('Authorization')
    if 'Bearer ' not in auth_header:
        return {'message': 'Request denied access',
                'reason': "Malformed authorization header provided. Please make sure to "
                           "specify the header prefix correctly as 'Bearer ' and try again."}, 400

    # validate the token with Google
    access_token = auth_header.split("Bearer ")[1]

    google_auth = GoogleAuth()
    validation = google_auth.validate_token(access_token)
    if 'error' in validation.keys():
        return {'message': 'Request denied access',
                'reason': f'Google rejected oauth2 token: {validation["error_description"]}'}, 401

    g.access_token = access_token

    # unless this is a registration attempt, find the user associated with access token
    if request.endpoint != 'registration':
        user = User.find_by_g_id(validation['user_id'])
        if not user:
            return {'message': 'Request denied access',
                    'reason': 'User is not yet registered with this application; please '
                              'register before proceeding'}, 401

        # save this user for the rest of the request processing
        g.user = user


class Registration(Resource):
    """
    Resource for registering a user with this puzzle API. Requires that an access_token
    is set.
    """
    def post(self):
        google_auth = GoogleAuth()

        try:
            user_info = google_auth.get_user_information(g.access_token)
            if 'error' in user_info.keys():
                return {'message': 'User could not be registered',
                        'reason': 'User identity could not be found; valid OAuth2 access '
                                  'token not received.'}, 401

            elif any(field not in user_info.keys() for field in ['id', 'email']):
                return {'message': 'User could not be registered',
                        'reason': "Google id (unique user identifier) and email must be "
                                  "retrievable attributes, but Google would not provide them."}, 401
        except Exception as e:
            print(f"Unexpected error occurred getting user info from Google: {e}")
            return {'message': 'User could not be registered',
                    'reason': "Could not determine user information from Google using Oath2 token"
                              "for unknown reason"}, 500

        try:
            # does user with user id already exist?
            if User.find_by_g_id(user_info['id']):
                return {'message': f'User with Google ID {user_info["id"]} is already registered.'}

            new_user = User(
                g_id=user_info['id'],
                first_name=user_info['given_name'] if 'given_name' in user_info.keys() else None,
                last_name=user_info['family_name'] if 'family_name' in user_info.keys() else None,
                email=user_info['email']
            )
            new_user.save()
            return {'message': 'User {} {} was successfully registered'.format(
                                new_user.first_name, new_user.last_name)}

        except Exception as e:
            print(f"Unexpected error occurred registering new user in db: {e}")
            return {'message': 'User could not be registered.',
                    'reason': f'An unknown error occurred {e}'}, 500
