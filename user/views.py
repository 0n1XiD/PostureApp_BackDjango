import json

from django.db import transaction
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import ClientWeekSerializer, ClientSerializer, ClientPosturePhotosSerializer, \
    ClientDaySerializer, ClientConditionSerializer, ClientCompleteExerciseCountSerializer
from .services.auth_services import generate_token, create_user, client_setup_settings, \
    delete_token, change_password, get_user_from_auth_code, get_user_from_reset_password_code, \
    check_reset_password_valid, delete_reset_password_code
from .services.client_services import add_client_condition, get_client, add_client_photo, delete_client_photo, \
    get_client_photos, update_client_week, get_client_week, get_client_day, delete_client_day, add_client_to_archive, \
    previous_client_day, change_client_last_visit, reset_all_weeks_for_current_client, reset_client_complete_day_time, \
    add_client_complete_exercise_count, update_client_complete_day_time, get_client_week_by_id, complete_client_week, \
    complete_client_day, create_client_condition, get_client_conditions, get_client_complete_exercise_count, \
    generate_client_weeks_exercises
from .services.mailing_services import send_reset_password_code_message
from .services.user_services import delete_user, get_user, change_user_info, check_user_valid


class ResetClientTimer(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            client = get_client(client_id=request.GET.get('client_id'))
            reset_client_complete_day_time(client)
            return Response('successfully', 200)
        except Exception as ex:
            return Response({'message': f'Error! {str(ex)}'}, 400)


class UserRegistration(APIView):
    permission_classes = [AllowAny]

    @transaction.atomic
    def post(self, request):
        try:
            user, status_code = create_user(
                user_type=json.loads(request.data['user_type']),
                email=json.loads(request.data['email']),
                first_name=json.loads(request.data['first_name']),
                last_name=json.loads(request.data['last_name']),
                password=json.loads(request.data['password']),
                phone=json.loads(request.data['phone']),
                birthday=json.loads(request.data['birthday'])
            )
            if status_code != 200:
                return Response(user, status=status_code)
            first_week_id = None
            try:
                client_setup_settings(
                    user=user,
                    gender=json.loads(request.data['gender']),
                    height=json.loads(request.data['height']),
                    weight=json.loads(request.data['weight']),
                )
                with transaction.atomic():
                    for img in json.loads(request.data['photos']):
                        if img['src']:
                            try:
                                add_client_photo(
                                    client=user,
                                    photo=img['src'],
                                    line_first=img['top_line_first'],
                                    line_second=img['top_line_second']
                                )
                            except:
                                continue
            except Exception as ex:
                return Response(
                    {'message': f'Error! {str(ex)}'}, status=400
                )
        except Exception as ex:
            delete_user(user_id=user.id)
            return Response(
                {'message': f'Error! {str(ex)}'}, status=400
            )
        token = generate_token(user)
        if request.user.is_authenticated:
            return Response({'token': token, 'message': 'User was successfully created'}, 200)


class Logout(APIView):

    def post(self, request):
        delete_token(user=request.user)
        return Response({'message': 'You logged out successfully'}, status=200)


class ChangePassword(APIView):

    def put(self, request):
        try:
            current_password = request.data.get('current_password')
            new_password = request.data.get('new_password')
            if request.user.check_password(current_password):
                if request.user.check_password(new_password):
                    return Response({'message': "Current and new password match"}, status=400)
                token = change_password(user=request.user, password=new_password)
                return Response({'token': token, 'message': 'Password successfully changed'}, status=200)
            return Response({'message': "Wrong current password"}, status=400)
        except Exception as ex:
            return Response({'message': f"Error! {str(ex)}"}, status=400)


# TODO: add to postman and create
class ResetPassword(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            if request.data.get('step') == 1:
                if check_user_valid(email=request.data.get('email')):
                    send_reset_password_code_message(email=request.data.get('email'))
                    return Response({'message': "Message sent in the mail"}, status=200)
                else:
                    return Response({'message': "There is no such user"}, status=200)
            if request.data.get('step') == 2:
                user = get_user_from_reset_password_code(reset_password_code=request.data['reset_password_code'])
                token = change_password(user=user, password=request.data.get('new_password'))
                delete_reset_password_code(reset_password_code=request.data['reset_password_code'])
                return Response({
                    'token': token,
                    'user_status': user.status,
                    'message': 'Password successfully changed'
                }, status=200)
            else:
                return Response({'message': "There is no such step"}, status=400)
        except Exception as ex:
            return Response({'message': f"Error! {str(ex)}"}, status=400)


# TODO: add to postman and create
class CheckValidResetCode(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            if check_reset_password_valid(reset_password_code=request.data['reset_password_code']):
                return Response({'message': "Correct code"}, status=200)
            else:
                return Response({'message': "Non-existent code"}, status=400)
        except Exception as ex:
            return Response({'message': f"Error! {str(ex)}"}, status=400)


class CheckValidEmail(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            if check_user_valid(email=request.data['email']):
                return Response({'message': "email invalid"}, status=200)
            else:
                return Response({'message': "email valid"}, status=200)
        except Exception as ex:
            return Response({'message': f"Error! {str(ex)}"}, status=400)


# TODO: add to postman
class GetTokenFromAuthCode(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        print(request.data['authorization_code'])
        try:
            user = get_user_from_auth_code(authorization_code=request.data['authorization_code'])
            token = generate_token(user)
            return Response({'token': token, 'message': 'User was successfully created'}, 200)
        except Exception as ex:
            return Response({'message': f"Error! {str(ex)}"}, status=400)


# TODO: add to postman
class GetUserInfo(APIView):

    def get(self, request):
        try:
            return Response(ClientSerializer(get_client(request.user.id), context={'request': request}).data)
        except Exception as ex:
            return Response({'message': f"Error! {str(ex)}"}, status=400)


class ChangeClientLastVisit(APIView):

    def post(self, request):
        try:
            client = get_client(request.user.id)
            change_client_last_visit(client=client)
            return Response({'message': "Success"}, status=200)
        except Exception as ex:
            return Response({'message': f"Error! {str(ex)}"}, status=400)


# TODO: add to postman and frontend
class AddClientToArchive(APIView):

    def post(self, request):
        try:
            client = get_client(request.user.id)
            add_client_to_archive(client=client)
            return Response({'message': "Client has been successfully added to the archive"}, status=200)
        except Exception as ex:
            return Response({'message': f"Error! There is no -{str(ex)}"}, status=400)


class AddClientCondition(APIView):

    def post(self, request):
        try:
            client = get_client(request.user.id)
            add_client_condition(
                client=client,
                general_condition_before=request.data['general_condition_before'],
                general_condition_after=request.data['general_condition_after']
            )
            return Response({'message': "Successfully Added feedback on the client's well-being"}, status=200)
        except Exception as ex:
            return Response({'message': f"Error! There is no -{str(ex)}"}, status=400)


class GetClientPhotos(APIView):

    def get(self, request):
        try:
            if request.GET.get('client_id'):
                client = get_client(request.GET.get('client_id'))
            else:
                client = get_client(request.user.id)
            photos = get_client_photos(client=client)
            return Response(ClientPosturePhotosSerializer(photos, many=True, context={'request': request}).data)
        except Exception as ex:
            return Response({'message': f"Error! {str(ex)}"}, status=400)


class AddClientPhoto(APIView):

    def post(self, request):
        try:
            client = get_client(request.user.id)
            add_client_photo(
                client=client,
                left_side_image=request.data['left_side_image'],
                top_side_image=request.data['top_side_image'],
                right_side_image=request.data['right_side_image'],
            )
            return Response({'message': 'Photos successfully added'}, status=200)
        except Exception as ex:
            return Response({'message': f"Error! There is no - {str(ex)}"}, status=400)


class DeleteClientPhoto(APIView):

    def delete(self, request):
        try:
            delete_client_photo(photo_id=request.data['photo_id'])
            return Response({'message': "The client photo was successfully deleted"}, status=200)
        except Exception as ex:
            return Response({'message': f"Error! {str(ex)}"}, status=400)


class ResetAllWeeks(APIView):

    def post(self, request):
        try:
            client = get_client(request.user.id)
            reset_all_weeks_for_current_client(client=client)
            return Response({'message': "Success"}, status=200)
        except Exception as ex:
            return Response({'message': f"Error! {str(ex)}"}, status=400)


class GetClientWeeks(APIView):
    def get(self, request):
        try:
            client = get_client(request.GET.get('client_id'))
            weeks = get_client_week(client=client)

            return Response({
                'weeks': ClientWeekSerializer(weeks, many=True).data,
            }, status=200
            )
        except Exception as ex:
            return Response({'message': f"Error! {str(ex)}"}, status=400)

class GetClientDay(APIView):

    def get(self, request):
        client = get_client(request.GET.get('client_id'))
        day = get_client_day(client=client, week_id=request.GET.get('week_id'))
        return Response(ClientDaySerializer(day, many=True, context={"request": request}).data)


class ChangeUserInfo(APIView):

    @transaction.atomic
    def put(self, request):
        try:
            if request.data.get('first_name') or request.data.get('last_name') or \
                    request.data.get('email') or request.data.get('phone'):
                if request.data.get('user_id'):
                    user_for_change = get_user(user_id=request.data.get('user_id'))
                else:
                    user_for_change = request.user
                change_user_info(
                    user=user_for_change,
                    first_name=request.data.get('first_name'),
                    last_name=request.data.get('last_name'),
                    email=request.data.get('email'),
                    phone=request.data.get('phone'),
                    is_first_login=request.data.get('is_first_login')
                )
                return Response(ClientSerializer(get_client(request.user.id), context={'request': request}).data)
            else:
                return Response({'message': "You are transmitting empty data"}, status=400)
        except Exception as ex:
            return Response({'message': f"Error! {str(ex)}"}, status=400)


class GetClient(APIView):

    def get(self, request):
        try:
            client = get_client(request.GET.get('client_id'))
            return Response(ClientSerializer(client, context={'request': request}).data, status=200)
        except Exception as ex:
            return Response({'message': f"Error! {str(ex)}"}, status=400)


class DeleteClientDay(APIView):

    @transaction.atomic
    def delete(self, request):
        try:
            delete_client_day(day_id=request.data.get('day_id'))
            return Response({'message': "The client day was successfully deleted"}, status=200)
        except Exception as ex:
            return Response({'message': f"Error! {str(ex)}"}, status=400)


class PreviousClientDay(APIView):
    def post(self, request):
        try:
            previous_client_day(
                day_id=request.data.get('day_id'),
                is_repeat=request.data.get('is_repeat')
            )
            return Response({'message': "Success!"}, status=200)
        except Exception as ex:
            return Response({'message': f"Error! {str(ex)}"}, status=400)


class UpdateClientWeek(APIView):
    @transaction.atomic
    def put(self, request):
        try:
            week = json.loads(request.data['week'])
            update_client_week(
                week_id=week['id'],
                description=week['description'],
                name=week['name'],
                open_for_client=week['is_available_for_client']
            )
            return Response({'message': "The data of the week has been successfully updated"}, status=200)
        except Exception as ex:
            return Response({'message': f"Error! {str(ex)}"}, status=400)

# class CompleteClientDay(APIView):
#     @transaction.atomic
#     def post(self, request):
#         try:
#             client = get_client(request.GET.get('client_id'))
#             print(request.data.get('is_additional'))
#             complete_client_day(
#                 day_id=request.data.get('day_id'),
#                 is_repeat=request.data.get('is_repeat')
#             )
#             if request.data.get('complete'):
#                 print(request.data.get('is_repeat'))
#                 complete_client_week(
#                     week_id=request.data.get('week_id'),
#                     client=client,
#                     is_repeat=request.data.get('is_repeat')
#                 )
#                 if get_client_week_by_id(request.data.get('week_id')).complete_count < 7:
#                     update_client_complete_day_time(client)
#
#             add_client_complete_exercise_count(client=client)
#
#             return Response({'message': "You have successfully completed the exercise"}, status=200)
#         except Exception as ex:
#             return Response({'message': f"Error! {str(ex)}"}, status=400)


class CompleteClientDay(APIView):
    @transaction.atomic
    def post(self, request):
        try:
            client = get_client(request.GET.get('client_id'))
            complete_client_week(
                week_id=request.data.get('week_id'),
                client=client,
                is_repeat=request.data.get('is_repeat')
            )
            if get_client_week_by_id(request.data.get('week_id')).complete_count < 7:
                update_client_complete_day_time(client)

            add_client_complete_exercise_count(client=client)

            return Response({'message': "You have successfully completed the exercise"}, status=200)
        except Exception as ex:
            return Response({'message': f"Error! {str(ex)}"}, status=400)

class SetClientStatistics(APIView):

    @transaction.atomic
    def post(self, request):
        try:
            client = get_client(request.GET.get('client_id'))
            create_client_condition(
                client=client,
                general_condition_before=request.data.get('general_condition_before'),
                general_condition_after=request.data.get('general_condition_after'),
            )
            return Response({'message': "Feedback on feeling was successfully added to the statistics"}, status=200)
        except Exception as ex:
            return Response({'message': f"Error! {str(ex)}"}, status=400)

class GetClientStatistics(APIView):

    def get(self, request):
        try:
            client = get_client(request.GET.get('client_id'))
            condition = get_client_conditions(client=client)
            complete_exercise = get_client_complete_exercise_count(client=client)
            return Response(
                {'condition': ClientConditionSerializer(condition, many=True).data,
                 'complete_exercise': ClientCompleteExerciseCountSerializer(complete_exercise, many=True).data})
        except Exception as ex:
            return Response({'message': f"Error! There is no - {str(ex)}"}, status=400)

class ClientAccountSetup(APIView):

    def post(self, request):
        try:
            print(request.data.get('type_front'))
            print(request.data.get('type_back'))
            print(1)
            client = get_client(request.user.id)
            print(2)
            client.posture_side = request.data.get('type_front')
            client.posture_back = request.data.get('type_back')
            print(3)
            client.save()
            generate_client_weeks_exercises(client_id=request.user.id)
            return Response("Success")
        except Exception as ex:
            return Response({'message': f"Error! {str(ex)}"}, status=400)