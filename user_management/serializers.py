from rest_framework import serializers
from user_management.models import *


class RolePermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RolePermission
        fields = '__all__'
  
class UserTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserToken
        fields = '__all__'
        
class UserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'

class UserTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserToken
        fields = '__all__' 
    
class UserLoginDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'Id',
            'TenantId',
            'UserName',
            'Email',
            'FirstName',
            'LastName',
            'EmailConfirmed',
            'PhoneNo',
            'PhoneNoConfirmed',
            'LockoutEnd',
            'LockoutEnabled',
            'AccessFailedCount',
            'RoleId',
            'BranchId',
            'TerritoryId',
            'CreatedDate',
            'CreatedBy',
            'UpdatedDate',
            'UpdatedBy',
            'IPAddress',
            'Status',
        )

class UserLogin(serializers.ModelSerializer):
    UserTokenDetails = UserTokenSerializer()
    class Meta:
        model = User
        fields = (
            'Id',
            'TenantId',
            'UserName',
            'Email',
            'FirstName',
            'LastName',
            'EmailConfirmed',
            'PhoneNo',
            'PhoneNoConfirmed',
            'LockoutEnd',
            'LockoutEnabled',
            'AccessFailedCount',
            'RoleId',
            'BranchId',
            'TerritoryId',
            'CreatedDate',
            'CreatedBy',
            'UpdatedDate',
            'UpdatedBy',
            'IPAddress',
            'Status',
            'UserTokenDetails',
        )