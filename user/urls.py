from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from .views import UserRegistration, Logout, AddClientCondition, AddClientPhoto, \
    ChangePassword, ChangeUserInfo, GetClient, DeleteClientPhoto, \
    GetClientPhotos, UpdateClientWeek, GetUserInfo, GetClientWeeks, GetClientDay, DeleteClientDay, CheckValidEmail, \
    GetTokenFromAuthCode, ResetPassword, CheckValidResetCode, AddClientToArchive, PreviousClientDay, \
    ChangeClientLastVisit, \
    ResetAllWeeks, ResetClientTimer, CompleteClientDay, SetClientStatistics, GetClientStatistics, ClientAccountSetup

urlpatterns = [

    path('login/', obtain_auth_token, name='login'),
    path('registration/', UserRegistration.as_view(), name='registration'),
    path('logout/', Logout.as_view(), name='logout'),
    path('me/', GetUserInfo.as_view(), name='me'),
    path('change-password/', ChangePassword.as_view(), name='change_password'),
    path('reset-password/', ResetPassword().as_view(), name='reset_password'),
    path('check-valid-reset-code/', CheckValidResetCode.as_view(), name='check_valid_reset_code'),
    path('check-valid-email/', CheckValidEmail.as_view(), name='check_valid_email'),
    path('token-from-auth-code/', GetTokenFromAuthCode().as_view(), name='token_from_auth_code'),

    path('add-client-to-archive/', AddClientToArchive.as_view(), name='add_client_to_archive'),
    path('change-client-last-visit/', ChangeClientLastVisit.as_view(), name='change_client_last_visit'),
    path('reset-all-weeks/', ResetAllWeeks.as_view(), name='reset_all_weeks'),
    path('add-client-condition/', AddClientCondition.as_view(), name='add_client_condition'),
    path('add-client-photo/', AddClientPhoto.as_view(), name='add_client_photo'),

    path('complete-client-day/', CompleteClientDay.as_view(), name='complete_client_day'),
    path('previous-client-day/', PreviousClientDay.as_view(), name='previous_client_day'),
    path('set-client-statistics/', SetClientStatistics.as_view(), name='set_client_statistics'),

    path('delete-client-photo/', DeleteClientPhoto.as_view(), name='delete_client_photo'),
    path('delete-client-day/', DeleteClientDay.as_view(), name='delete_client_day'),

    path('change-user-info/', ChangeUserInfo.as_view(), name='change_user_info'),
    path('update-client-week/', UpdateClientWeek.as_view(), name='update_client_week'),

    path('get-client/', GetClient.as_view(), name='get_client'),
    path('get-client-photos/', GetClientPhotos.as_view(), name='get_client_photos'),
    path('get-client-weeks/', GetClientWeeks.as_view(), name='get_client_weeks'),
    path('get-client-statistics/', GetClientStatistics.as_view(), name='get_client_statistics'),
    path('get-client-day/', GetClientDay.as_view(), name='get_client_day'),

    path('reset-client-timer/', ResetClientTimer.as_view(), name='reset_client_timer'),
    path('client-setup/', ClientAccountSetup.as_view(), name='client_setup'),
]
