from drf_yasg import openapi
from django.http.response import *
from scm_app.models import *
from scm_app.serializers import *
from user_management.serializers import *
from django.forms.models import model_to_dict


single_job_response = openapi.Response('JobSchedulerData', JobSchedulerSerializer)
multiple_job_response = openapi.Response('JobSchedulerData',JobSchedulerSerializer(many=True))
tenant_id_query_param = openapi.Parameter('tenant_id',openapi.IN_QUERY,type=openapi.TYPE_STRING)
bu_id_query_param = openapi.Parameter('bu_id',openapi.IN_QUERY,type=openapi.TYPE_STRING)
channel_id_query_param = openapi.Parameter('channel_id',openapi.IN_QUERY,type=openapi.TYPE_STRING)
division_id_query_param = openapi.Parameter('division_id',openapi.IN_QUERY,type=openapi.TYPE_STRING)
category_id_query_param = openapi.Parameter('category_id',openapi.IN_QUERY,type=openapi.TYPE_STRING)
brand_id_query_param = openapi.Parameter('brand_id',openapi.IN_QUERY,type=openapi.TYPE_STRING)
search_query_param = openapi.Parameter('search',openapi.IN_QUERY,type=openapi.TYPE_STRING,description='Search by name')
search_bu_name_query_param = openapi.Parameter('search',openapi.IN_QUERY,type=openapi.TYPE_STRING,description='Search by business name')
branch_id_query_param = openapi.Parameter('branch_id',openapi.IN_QUERY,type=openapi.TYPE_STRING)
sku_snp_id_query_param = openapi.Parameter('sku_snp_id',openapi.IN_QUERY,type=openapi.TYPE_STRING)
branch_sku_id_query_param = openapi.Parameter('branch_sku_id',openapi.IN_QUERY,type=openapi.TYPE_STRING)
search_query_param = openapi.Parameter('search',openapi.IN_QUERY,type=openapi.TYPE_STRING,description='Search by name')
from_date_query_param = openapi.Parameter('from_date',openapi.IN_QUERY,type=openapi.FORMAT_DATE, description='Date format "YYYY-MM-DD" e.g., 2022-12-27')
to_date_query_param = openapi.Parameter('to_date',openapi.IN_QUERY,type=openapi.FORMAT_DATE)
job_name_query_param = openapi.Parameter('job_name',openapi.IN_QUERY,type=openapi.TYPE_STRING,enum=['MSL Planning', 'MSL Reporting', 'Replenishment Planning', 'Replenishment Reporting', 'DOS Calculation', 'PP Planning'])
user_type_query_param = openapi.Parameter('user_type',openapi.IN_QUERY,type=openapi.TYPE_STRING,enum=['PP', 'RP'])
job_frequency_query_param = openapi.Parameter('job_frequency',openapi.IN_QUERY,type=openapi.TYPE_STRING,enum=['YEARLY', 'MONTHLY', 'WEEKLY', 'DAILY', 'HOURLY'])
rp_rule_id_query_param = openapi.Parameter('rp_rule_id',openapi.IN_QUERY,type=openapi.TYPE_STRING)

scheduler_payload = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
                "TenantId": openapi.Schema(type=openapi.TYPE_INTEGER),
                "Name": openapi.Schema(type=openapi.TYPE_STRING,enum=['MSL Planning', 'MSL Reporting', 'Replenishment Planning', 'Replenishment Reporting', 'DOS Calculation', 'PP Planning']),
                "Frequency": openapi.Schema(type=openapi.TYPE_STRING),
                "DateTime": openapi.Schema(type=openapi.TYPE_STRING),
                "Status": openapi.Schema(type=openapi.TYPE_STRING),
                "UserType": openapi.Schema(type=openapi.TYPE_STRING,enum=['PP', 'RP']),
                "UpdatedBy": openapi.Schema(type=openapi.TYPE_STRING),
                "CreatedBy": openapi.Schema(type=openapi.TYPE_STRING),
                "IPAddress": openapi.Schema(type=openapi.TYPE_STRING),
        },)

