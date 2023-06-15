from .models import *
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly
from django.contrib.auth.hashers import make_password
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from .serializers import *
from .backend import EmailAuthBackend
from rest_framework.authtoken.models import Token

from django.db.models import F


@api_view(['POST'])
def signup_api(request):
    first = request.data.get("first_name")
    last = request.data.get("last_name")
    username = request.data.get("username")
    email = request.data.get("email")
    # password = request.data.get("password")
    password = make_password(request.data.get("password"))
    if (User.objects.filter(username=username)):
        return Response({"message": "This Username is already registered"},
                        status=status.HTTP_400_BAD_REQUEST)
    if (User.objects.filter(email=email).exists()):
        return Response({"message": "This email is already registered"}, status=status.HTTP_400_BAD_REQUEST)
    user = User.objects.create(first_name=first,
                               last_name=last,
                               username=username,
                               email=email,
                               password=password)

    return Response({"message": "User registered successfully"}, status=status.HTTP_200_OK)


@api_view(['GET'])
def user_list(request):
    user = User.objects.all()
    data = UserSerializer(user, many=True, context={'request': request}).data
    return Response({"data": data}, status=status.HTTP_200_OK)


@api_view(["GET"])
def search_StartsWith(request):
    search_user = request.data.get("user")
    if (User.objects.filter(username__startswith=search_user).exists()):
        data = User.objects.filter(username__startswith=search_user)
        data1 = UserSerializer(data, many=True, context={
                               'request': request}).data
        return Response({"data": data1})
    else:
        return Response({"message ": "No such user exists."})


# @ DENOTES DECORATORS (kind of function which has a special functionality and can be implemented or added anywhere)
@api_view(["GET"])
def search_cont(request):
    search_user = request.query_params.get("user")
    # http://127.0.0.1:8000/accounts/searchBetween?user=sh
    if (User.objects.filter(username__contains=search_user).exists()):
        data = User.objects.filter(email__contains=search_user)
        data1 = UserSerializer(data, many=True, context={
            'request': request}).data
        return Response({"data": data1})
    else:
        return Response({"message ": "No such user exists."})


@api_view(["GET"])
def login(request):
    login_username = request.data.get("user")
    login_password = request.data.get("password")
    print("data entered")
    if (User.objects.filter(username=login_username).exists()):
        data = EmailAuthBackend.authenticate(request, username=login_username,
                                             password=login_password)
        if data:
            try:
                token = Token.objects.get(user=data)
                # token = Token.objects.create(user=data)
                print("updated token:", token)
            except:
                token = Token.objects.create(user=data)

            data1 = UserSerializer(data, context={
                'request': request}).data
            return Response({"data ": data1, "token": token.key})
        else:
            return Response({"message": "the password is wrong"})
    else:
        return Response({"message ": "No such user exists."})


# For clients to authenticate, the token key should be included in the Authorization HTTP header. The key should be prefixed by the string literal "Token", with whitespace separating the two strings.
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profile(request):
    print("request:", request.user, request.user.id, request.user.email)
    user = User.objects.get(id=request.user.id)
    data = UserSerializer(user, context={'request': request}).data
    return Response({"data ": data})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    user = User.objects.get(id=request.user.id)
    # always access the user from user id becoz it is always unique
    print(user)
    if request.data.get("first_name"):
        user.first_name = request.data.get("first_name")
    if request.data.get("last_name"):
        user.last_name = request.data.get("last_name")
    if request.data.get("username"):
        user.username = request.data.get("username")
    user.save()
    data = UserSerializer(user, context={'request': request}).data
    return Response({"data ": data})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_post(request):
    user = User.objects.get(id=request.user.id)
    userID = request.user.id
    title_name = request.data.get("title")
    text_discrp = request.data.get("text")
    user_post = Post.objects.create(
        user=user, title=title_name, text=text_discrp)
    data = PostSerializer(user_post, context={'request': request}).data
    return Response({"message": data})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_post(request):
    user = User.objects.get(id=request.user.id)
    data = UserSerializer(user, context={'request': request}).data
    return Response({'message ': data})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_pass(request):
    user = User.objects.get(id=request.user.id)
    old_pass = request.data.get('old password')
    print(user.check_password(old_pass))

    if (user.check_password(old_pass)):
        print("Password Matched")
        new_pass = request.data.get('new password')
        confirm_pass = request.data.get('confirm password')
        print("new pass: ", new_pass, "confirm pass: ", confirm_pass)
        if (new_pass == confirm_pass):
            if (old_pass == new_pass):
                return Response({'message ': "Plz enter a different password than the last password "})
            print("user.password", user.password)
            user.password = make_password(new_pass)
            print(user.password)
            user.save()
            return Response({'message ': "Password changed successfully"})
        else:
            return Response({'message ': "new password and confirm password are different. Plz try again."})

    else:
        return Response({'message ': "wrong password"})


@api_view(['GET'])
def filter_date(request):
    from_date=request.data.get("from_date")
    to_date=request.data.get("to_date")
    data=User.objects.filter(DOB__range=[from_date,to_date])
    #DOB__range: DOB is the name of the field in the model __range is the function 
    # for range of months use [field_name]__month_range, etc
    data1 = UserSerializer(data, many=True, context={'request': request}).data
    return Response({"data": data1})

@api_view(['GET'])
def get_all_posts():
    posts = Post.objects.select_related('user').annotate(user_name=F('user__name')).values('id', 'name', 'author_name')
    print(posts)
