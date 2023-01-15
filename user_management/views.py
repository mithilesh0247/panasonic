from rest_framework.response import Response
from rest_framework.views import APIView
from user_management.models import *
from user_management.serializers import *
from rest_framework_simplejwt.tokens import AccessToken
from datetime import datetime, timedelta
from rest_framework.decorators import action
from scm_app.swagger_models import *
from drf_yasg.utils import swagger_auto_schema
# Create your views here.
class UserLoginView(APIView):
    
    @swagger_auto_schema(method='post',request_body=user_login_payload, responses=({201:user_login_response,**error_responses} ))
    @action(methods=['POST'],detail='user login')
    def post(self, request, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        if not username or not password:
            return Response({"error":{},"error_message":"username/password can't be empty","status":"NOT_FOUND_ERR"},status=404)
        try:
            user_obj = User.objects.get(UserName=username,Password=password)
            user_data = UserLoginDetailsSerializer(user_obj) 
            user_data = user_data.data
            access_token = AccessToken.for_user(user_obj)
            access_token.payload["user_details"] = user_data
            role_id = user_data.get('RoleId')
            try:
                user_data['RolePermissionDetails'] = (RolePermissionSerializer(RolePermission.objects.get(RoleId=role_id))).data
            except RolePermission.DoesNotExist:
                user_data['RolePermissionDetails'] = {} 
            data = {
                        "Token": str(access_token),
                        "UserId"        : user_data.get('Id'),
                        "ExpiryDate"    : str((datetime.now()+timedelta(days=28)).strftime("%Y-%m-%d")),
                        "CreatedBy"     : user_data.get('CreatedBy'),
                        "Status"        : 1,
                    }         
            token_data = UserToken
            try:
                check_user_token = UserToken.objects.get(UserId=user_data.get('Id'))
                user_token_srl = UserTokenSerializer(instance=check_user_token,data=data,partial=True)
                if user_token_srl.is_valid(raise_exception=True):
                    user_token_srl.save()
                    token_data = user_token_srl
            except UserToken.DoesNotExist:
                token_data = UserTokenSerializer(data=data,many=False)
                if token_data.is_valid(raise_exception=True):
                    token_data.save()
                else:
                    return Response({"error":{token_data.errors},"error_message":"invalid data found for UserToken","status":"INTERNAL_SERVER_ERR"},status=500)            
            user_data['UserTokenDetails'] = token_data.data
            return Response(user_data,status=200)
        except User.DoesNotExist:
            return Response({"error":{},"error_message":"invalid username/password","status":"UNAUTHORIZED_ERR"},status=404)
        except Exception as e:
            if not (isinstance(e,dict)):
                e = {"exception": str(e)}
            return Response({"error":e,"error_message":"some unexpected error ocurred","status":"INTERNAL_SERVER_ERR"},status=500)
        
        
            