scheduler_update_payload = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
                "Name": openapi.Schema(type=openapi.TYPE_STRING,enum=['MSL Planning', 'MSL Reporting', 'Replenishment Planning', 'Replenishment Reporting', 'DOS Calculation', 'PP Planning']),
                "Frequency": openapi.Schema(type=openapi.TYPE_STRING),
                "Status": openapi.Schema(type=openapi.TYPE_STRING),
                "DateTime": openapi.Schema(type=openapi.TYPE_STRING),
                "UserType": openapi.Schema(type=openapi.TYPE_STRING,enum=['PP', 'RP']),
                "UpdatedBy": openapi.Schema(type=openapi.TYPE_STRING),
                "CreatedBy": openapi.Schema(type=openapi.TYPE_STRING),
                "IPAddress": openapi.Schema(type=openapi.TYPE_STRING),
        },)

payload_for_job = {
                "TenantId": openapi.Schema(type=openapi.TYPE_INTEGER),
                "Name": openapi.Schema(type=openapi.TYPE_STRING),
                "Frequency": openapi.Schema(type=openapi.TYPE_STRING),
                "DateTime": openapi.Schema(type=openapi.TYPE_STRING),
                "Status": openapi.Schema(type=openapi.TYPE_STRING),
                "UserType": openapi.Schema(type=openapi.TYPE_STRING),
                "UpdatedBy": openapi.Schema(type=openapi.TYPE_STRING),
                "CreatedBy": openapi.Schema(type=openapi.TYPE_STRING),
                "IPAddress": openapi.Schema(type=openapi.TYPE_STRING),
        }

user_login_payload = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
                "username": openapi.Schema(type=openapi.TYPE_STRING),
                "password": openapi.Schema(type=openapi.TYPE_STRING)
        },)
user_login_response = openapi.Response('user-data', UserLogin)

payload_for_bu = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
                "TenantId": openapi.Schema(type=openapi.TYPE_INTEGER),
                "Code": openapi.Schema(type=openapi.TYPE_STRING),
                "Name": openapi.Schema(type=openapi.TYPE_STRING),
                "Description": openapi.Schema(type=openapi.TYPE_STRING),
                "IPAddress": openapi.Schema(type=openapi.TYPE_STRING),
                "channelID": openapi.Schema(type=openapi.TYPE_INTEGER),
                "Status": openapi.Schema(type=openapi.TYPE_INTEGER,default=1)
        },)

payload_for_master = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
                "TenantId": openapi.Schema(type=openapi.TYPE_INTEGER),
                "Code": openapi.Schema(type=openapi.TYPE_STRING),
                "Name": openapi.Schema(type=openapi.TYPE_STRING),
                "Description": openapi.Schema(type=openapi.TYPE_STRING),
                "IPAddress": openapi.Schema(type=openapi.TYPE_STRING),
                "Status": openapi.Schema(type=openapi.TYPE_INTEGER,default=1)
        },)
payload_for_brand = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
                "Id": openapi.Schema(type=openapi.TYPE_INTEGER),
                "TenantId": openapi.Schema(type=openapi.TYPE_INTEGER),
                "Code": openapi.Schema(type=openapi.TYPE_STRING),
                "Name": openapi.Schema(type=openapi.TYPE_STRING),
                "Description": openapi.Schema(type=openapi.TYPE_STRING),
                "IPAddress": openapi.Schema(type=openapi.TYPE_STRING),
                "Status": openapi.Schema(type=openapi.TYPE_INTEGER,default=1),
                "CreatedBy": openapi.Schema(type=openapi.TYPE_STRING),
                "UpdatedBy": openapi.Schema(type=openapi.TYPE_STRING)

        },)
