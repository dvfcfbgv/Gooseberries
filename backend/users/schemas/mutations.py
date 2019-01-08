import graphene
import copy
from graphql import GraphQLError
from django.contrib.auth import authenticate, login, logout
from backend.users.schemas.queries import UserNode
from backend.users.models import User as UserModel
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.validators import ASCIIUsernameValidator
from backend.utils import remove_none, validate_name


class Register(graphene.relay.ClientIDMutation):
    """
    Registers user with the provided parameters,
    returns back a User node.
    """
    class Input:
        username      = graphene.String(required=True, description="User's username")
        email         = graphene.String(required=True, description="User's email")
        password      = graphene.String(required=True, description="User's password")
        date_of_birth = graphene.types.datetime.Date(required=True, description="User's date of birth")
        first_name    = graphene.String(description="User's first name", default_value="")
        last_name     = graphene.String(description="User's last name", default_value="")
        is_staff      = graphene.Boolean(description="Whether the user is an admin or not", default_value=False)

    ' Fields '
    user = graphene.Field(UserNode)

    def mutate_and_get_payload(root, info, **input):
        "Login check"
        if not info.context.user.is_anonymous:
            raise GraphQLError('Already logged in.')
        "Extra username validation"
        if ' ' in input.get('username'):
            raise GraphQLError('Invalid username format.')
        "Email validation"
        try:
            validate_email(input.get('email'))
        except ValidationError:
            raise GraphQLError('Invalid email format.')
        "Checks to see if the user exists in the database"
        if UserModel.objects.filter(username=input.get('username')).first():
            raise GraphQLError('Username already taken.')
        if UserModel.objects.filter(email=input.get('email')).first():
            raise GraphQLError('Email already taken.')
        "Checks name format"
        if not validate_name(input.get('first_name')) or not validate_name(input.get('last_name')):
            raise GraphQLError('Invalid first/last name.')

        password = input.pop('password')
        new_user = UserModel(**input)
        new_user.set_password(password)
        new_user.save()
        return Register(user=new_user)


class Login(graphene.relay.ClientIDMutation):
    """
    Login function; the login process is handled backend by Django.
    """
    class Input:
        username = graphene.String(required=True)
        password = graphene.String(required=True)

    ' Fields '
    user = graphene.Field(UserNode)

    def mutate_and_get_payload(root, info, **input):
        # Logged in user
        if not info.context.user.is_anonymous:
            raise GraphQLError('Log out first to login to accounts.')

        user = authenticate(**input)

        # Disabled user or wrong credentials
        if user is None:
            raise GraphQLError('Unable to authenticate user. Either the account is disabled or the entered credentials are wrong.')

        login(info.context, user)
        return Login(user=user)

class Logout(graphene.Mutation):
    """
    Logs the user out, returning a boolean indicating whether the process
    was successful or not. No input needed; logout handled behind the scenes.
    """

    ' Fields '
    successful = graphene.Boolean()

    def mutate(self, info):
        if info.context.user.is_anonymous:
            raise GraphQLError('Not logged in.')
        try: 
            logout(info.context)
        except: 
            raise GraphQLError('Failed to log in.')
        return Logout(successful=True)
        

        
class UpdateProfile(graphene.relay.ClientIDMutation):
    """
    Update user's profile according to the provided optional arguments.
    """
    class Input:
        first_name = graphene.String()
        last_name  = graphene.String()
        # profile_image
    
    ' Fields '
    user = graphene.Field(UserNode)

    def mutate_and_get_payload(root, info, **input):
        user = info.context.user

        if user.is_anonymous:
            raise GraphQLError('Please login first to modify profile.')

        if not validate_name(input.get('first_name')) or not validate_name(input.get('last_name')):
            raise GraphQLError('Invalid first/last name.')
        
        filtered_input = remove_none(input) 

        updated_user = UserModel.objects.get(id=user.id)
        for (key, value) in filtered_input.items():
            setattr(updated_user, key, value)
        updated_user.save()

        return UpdateProfile(user=updated_user)
    

class DeleteAccount(graphene.Mutation):
    """
    Logouts the user and deletes the account.
    Optional inputs, depending on whether its an admin
    deleting users or users deleting themselves.
    """
    class Arguments:
        username = graphene.String(description="Deleted user's username")

    ' Fields '
    user = graphene.Field(UserNode)

    def mutate(self, info, username):
        if info.context.user.is_anonymous:
            raise GraphQLError('Not logged in.')

        if not username:
            user = info.context.user
        else:
            if not info.context.user.is_staff:
                raise GraphQLError('Not an admin.')
            user = UserModel.objects.get(username=username)
        deleted_user = copy.deepcopy(user)

        try:
            if not username:
                logout(info.context)
            user.delete()
        except:
            raise GraphQLError('Failed to delete account.')

        return DeleteAccount(user=deleted_user)


class EnableAccount(graphene.relay.ClientIDMutation):
    """
    Enables the account with the given username
    """
    class Input:
        username = graphene.String(required=True, description="User's username")
    
    ' Fields '
    user = graphene.Field(UserNode)

    def mutate_and_get_payload(root, info, **input):
        called_user = info.context.user
        if called_user.is_anonymous:
            raise GraphQLError('Not logged in.')
        # Admin rights
        if not called_user.is_staff:
            raise GraphQLError('Not an admin.')

        enabled_user = UserModel.objects.get(username=input.get('username'))
        
        # Already enabled
        if enabled_user.is_active:
            raise GraphQLError('User already active')

        enabled_user.enable()
        enabled_user.save(called_by_admin=True)
        return EnableAccount(user=enabled_user)


class DisableAccount(graphene.relay.ClientIDMutation):
    """
    Disables account with the provided username
    """
    class Input:
        username = graphene.String(required=True, description="User's username")

    ' Fields '
    user = graphene.Field(UserNode)

    def mutate_and_get_payload(root, info, **input):
        called_user = info.context.user
        if called_user.is_anonymous:
            raise GraphQLError('Not logged in.')
        # Admin rights
        if not called_user.is_staff:
            raise GraphQLError('Not an admin.')

        disabled_user = UserModel.objects.get(username=input.get('username'))
        
        # Already enabled
        if not disabled_user.is_active:
            raise GraphQLError('User already disabled')

        disabled_user.disable()
        disabled_user.save(called_by_admin=True)
        return DisableAccount(user=disabled_user)
        