payload_for_branch = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
                "Id": openapi.Schema(type=openapi.TYPE_INTEGER),
                "TenantId": openapi.Schema(type=openapi.TYPE_INTEGER),
                "Code": openapi.Schema(type=openapi.TYPE_STRING),
                "Name": openapi.Schema(type=openapi.TYPE_STRING),
                "BUId":openapi.Schema(type=openapi.TYPE_INTEGER),
                "channelID":openapi.Schema(type=openapi.TYPE_INTEGER),
                "Description": openapi.Schema(type=openapi.TYPE_STRING),
                "BranchType": openapi.Schema(type=openapi.TYPE_STRING),
                "TotalVolume": openapi.Schema(type=openapi.TYPE_STRING),
                "OperationHours": openapi.Schema(type=openapi.TYPE_STRING),
                "OperatingDaysoftheWeek": openapi.Schema(type=openapi.TYPE_STRING),
                "Operating_times": openapi.Schema(type=openapi.TYPE_STRING),
                "LoadingTimes": openapi.Schema(type=openapi.TYPE_STRING),
                "UnloadingTimes": openapi.Schema(type=openapi.TYPE_STRING),
                "CreatedDate": openapi.Schema(type=openapi.TYPE_STRING),
                "IPAddress": openapi.Schema(type=openapi.TYPE_STRING),
                "Status": openapi.Schema(type=openapi.TYPE_INTEGER,default=1),
                "CreatedBy": openapi.Schema(type=openapi.TYPE_STRING),
                "UpdatedBy": openapi.Schema(type=openapi.TYPE_STRING)

        },)

payload_for_sku_snp = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
                "Id": openapi.Schema(type=openapi.TYPE_INTEGER),
                "TenantId": openapi.Schema(type=openapi.TYPE_INTEGER),
                "BUId":openapi.Schema(type=openapi.TYPE_INTEGER),
                "Code": openapi.Schema(type=openapi.TYPE_STRING),
                "Name": openapi.Schema(type=openapi.TYPE_STRING),
                "Description": openapi.Schema(type=openapi.TYPE_STRING),
                "UOM":openapi.Schema(type=openapi.TYPE_STRING),
                "CategoryId": openapi.Schema(type=openapi.TYPE_INTEGER),
                "DivisionId":openapi.Schema(type=openapi.TYPE_INTEGER),
                "Brand":openapi.Schema(type=openapi.TYPE_INTEGER),
                "LeadTime": openapi.Schema(type=openapi.TYPE_STRING),
                "CreatedBy": openapi.Schema(type=openapi.TYPE_STRING),
                "Status":openapi.Schema(type=openapi.TYPE_INTEGER),
                "IPAddress": openapi.Schema(type=openapi.TYPE_STRING),
                },)


                

success_responses_message = openapi.Response("success response",openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
                "message": openapi.Schema(type=openapi.TYPE_STRING)
        }))

error_response = openapi.Response("error response",openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
                "error": openapi.Schema(type=(openapi.TYPE_OBJECT)),
                "error_message": openapi.Schema(type=(openapi.TYPE_STRING)),
                "status": openapi.Schema(type=(openapi.TYPE_STRING))
        }))

error_responses={
        401: error_response,
        404: error_response,
        500: error_response,
        }

payload_for_rp_rule = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
                "BU": openapi.Schema(type=openapi.TYPE_INTEGER),
                "ConsiderMTO":openapi.Schema(type=openapi.TYPE_BOOLEAN),
                "MTO_RP_Rules": openapi.Schema(type=openapi.TYPE_STRING,enum=["Safety stock Gap -> MSL Gap -> Forecast Gap","MSL Gap -> Sales Order Gap / Shortage -> Forecast Gap","Stock Out Gap -> MSL Gap -> Order Gap ->Forecast Gap"]),
                "STO_RP_Rules": openapi.Schema(type=openapi.TYPE_STRING,enum=["Safety stock Gap -> MSL Gap -> Forecast Gap","MSL Gap -> Sales Order Gap / Shortage -> Forecast Gap","Stock Out Gap -> MSL Gap -> Order Gap ->Forecast Gap"]),
                "ForecastType": openapi.Schema(type=openapi.TYPE_STRING,enum=["Operational Forecast","Final Forecast"]),
                "IPAddress": openapi.Schema(type=openapi.TYPE_STRING),
},)