from rest_framework.views import APIView
from rest_framework.response import Response
from scm.celery import app
from scm_app.models import MSL_report
from . utils import mslReport
from  .utils import query_set_for_filter
# from scm_app.task import add
from django_celery_beat.models import  PeriodicTask, CrontabSchedule
from celery.schedules import crontab
from rest_framework.decorators import action
from drf_yasg.utils import swagger_auto_schema
from  .utils import mslReport
from scm_app.models import *
from scm_app.serializers import *
from .swagger_models import *
from .tasks import test_func
from utilities.splitter import splitter
import pandas as pd
from django.http import HttpResponse, JsonResponse
from rest_framework.pagination import PageNumberPagination#,Paginator
from scm_app.pagination import PaginationHandlerMixin
# from django_filters.rest_framework import DjangoFilterBackend
# Create your views here.

class BasicPagination(PageNumberPagination):
    page_size_query_param = 'limit'

class MSLReports(APIView,PaginationHandlerMixin):
    pagination_class = BasicPagination
    serializer_class = MSLSerializer
    def get(self, *args, **kwargs):
        jobId = self.request.GET.get('jobId',None)
        if jobId:
            msl = MSL_report.objects.filter(JobId__Id=jobId).order_by('-Id')
        else:
            msl = MSL_report.objects.all().order_by('-Id')
        page = self.paginate_queryset(msl)
        if page is not None:
            serializer = self.get_paginated_response(self.serializer_class(page,
                        many=True).data)
        else:
            serializer = self.serializer_class(msl, many=True)
        return self.get_paginated_response(serializer.data) # <- here it is

    def post(self, *args, **kwargs):
        msl = mslReport()
        return Response({"MSL":msl})

    def patch(self, *args, **kwargs):
        mslId = self.request.GET.get("mslId",None)
        final_msl_value = self.request.GET.get("FinalMSL",None)
        #have to work for patch
        if mslId and final_msl_value :
            msl = MSL_report.objects.get(Id=mslId)
            serializer=self.serializer_class(msl,data=self.request.GET,partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)

        page = self.paginate_queryset(msl)
        if page is not None:
            serializer = self.get_paginated_response(self.serializer_class(page,
                        many=True).data)
        else:
            serializer = self.serializer_class(msl, many=True)
        return self.get_paginated_response(serializer.data) # <- here it is

    def delete(self, *args, **kwargs):
        MSL_report.objects.all().delete()
        return JsonResponse({"messgae": "Execusted Succesfully"})

# def checkcelery(request):
#     res=add.delay()
#     return Response({"RES":res})

class scheduler(APIView):
    serializer_class=CronSerializer
    def get(self, *args, **kwargs):
        periodic_schedule = PeriodicTask.objects.all().values()
        # cronSchedule = CrontabSchedule.objects.all().values()
        return Response({"periodic_schedule":periodic_schedule,"cronSchedule":"cronSchedule"})
    
    def post(self, *args, **kwargs):
        crontabId = self.request.POST.get('crontabId',None)
        minutes = self.request.POST.get('minutes',"*")
        hour = self.request.POST.get('hour',"*")
        day_of_week = self.request.POST.get('day_of_week',"*")
        day_of_month = self.request.POST.get('day_of_month',"*")
        month_of_year = self.request.POST.get('month_of_year',"*")

        #=========================================================
        app.conf.beat_schedule = {
        # Executes every Monday morning at 7:30 a.m.
        'scm_app.task.mslReportGeneration': {
            'task': 'scm_app.task.mslReportGeneration',
            'schedule': crontab(minute=1),
            # 'args': (16, 16),
        },
        }
        # schedule, _ = CrontabSchedule.objects.get_or_create(minute='*/1')
        # task = PeriodicTask.objects.create(name='mslReportGeneration',
        #     task='scm_app.task.mslReportGeneration',
        #     crontab=schedule)
        #=========================================================
        scheduled_time, _ = CrontabSchedule.objects.get_or_create(
            minute=minutes, hour=hour, day_of_week=day_of_week, day_of_month=day_of_month, month_of_year=month_of_year,
        )
        
        print(scheduled_time,"===== ",minutes,hour,day_of_week,day_of_month,month_of_year)
        PeriodicTask.objects.update_or_create(
            task="scm_app.task.mslReportGeneration",
            name="scm_app.task.mslReportGeneration",
            defaults=dict(
                crontab=scheduled_time,
                expire_seconds=7200,
            ),
        )
        #to schdule in beat
       
        return Response({"scheduled_task":"Scheduled!"})

class JobSchedulerPostV1(APIView):
   
    @swagger_auto_schema(method='post',request_body=scheduler_payload, responses=({201:single_job_response,**error_responses} ))
    @action(methods=['POST'],detail='create new job scheduler')
    def post(self, request, *args, **kwargs):
        '''
        This endpoint is used to add a new job scheduler for all possible cron expressions.
        Expression must be putted correctly in `DateTime` field in request body.
        Possible values:
            `Name`: ('MSL Planning', 'MSL Reporting', 'Replenishment Planning', 'Replenishment Reporting', 'DOS Calculation', 'PP Planning'),
            `Frequency`: ('YEARLY', 'MONTHLY', 'WEEKLY', 'DAILY', 'HOURLY'),
            `UserType`: ('PP','RP'),
            `Status`: (0, 1),
            `DateTime`: any cron expression splitted by proper whitespace e.g. ('* 5 * * *', '0 15 10 * MON,WED,FRI', ...)
        '''    
        serializer=JobSchedulerSerializer(data=self.request.data)
        if serializer.is_valid():
            serializer.save()
            
            try:
                possibleExpressions = splitter(self.request.data.get('DateTime'))
                if isinstance(possibleExpressions,list):
                    data = []
                    for exp in possibleExpressions:
                        data.append({
                        "DateTime": ' '.join(exp),
                        "UpdatedBy":self.request.data.get('UpdatedBy') ,
                        "IPAddress":self.request.data.get('IPAddress') ,
                        "JobSchedulerId":serializer.data.get('Id') ,
                        "CreatedBy":self.request.data.get('CreatedBy') 
                    }
                        )
                else:
                    data={
                        "DateTime":possibleExpressions,
                        "UpdatedBy":self.request.data.get('UpdatedBy') ,
                        "IPAddress":self.request.data.get('IPAddress') ,
                        "JobSchedulerId":serializer.data.get('Id') ,
                        "CreatedBy":self.request.data.get('CreatedBy') 
                    }
                job = JobScheduler.objects.get(Id=serializer.data.get('Id'))
            except JobScheduler.DoesNotExist:
                return Response({"error":{},"error_message":"job not found","status":"NOT_FOUND_ERR"},status=404)
            except Exception as e:
                if not isinstance(e,dict):
                    e=str(e)
                return Response({"error": e,"error_message":"some unexpected error ocurred","status":"INTERNAL_SERVER_ERR"},status=500)
            
            sDetails = JobSchedulerDetailsSerializer(data=data,many=(isinstance(possibleExpressions,list)))
            
            if sDetails.is_valid():
                sDetails.save()
                serializerData = serializer.data
                serializerData['JobDetails'] = [data]
                createDataFrameObject(None)
                return Response({"message":"job created","data":serializerData},status=201)
            else:
                job.delete()
                return Response({"error":sDetails.errors, "error_message":"error ocurred while saving job details","status":"INTERNAL_SERVER_ERR"},status=500)
        else:
            return Response({"error":serializer.errors, "error_message":"error ocurred while saving job","status":"INTERNAL_SERVER_ERR"},status=500)
    
    
    @swagger_auto_schema(method='get', manual_parameters=[tenant_id_query_param,job_name_query_param,user_type_query_param,job_frequency_query_param],responses=({200: multiple_job_response, **error_responses}))
    @action(methods=['GET'],detail='get all available schedulers with their respective detailed data')
    def get(self, request, *args, **kwargs):
        '''
        This endpoint is to get all job scheduler array with detailed expression for all tenant.
        You can also provide `tenant_id` as query parameter to get data for specific tenant.
        '''
        try:
            tenant_id = self.request.GET.get('tenant_id',None)
            job_name = self.request.GET.get('job_name',None)
            user_type = self.request.GET.get('user_type',None)
            job_frequency = self.request.GET.get('job_frequency',None)
            no_filter = True
            job = JobScheduler.objects
            if tenant_id:
                job = job.filter(TenantId=tenant_id)
                no_filter = False
            if job_name:
                job = job.filter(Name=job_name)
                no_filter = False
            if job_frequency:
                job = job.filter(Frequency=job_frequency)
                no_filter = False
            if user_type:
                job = job.filter(UserType=user_type)
                no_filter = False
            if no_filter:
                job = job.all()
                
        except JobScheduler.DoesNotExist:
            return Response({"error":{},"error_message":"jobs not found","status":"NOT_FOUND_ERR"},status=404)
        except Exception as e:
            if not isinstance(e,dict):
                e=str(e)
            return Response({"error": e,"error_message":"some unexpected error ocurred","status":"INTERNAL_SERVER_ERR"},status=500)
        serializer = JobSchedulerSerializer(job,many=True)
        return Response(serializer.data,status=200)


class JobSchedulerV1(APIView):
    
    @swagger_auto_schema(method='GET', responses=({200: single_job_response,**error_responses}))
    @action(methods=['GET'],detail='get job scheduler according to job_id with their respective detailed data')
    def get(self, request, job_id):
        '''
        This endpoint is to get specific job scheduler with detailed expression by providing job_id in path/url parameter
        '''
        try:
            job = JobScheduler.objects.get(Id=job_id)
        except JobScheduler.DoesNotExist:
            return Response({"error":{},"error_message":"job not found","status":"NOT_FOUND_ERR"},status=404)
        except Exception as e:
            if not isinstance(e,dict):
                e=str(e)
            return Response({"error": e,"error_message":"some unexpected error ocurred","status":"INTERNAL_SERVER_ERR"},status=500)
        serializer = JobSchedulerSerializer(job)
        return Response({"data":serializer.data})


    @swagger_auto_schema(method='PATCH', request_body=scheduler_update_payload, responses=({200:success_responses_message, **error_responses}))
    @action(methods=['PATCH'],detail='update job scheduler according to job_id with their respective detailed data ("except `datetime` string")')
    def patch(self, request, job_id):
        '''
        This endpoint is used to partially update a job scheduler using job_id in path/url parameter.
        You can only update fields available in request-body.
        Possible values:
            `Name`: ('MSL Planning', 'MSL Reporting', 'Replenishment Planning', 'Replenishment Reporting', 'DOS Calculation', 'PP Planning'),
            `Frequency`: ('YEARLY', 'MONTHLY', 'WEEKLY', 'DAILY', 'HOURLY'),
            `UserType`: ('PP','RP'),
            `Status`: (0, 1),
        '''
        try:
            try:
                job = JobScheduler.objects.get(Id=job_id)            
            except JobScheduler.DoesNotExist:
                return Response({"error":{},"error_message":"job or their respective details not found","status":"NOT_FOUND_ERR"},status=404)
            except Exception as e:
                if not isinstance(e,dict):
                    e=str(e)
                return Response({"error": e,"error_message":"some unexpected error ocurred","status":"INTERNAL_SERVER_ERR"},status=500)

            validated_data = self.request.data

            property_payload = {}
            property_payload_for_job_details = {}

            if validated_data.get('UpdatedBy', None) :
                property_payload['UpdatedBy'] = validated_data.get('UpdatedBy',job.UpdatedBy)
                property_payload_for_job_details['UpdatedBy'] = validated_data.get('UpdatedBy',job.UpdatedBy)

            if validated_data.get('IPAddress', None) :
                property_payload['IPAddress'] = validated_data.get('IPAddress',job.IPAddress)
                property_payload_for_job_details['IPAddress'] = validated_data.get('IPAddress',job.IPAddress)

            if job.CreatedBy :
                property_payload_for_job_details['CreatedBy'] = job.CreatedBy

            if validated_data.get('Name',None):
                property_payload['Name'] = validated_data.get('Name',job.Name)

            if validated_data.get('Frequency',None):
                property_payload['Frequency'] = validated_data.get('Frequency',job.Frequency)

            if validated_data.get('Status',None):
                property_payload['Status'] = validated_data.get('Status',job.Status)                

            if validated_data.get('UserType',None):
                property_payload['UserType'] = validated_data.get('UserType',job.UserType)

            try:
                jobDetail = JobSchedulerDetails.objects.filter(JobSchedulerId=job.Id)  
            except JobSchedulerDetails.DoesNotExist:
                return Response({"error":{},"error_message":"job details not found","status":"NOT_FOUND_ERR"},status=404)
            
            data = []
            if validated_data.get('DateTime',None):
                property_payload['DateTime'] = validated_data.get('DateTime',job.DateTime)
                print(jobDetail.delete())
                
                possibleExpressions = splitter(self.request.data.get('DateTime'))
                if isinstance(possibleExpressions,list):
                    for exp in possibleExpressions:
                        data.append({'DateTime': (' '.join(exp)), 'JobSchedulerId': job_id,**property_payload_for_job_details})
                else:
                    data.append({'DateTime': validated_data.get('DateTime',job.DateTime),  'JobSchedulerId': job_id, **property_payload_for_job_details})
            property_serializer = JobSchedulerSerializer(instance=job, data=property_payload, partial=True)
            if property_serializer.is_valid():
                property_serializer.save()

                if isinstance(data,list) and len(data)>0:
                    property_serializer_for_details = JobSchedulerDetailsSerializer(data=data, many=True)
                    if property_serializer_for_details.is_valid(raise_exception=True):
                        property_serializer_for_details.save()
                    else:
                        return Response({"error": property_serializer_for_details.errors,"error_message":"unable to update job details", "status":"INTERNAL_SERVER_ERR"},status=500)
                else:
                    for detailsObject in jobDetail:
                        property_serializer_for_details = JobSchedulerDetailsSerializer(instance=detailsObject, data=property_payload_for_job_details, partial=True)
                        if property_serializer_for_details.is_valid(raise_exception=True):
                            property_serializer_for_details.save()
                        else:
                            return Response({"error": property_serializer_for_details.errors,"error_message":"unable to update job details", "status":"INTERNAL_SERVER_ERR"},status=500)
                createDataFrameObject(None)
                return Response({"message":"job updated"},status=200)
            else:
                return Response({"error": property_serializer.errors,"error_message":"unable to update job details", "status": "INTERNAL_SERVER_ERR"},status=500)
        except Exception as e:
            if not isinstance(e,dict):
                e=str(e)
            return Response({"error": e,"error_message":"some unexpected error ocurred","status":"INTERNAL_SERVER_ERR"},status=500)

                
            
    @swagger_auto_schema(method='DELETE',responses=({200:success_responses_message, **error_responses}))
    @action(methods=['DELETE'],detail='delete job scheduler according to job_id with their respective detailed data')
    def delete(self, request, job_id):
        '''
        This endpoint is to delete any specific job scheduler with all detailed expression by providing job_id in path/url parameter
        '''
        try:
            JobScheduler.objects.get(Id=job_id).delete()
        except JobScheduler.DoesNotExist:
            return Response({"error":{},"error_message":"job not found","status":"NOT_FOUND_ERR"},status=404)
        except Exception as e:
            print(e)
            return Response({"error":e,"error_message":"some unexpected error ocurred","status":"INTERNAL_SERVER_ERR"},status=500)
        return Response({"message": "job successfully deleted"},status=200)

class GetJobDetails(APIView,PaginationHandlerMixin):
    pagination_class = BasicPagination
    serializer_class= JobSerializer
    @swagger_auto_schema(method='GET',responses=({200:success_responses_message, **error_responses}))
    @action(methods=['GET'],detail='get all job details with their respective detailed data')
    def get(self, *args, **kwargs):
        try:
            jobs = Job.objects.all().order_by("-Id")
        except Job.DoesNotExist:
            return Response({"error":{},"error_message":"job not found","status":"NOT_FOUND_ERR"},status=404)
        except Exception as e:
            return Response({"error":{e},"error_message":"some unexpected error ocurred","status":"INTERNAL_SERVER_ERR"},status=500)
        page = self.paginate_queryset(jobs)
        if page is not None:
            serializer = self.get_paginated_response(self.serializer_class(page,
                        many=True).data)
        else:
            serializer = self.serializer_class(jobs, many=True)
        return self.get_paginated_response(serializer.data) # <- here it is
    
def createDataFrameObject(obj: JobSchedulerDetailsSerializer):
    '''
    This function is to take all data of JobSchedulerDetails and add one more attribute 'Name' 
    from JobScheduler table using JobSchedulerId(fKey) and then make csv of that data using 
    'Pandas' under documents/scheduler/csv/data.csv file.
    '''
    if obj == None:
        obj = JobSchedulerDetailsSerializer(JobSchedulerDetails.objects.all(),many=True)
    obj = obj.data
    if not isinstance(obj,list):
        obj = [obj]
    for data in obj:
        jobData = JobScheduler.objects.filter(Id=data['JobSchedulerId']).get()
        data["Name"] = jobData.Name
    pd.DataFrame(obj).to_csv("documents/scheduler/csv/data.csv", index=False)

class ChannelMaster(APIView,PaginationHandlerMixin):
    pagination_class = BasicPagination
    serializer_class = ChannelSerializer

    @swagger_auto_schema(method='get',manual_parameters=[channel_id_query_param,search_query_param,from_date_query_param,to_date_query_param] ,responses=({200:success_responses_message, **error_responses}))
    @action(methods=['GET'],detail='get all channel details with their respective detailed data')
    def get(self, *args, **kwargs):
        Id = self.request.GET.get('channel_id',None)
        filter_set = query_set_for_filter(self.request.GET)
        try:
            if Id:
                channel = Channel.objects.get(Id=Id)
                serializer = self.serializer_class(channel)
                return Response({"data":serializer.data})                
            else:
                channel = Channel.objects.filter(**filter_set).order_by('-Id')
        except Channel.DoesNotExist:
            return Response({"error":{},"error_message":"channel not found","status":"NOT_FOUND_ERR"},status=404)
        except Exception as e:
            return Response({"error":{e},"error_message":"some unexpected error ocurred","status":"INTERNAL_SERVER_ERR"},status=500)
        page = self.paginate_queryset(channel)
        if page is not None:
            serializer = self.get_paginated_response(self.serializer_class(page,
                        many=True).data)
        else:
            serializer = self.serializer_class(channel, many=True)
        return self.get_paginated_response(serializer.data) # <- here it is
    
    @swagger_auto_schema(method='post',request_body=payload_for_master,responses=({200:success_responses_message, **error_responses}))
    @action(methods=['POST'],detail='Create channel detailed data')
    def post(self, *args, **kwargs):
        try:
            self.request.data["Id"] = Channel.objects.all().last().Id + 1
        except:
            self.request.data["Id"] = 1
        self.request.data['CreatedBy'] = ScmUser.object.all().first()
        serializer = self.serializer_class(data=dict(self.request.data),many=False)
        data = {}
        if serializer.is_valid():
            serializer.save()
            data['data'] = serializer.data
            data['response'] = 201
            data['message'] = "Created Successfully!"
        else:
            data['error'] = serializer._errors
            data['response'] = 400
            data['message'] = "Bad Request!"
        return Response(data)    

    @swagger_auto_schema(method='patch',manual_parameters=[channel_id_query_param] ,request_body=payload_for_master,responses=({200:success_responses_message, **error_responses}))
    @action(methods=['PATCH'],detail='edit channel details with their respective id')
    def patch(self, *args, **kwargs):
        data = {}
        Id = self.request.GET['channel_id']
        if Id:
            channel = Channel.objects.get(Id=Id)
        else:
            data['field'] = 'Id is required!'
            data['response'] = 400
            data['message'] = "Bad Request!"
            return JsonResponse(data)
        serializer = self.serializer_class(channel,data=dict(self.request.data),partial=True)
        if serializer.is_valid():
            serializer.save()
            data['data'] = serializer.data
            data['response'] = 200
            data['message'] = "Updated Successfully!"
        else:
            data['error'] = serializer._errors
            data['response'] = 400
            data['message'] = "Bad Request!"
        return JsonResponse(data)   
     
    @swagger_auto_schema(method='delete',manual_parameters=[channel_id_query_param] ,responses=({200:success_responses_message, **error_responses}))
    @action(methods=['DELETE'],detail='delete channel details with their respective id')
    def delete(self, *args, **kwargs):
        data = {}
        Id = self.request.GET['channel_id']
        if Id:
            channel = Channel.objects.get(Id=Id)
        else:
            data['field'] = 'Id is required!'
            data['response'] = 400
            data['message'] = "Bad Request!"
            return JsonResponse(data)
        try:
            channel.delete()
        except channel.DoesNotExist:
            return Response({"error":{},"error_message":"channel not found","status":"NOT_FOUND_ERR"},status=404)
        except Exception as e:
            return JsonResponse({"error":{e},"error_message":"some unexpected error ocurred","status":"INTERNAL_SERVER_ERR"},status=500)
        return JsonResponse({"message": "channel successfully deleted"},status=200)

class BUMaster(APIView,PaginationHandlerMixin):
    pagination_class = BasicPagination
    serializer_class = BUSerializer

    @swagger_auto_schema(method='get',manual_parameters=[bu_id_query_param,search_query_param,from_date_query_param,to_date_query_param],responses=({200:success_responses_message, **error_responses}))
    @action(methods=['GET'],detail='get all business unit details with their respective detailed data')
    def get(self, *args, **kwargs):
        Id = self.request.GET.get('bu_id',None)
        filter_set = query_set_for_filter(self.request.GET)
        try:
            if Id:
                bu = BU.objects.get(Id=Id)
                serializer = self.serializer_class(bu)
                return Response({"data":serializer.data})
            else:
                bu = BU.objects.filter(**filter_set).order_by('-Id')
        except BU.DoesNotExist:
            return Response({"error":{},"error_message":"BU not found","status":"NOT_FOUND_ERR"},status=404)
        except Exception as e:
            return Response({"error":{e},"error_message":"some unexpected error ocurred","status":"INTERNAL_SERVER_ERR"},status=500)
        
        page = self.paginate_queryset(bu)
        if page is not None:
            serializer = self.get_paginated_response(self.serializer_class(page,
                        many=True).data)
        else:
            serializer = self.serializer_class(bu, many=True)
        return self.get_paginated_response(serializer.data) # <- here it is

    @swagger_auto_schema(method='post',request_body=payload_for_bu,responses=({200:success_responses_message, **error_responses}))
    @action(methods=['POST'],detail='create business unit details with their respective detailed data')
    def post(self, *args, **kwargs):
        try:    
            self.request.data["Id"] = BU.objects.all().last().Id + 1
        except:
            self.request.data["Id"] = 1
        self.request.data['CreatedBy'] = ScmUser.object.all().first()
        serializer = self.serializer_class(data=dict(self.request.data),many=False)
        data = {}
        if serializer.is_valid():
            serializer.save()
            data['data'] = serializer.data
            data['response'] = 201
            data['message'] = "Created Successfully!"
            
        else:
            data['error'] = serializer._errors
            data['response'] = 400
            data['message'] = "Bad Request!"
        return Response(data)    

    @swagger_auto_schema(method='patch',manual_parameters=[bu_id_query_param],request_body=payload_for_bu,responses=({200:success_responses_message, **error_responses}))
    @action(methods=['PATCH'],detail='patch business unit details with their respective id')
    def patch(self, *args, **kwargs):
        data = {}
        Id = self.request.GET.get('bu_id',None)
        try:
            if Id:
                bu = BU.objects.get(Id=Id)
            else:
                data['field'] = 'Id is required!'
                data['response'] = 400
                data['message'] = "Bad Request!"
                return JsonResponse(data)
            serializer = self.serializer_class(bu,data=dict(self.request.data),partial=True)
            if serializer.is_valid():
                serializer.save()
                data['data'] = serializer.data
                data['response'] = 200
                data['message'] = "Updated Successfully!"
            else:
                data['error'] = serializer._errors
                data['response'] = 400
                data['message'] = "Bad Request!"
        except Exception as e:
            data['error'] = str(e)
            data['response'] = 500
            data['message'] = "Internal Server Error!"
        return JsonResponse(data)    

    @swagger_auto_schema(method='delete',manual_parameters=[bu_id_query_param],responses=({200:success_responses_message, **error_responses}))
    @action(methods=['DELETE'],detail='delete business details with their respective id')
    def delete(self, *args, **kwargs):
        data = {}
        Id = self.request.GET.get('bu_id',None)
        if Id:
            bu = BU.objects.get(Id=Id)
        else:
            data['field'] = 'Id is required!'
            data['response'] = 400
            data['message'] = "Bad Request!"
            return JsonResponse(data)
        try:
            bu.delete()
        except BU.DoesNotExist:
            return Response({"error":{},"error_message":"BU not found","status":"NOT_FOUND_ERR"},status=404)
        except Exception as e:
            return JsonResponse({"error":{e},"error_message":"some unexpected error ocurred","status":"INTERNAL_SERVER_ERR"},status=500)
        return JsonResponse({"message": "BU successfully deleted"},status=200)

class DivisionMaster(APIView,PaginationHandlerMixin):
    pagination_class = BasicPagination
    serializer_class = DivisionSerializer

    @swagger_auto_schema(method='get',manual_parameters=[division_id_query_param,search_query_param,from_date_query_param,to_date_query_param],responses=({200:success_responses_message, **error_responses}))
    @action(methods=['GET'],detail='get all division details with their respective detailed data')
    def get(self, *args, **kwargs):
        Id = self.request.GET.get('division_id',None)
        filter_set = query_set_for_filter(self.request.GET)
        try:
            if Id:
                division = Division.objects.get(Id=Id)
                serializer = self.serializer_class(division)
                return Response({"data":serializer.data})
            else:
                division = Division.objects.filter(**filter_set).order_by('-Id')
        except Division.DoesNotExist:
            return Response({"error":{},"error_message":"division not found","status":"NOT_FOUND_ERR"},status=404)
        except Exception as e:
            return Response({"error":{e},"error_message":"some unexpected error ocurred","status":"INTERNAL_SERVER_ERR"},status=500)
        page = self.paginate_queryset(division)
        if page is not None:
            serializer = self.get_paginated_response(self.serializer_class(page,
                        many=True).data)
        else:
            serializer = self.serializer_class(division, many=True)
        return self.get_paginated_response(serializer.data) # <- here it is

    @swagger_auto_schema(method='post',request_body=payload_for_master,responses=({200:success_responses_message, **error_responses}))
    @action(methods=['POST'],detail='create division details ')
    def post(self, *args, **kwargs):
        try:
            self.request.data["Id"] = Division.objects.all().last().Id + 1
        except:
            self.request.data["Id"] = 1
        self.request.data['CreatedBy'] = ScmUser.object.all().first()
        serializer = self.serializer_class(data=dict(self.request.data),many=False)
        data = {}
        if serializer.is_valid():
            serializer.save()
            data['data'] = serializer.data
            data['response'] = 201
            data['message'] = "Created Successfully!"
            
        else:
            data['error'] = serializer._errors
            data['response'] = 400
            data['message'] = "Bad Request!"
        return Response(data)    

    @swagger_auto_schema(method='patch',manual_parameters=[division_id_query_param],request_body=payload_for_master,responses=({200:success_responses_message, **error_responses}))
    @action(methods=['PATCH'],detail='edit division details with their respective id')
    def patch(self, *args, **kwargs):
        data = {}
        Id = self.request.GET['division_id']
        try:
            if Id:
                division = Division.objects.get(Id=Id)
            else:
                data['field'] = 'Id is required!'
                data['response'] = 400
                data['message'] = "Bad Request!"
                return JsonResponse(data)

            serializer = self.serializer_class(division,data=dict(self.request.data),partial=True)
            
            if serializer.is_valid():
                serializer.save()
                data['data'] = serializer.data
                data['response'] = 200
                data['message'] = "Updated Successfully!"
                
            else:
                data['error'] = serializer._errors
                data['response'] = 400
                data['message'] = "Bad Request!"
        except Exception as e:
            data['error'] = str(e)
            data['response'] = 500
            data['message'] = "Internal Server Error!"
        return JsonResponse(data)    

    @swagger_auto_schema(method='delete',manual_parameters=[division_id_query_param],responses=({200:success_responses_message, **error_responses}))
    @action(methods=['DELETE'],detail='delete division details with their respective id')
    def delete(self, *args, **kwargs):
        data = {}
        Id = self.request.GET['division_id']
        if Id:
            division = Division.objects.get(Id=Id)
        else:
            data['field'] = 'Id is required!'
            data['response'] = 400
            data['message'] = "Bad Request!"
            return JsonResponse(data)
        try:
            division.delete()
        except BU.DoesNotExist:
            return Response({"error":{},"error_message":"division not found","status":"NOT_FOUND_ERR"},status=404)
        except Exception as e:
            return JsonResponse({"error":{e},"error_message":"some unexpected error ocurred","status":"INTERNAL_SERVER_ERR"},status=500)
        return JsonResponse({"message": "division successfully deleted"},status=200)

class CategoryMaster(APIView,PaginationHandlerMixin):
    pagination_class = BasicPagination
    serializer_class = CategorySerializer

    @swagger_auto_schema(method='get',manual_parameters=[category_id_query_param,search_query_param,from_date_query_param,to_date_query_param],responses=({200:success_responses_message, **error_responses}))
    @action(methods=['GET'],detail='get all category details with their respective detailed data')
    def get(self, *args, **kwargs):
        Id = self.request.GET.get('category_id',None)
        filter_set = query_set_for_filter(self.request.GET)
        try:
            if Id:
                category = Category.objects.get(Id=Id)
                serializer = self.serializer_class(category)
                return Response({"data":serializer.data})
            else:
                category = Category.objects.filter(**filter_set).order_by('-Id')
        except Category.DoesNotExist:
            return Response({"error":{},"error_message":"category not found","status":"NOT_FOUND_ERR"},status=404)
        except Exception as e:
            return Response({"error":{e},"error_message":"some unexpected error ocurred","status":"INTERNAL_SERVER_ERR"},status=500)
        page = self.paginate_queryset(category)
        if page is not None:
            serializer = self.get_paginated_response(self.serializer_class(page,
                        many=True).data)
        else:
            serializer = self.serializer_class(category, many=True)
        return self.get_paginated_response(serializer.data) # <- here it is

    @swagger_auto_schema(method='post',request_body=payload_for_master,responses=({200:success_responses_message, **error_responses}))
    @action(methods=['POST'],detail='get all channel details with their respective detailed data')
    def post(self, *args, **kwargs):
        try:
            self.request.data["Id"] = Category.objects.all().last().Id + 1
        except:
            self.request.data["Id"] = 1
        self.request.data['CreatedBy'] = ScmUser.object.all().first()
        serializer = self.serializer_class(data=dict(self.request.data),many=False)
        data = {}
        if serializer.is_valid():
            serializer.save()
            data['data'] = serializer.data
            data['response'] = 201
            data['message'] = "Created Successfully!"
            
        else:
            data['error'] = serializer._errors
            data['response'] = 400
            data['message'] = "Bad Request!"
        return Response(data)    

    @swagger_auto_schema(method='patch',manual_parameters=[category_id_query_param],request_body=payload_for_master,responses=({200:success_responses_message, **error_responses}))
    @action(methods=['PATCH'],detail='edit category details with their respective id')
    def patch(self, *args, **kwargs):
        data = {}
        Id = self.request.GET.get('category_id',None)
        try:
            if Id:
                category = Category.objects.get(Id=Id)
            else:
                data['field'] = 'Id is required!'
                data['response'] = 400
                data['message'] = "Bad Request!"
                return JsonResponse(data)

            serializer = self.serializer_class(category,data=dict(self.request.data),partial=True)
            
            if serializer.is_valid():
                serializer.save()
                data['data'] = serializer.data
                data['response'] = 200
                data['message'] = "Updated Successfully!"
                
            else:
                data['error'] = serializer._errors
                data['response'] = 400
                data['message'] = "Bad Request!"
        except Exception as e:
            data['error'] = str(e)
            data['response'] = 500
            data['message'] = "Internal Server Error!"
        return JsonResponse(data)    

    @swagger_auto_schema(method='delete',manual_parameters=[category_id_query_param],responses=({200:success_responses_message, **error_responses}))
    @action(methods=['DELETE'],detail='delete category details with their respective id')
    def delete(self, *args, **kwargs):
        data = {}
        Id = self.request.GET.get('category_id',None)
        if Id:
            category = Category.objects.get(Id=Id)
        else:
            data['field'] = 'Id is required!'
            data['response'] = 400
            data['message'] = "Bad Request!"
            return JsonResponse(data)
        try:
            category.delete()
        except Category.DoesNotExist:
            return Response({"error":{},"error_message":"category not found","status":"NOT_FOUND_ERR"},status=404)
        except Exception as e:
            return JsonResponse({"error":{e},"error_message":"some unexpected error ocurred","status":"INTERNAL_SERVER_ERR"},status=500)
        return JsonResponse({"message": "category successfully deleted"},status=200)
    
class BrandView(APIView,PaginationHandlerMixin):
    pagination_class = BasicPagination
    serializer_class = BrandSerializer

    @swagger_auto_schema(method='get',manual_parameters=[brand_id_query_param,search_query_param,from_date_query_param,to_date_query_param],responses=({200:success_responses_message, **error_responses}))
    @action(methods=['GET'],detail='get all brand detail with their respective detailed data')
    def get(self, *args, **kwargs):
        filter_set = query_set_for_filter(self.request.GET)
        Id = self.request.GET.get('brand_id',None)
        try:
            if Id:
                brand = Brand.objects.get(Id=Id)
                serializer = self.serializer_class(brand)
                return Response({"data":serializer.data})
            else:
                brand = Brand.objects.filter(**filter_set).order_by('-Id')
        except Brand.DoesNotExist:
            return Response({"error":{},"error_message":"brand not found","status":"NOT_FOUND_ERR"},status=404)
        except Exception as e:
            return Response({"error":{e},"error_message":"some unexpected error ocurred","status":"INTERNAL_SERVER_ERR"},status=500)
        page = self.paginate_queryset(brand)
        if page is not None:
            serializer = self.get_paginated_response(self.serializer_class(page,many=True).data)
        else:
            serializer = self.serializer_class(brand, many=True)
        return self.get_paginated_response(serializer.data) # <- here it is
             
    @swagger_auto_schema(method='post',request_body=payload_for_brand,responses=({200:success_responses_message, **error_responses}))
    @action(methods=['POST'],detail='Create brand detailed data')  
    def post(self, *args, **kwargs):
        try:
            self.request.data["Id"] = Brand.objects.all().last().Id + 1
        except:
            self.request.data["Id"] = 1
        self.request.data['CreatedBy'] = ScmUser.object.all().first()
        serializer = self.serializer_class(data=dict(self.request.data),many=False)
        data = {}
        if serializer.is_valid():
            serializer.save()
            data['data'] = serializer.data
            data['response'] = 201
            data['message'] = "Created Successfully!"
            
        else:
            data['error'] = serializer._errors
            data['response'] = 400
            data['message'] = "Bad Request!"
        return Response(data)  

    @swagger_auto_schema(method='patch',manual_parameters=[brand_id_query_param] ,request_body=payload_for_brand,responses=({200:success_responses_message, **error_responses}))
    @action(methods=['PATCH'],detail='edit brand details with their respective id')
    def patch(self, *args, **kwargs):
        data = {}
        Id = self.request.GET['brand_id']
        if Id:
            brand = Brand.objects.get(Id=Id)
        else:
            data['field'] = 'Id is required!'
            data['response'] = 400
            data['message'] = "Bad Request!"
            return JsonResponse(data)
        serializer = self.serializer_class(brand,data=dict(self.request.data),partial=True)
        if serializer.is_valid():
            serializer.save()
            data['data'] = serializer.data
            data['response'] = 200
            data['message'] = "Updated Successfully!"
        else:
            data['error'] = serializer._errors
            data['response'] = 400
            data['message'] = "Bad Request!"
        return JsonResponse(data)   

    @swagger_auto_schema(method='delete',manual_parameters=[brand_id_query_param] ,responses=({200:success_responses_message, **error_responses}))
    @action(methods=['DELETE'],detail='delete brand details with their respective id')
    def delete(self, *args, **kwargs):
        data = {}
        Id = self.request.GET['brand_id']
        if Id:
            brand = Brand.objects.get(Id=Id)
        else:
            data['field'] = 'Id is required!'
            data['response'] = 400
            data['message'] = "Bad Request!"
            return JsonResponse(data)
        try:
            brand.delete()
        except Channel.DoesNotExist:
            return Response({"error":{},"error_message":"brand not found","status":"NOT_FOUND_ERR"},status=404)
        except Exception as e:
            return JsonResponse({"error":{e},"error_message":"some unexpected error ocurred","status":"INTERNAL_SERVER_ERR"},status=500)
        return JsonResponse({"message": "brand successfully deleted"},status=200)   
    

class BranchView(APIView,PaginationHandlerMixin):
    pagination_class = BasicPagination
    serializer_class = BranchSerializer
    
    @swagger_auto_schema(method='get',manual_parameters=[branch_id_query_param,search_query_param,from_date_query_param,to_date_query_param],responses=({200:success_responses_message, **error_responses}))
    @action(methods=['GET'],detail='get all branch detail with their respective detailed data')
    def get(self, *args, **kwargs):
        filter_set = query_set_for_filter(self.request.GET)
        Id = self.request.GET.get('branch_id',None)
        try:
            if Id:
                branch = Branch.objects.get(Id=Id)
                serializer = self.serializer_class(branch)
                return Response({"data":serializer.data})
            else:
                branch = Branch.objects.filter(**filter_set).order_by('-Id')
        except Branch.DoesNotExist:
            return Response({"error":{},"error_message":"branch not found","status":"NOT_FOUND_ERR"},status=404)
        except Exception as e:
            return Response({"error":{e},"error_message":"some unexpected error ocurred","status":"INTERNAL_SERVER_ERR"},status=500)
        page = self.paginate_queryset(branch)
        if page is not None:
            serializer = self.get_paginated_response(self.serializer_class(page,many=True).data)
        else:
            serializer = self.serializer_class(branch, many=True)
        return self.get_paginated_response(serializer.data) # <- here it is
    
    @swagger_auto_schema(method='post',request_body=payload_for_branch,responses=({200:success_responses_message, **error_responses}))
    @action(methods=['POST'],detail='Create branch detailed data')
    def post(self, *args, **kwargs):
        try:
            self.request.data["Id"] = Branch.objects.all().last().Id + 1
        except:
            self.request.data["Id"] = 1
        self.request.data['CreatedBy'] = ScmUser.object.all().first()
        serializer = self.serializer_class(data=dict(self.request.data),many=False)
        data = {}
        if serializer.is_valid():
            serializer.save()
            data['data'] = serializer.data
            data['response'] = 201
            data['message'] = "Created Successfully!"
            
        else:
            data['error'] = serializer._errors
            data['response'] = 400
            data['message'] = "Bad Request!"
        return Response(data)

    @swagger_auto_schema(method='patch',manual_parameters=[branch_id_query_param] ,request_body=payload_for_branch,responses=({200:success_responses_message, **error_responses}))
    @action(methods=['PATCH'],detail='edit branch details with their respective id')
    def patch(self, *args, **kwargs):
        data = {}
        Id = self.request.GET.get('branch_id',None)
        try:
            if Id:
                branch = Branch.objects.get(Id=Id)
            else:
                data['field'] = 'Id is required!'
                data['response'] = 400
                data['message'] = "Bad Request!"
                return JsonResponse(data)

            serializer = self.serializer_class(branch,data=dict(self.request.data),partial=True)
            
            if serializer.is_valid():
                serializer.save()
                data['data'] = serializer.data
                data['response'] = 200
                data['message'] = "Updated Successfully!"
                
            else:
                data['error'] = serializer._errors
                data['response'] = 400
                data['message'] = "Bad Request!"
        except Exception as e:
            data['error'] = str(e)
            data['response'] = 500
            data['message'] = "Internal Server Error!"
        return JsonResponse(data)
    
    @swagger_auto_schema(method='delete',manual_parameters=[branch_id_query_param] ,responses=({200:success_responses_message, **error_responses}))
    @action(methods=['DELETE'],detail='delete branch details with their respective id')
    def delete(self, *args, **kwargs):
        data = {}
        Id = self.request.GET.get('branch_id',None)
        if Id:
            branch = Branch.objects.get(Id=Id)
        else:
            data['field'] = 'Id is required!'
            data['response'] = 400
            data['message'] = "Bad Request!"
            return JsonResponse(data)
        try:
            branch.delete()
        except Brand.DoesNotExist:
            return Response({"error":{},"error_message":"branch not found","status":"NOT_FOUND_ERR"},status=404)
        except Exception as e:
            return JsonResponse({"error":{e},"error_message":"some unexpected error ocurred","status":"INTERNAL_SERVER_ERR"},status=500)
        return JsonResponse({"message": "brand successfully deleted"},status=200)

class RPRulesView(APIView,PaginationHandlerMixin):
    pagination_class = BasicPagination
    serializer_class = RPRulesSerializer
    
    @swagger_auto_schema(method='get',manual_parameters=[rp_rule_id_query_param,search_bu_name_query_param,from_date_query_param,to_date_query_param],responses=({200:success_responses_message, **error_responses}))
    @action(methods=['GET'],detail='get all rp rules detail with their respective detailed data')
    def get(self, *args, **kwargs):
        filter_set = query_set_for_filter(self.request.GET,"BU")
        Id = self.request.GET.get('rp_rule_id',None)
        try:
            if Id:
                rprules = RPRules.objects.get(Id=Id)
                serializer = self.serializer_class(rprules)
                return Response({"data":serializer.data})
            else:
                rprules = RPRules.objects.filter(**filter_set).order_by('-Id')
        except Branch.DoesNotExist:
            return Response({"error":{},"error_message":"rprule not found","status":"NOT_FOUND_ERR"},status=404)
        except Exception as e:
            return Response({"error":{e},"error_message":"some unexpected error ocurred","status":"INTERNAL_SERVER_ERR"},status=500)
        page = self.paginate_queryset(rprules)
        if page is not None:
            serializer = self.get_paginated_response(self.serializer_class(page,many=True).data)
        else:
            serializer = self.serializer_class(rprules, many=True)
        return self.get_paginated_response(serializer.data) # <- here it is
    
    @swagger_auto_schema(method='post',request_body=payload_for_rp_rule,responses=({200:success_responses_message, **error_responses}))
    @action(methods=['POST'],detail='Create rp rule detailed data')
    def post(self, *args, **kwargs):
        try:
            self.request.data["Id"] = RPRules.objects.all().last().Id + 1
        except:
            self.request.data["Id"] = 1
        self.request.data['CreatedBy'] = ScmUser.object.all().first()
        serializer = self.serializer_class(data=dict(self.request.data),many=False)
        data = {}
        if serializer.is_valid():
            serializer.save()
            data['data'] = serializer.data
            data['response'] = 201
            data['message'] = "Created Successfully!"
        else:
            data['error'] = serializer._errors
            data['response'] = 400
            data['message'] = "Bad Request!"
        return Response(data)

    @swagger_auto_schema(method='patch',manual_parameters=[rp_rule_id_query_param] ,request_body=payload_for_rp_rule,responses=({200:success_responses_message, **error_responses}))
    @action(methods=['PATCH'],detail='edit rp rule details with their respective id')
    def patch(self, *args, **kwargs):
        data = {}
        Id = self.request.GET.get('rp_rule_id',None)
        try:
            if Id:
                rprule = RPRules.objects.get(Id=Id)
            else:
                data['field'] = 'Id is required!'
                data['response'] = 400
                data['message'] = "Bad Request!"
                return JsonResponse(data)
            serializer = self.serializer_class(rprule,data=dict(self.request.data),partial=True)
            if serializer.is_valid():
                serializer.save()
                data['data'] = serializer.data
                data['response'] = 200
                data['message'] = "Updated Successfully!"
            else:
                data['error'] = serializer._errors
                data['response'] = 400
                data['message'] = "Bad Request!"
        except Exception as e:
            data['error'] = str(e)
            data['response'] = 500
            data['message'] = "Internal Server Error!"
        return JsonResponse(data)
    
    @swagger_auto_schema(method='delete',manual_parameters=[rp_rule_id_query_param] ,responses=({200:success_responses_message, **error_responses}))
    @action(methods=['DELETE'],detail='delete rp rule details with their respective id')
    def delete(self, *args, **kwargs):
        data = {}
        Id = self.request.GET.get('rp_rule_id',None)
        if Id:
            rprule = RPRules.objects.get(Id=Id)
        else:
            data['field'] = 'Id is required!'
            data['response'] = 400
            data['message'] = "Bad Request!"
            return JsonResponse(data)
        try:
            rprule.delete()
        except RPRules.DoesNotExist:
            return Response({"error":{},"error_message":"rp rule not found","status":"NOT_FOUND_ERR"},status=404)
        except Exception as e:
            return JsonResponse({"error":{e},"error_message":"some unexpected error ocurred","status":"INTERNAL_SERVER_ERR"},status=500)
        return JsonResponse({"message": "rp rule successfully deleted"},status=200)
    




class SKU_SNPView(APIView,PaginationHandlerMixin):
    pagination_class = BasicPagination
    serializer_class = SKU_SNPSerializer
    @swagger_auto_schema(method='get',manual_parameters=[sku_snp_id_query_param,search_query_param,from_date_query_param,to_date_query_param],responses=({200:success_responses_message, **error_responses}))
    @action(methods=['GET'],detail='get all sku_snp detail with their respective detailed data')
    def get(self, *args, **kwargs):
        filter_set = query_set_for_filter(self.request.GET)
        Id = self.request.GET.get('sku_snp_id',None)
        try:
            if Id:
                sku_snp = SKU_SNP.objects.get(Id=Id)
                serializer = self.serializer_class(sku_snp)
                return Response({"data":serializer.data})
            else:
                sku_snp = SKU_SNP.objects.filter(**filter_set).order_by('-Id')
        except SKU_SNP.DoesNotExist:
            return Response({"error":{},"error_message":"sku_snp not found","status":"NOT_FOUND_ERR"},status=404)
        except Exception as e:
            return Response({"error":{e},"error_message":"some unexpected error ocurred","status":"INTERNAL_SERVER_ERR"},status=500)
        page = self.paginate_queryset(sku_snp)
        if page is not None:
            serializer = self.get_paginated_response(self.serializer_class(page,many=True).data)
        else:
            serializer = self.serializer_class(sku_snp, many=True)
        return self.get_paginated_response(serializer.data)

    @swagger_auto_schema(method='post',request_body=payload_for_sku_snp,responses=({200:success_responses_message, **error_responses}))
    @action(methods=['POST'],detail='Create branch detailed data')
    def post(self, *args, **kwargs):
        try:
            self.request.data["Id"] = SKU_SNP.objects.all().last().Id + 1
        except:
            self.request.data["Id"] = 1
        self.request.data['CreatedBy'] = ScmUser.object.all().first()
        serializer = self.serializer_class(data=dict(self.request.data),many=False)
        data = {}
        if serializer.is_valid():
            serializer.save()
            data['data'] = serializer.data
            data['response'] = 201
            data['message'] = "Created Successfully!"
            
        else:
            data['error'] = serializer._errors
            data['response'] = 400
            data['message'] = "Bad Request!"
        return Response(data)

    @swagger_auto_schema(method='patch',manual_parameters=[sku_snp_id_query_param] ,request_body=payload_for_sku_snp,responses=({200:success_responses_message, **error_responses}))
    @action(methods=['PATCH'],detail='edit sku_snp details with their respective id')
    def patch(self, *args, **kwargs):
        data = {}
        Id = self.request.GET.get('sku_snp_id',None)
        try:
            if Id:
                sku_snp = SKU_SNP.objects.get(Id=Id)
            else:
                data['field'] = 'Id is required!'
                data['response'] = 400
                data['message'] = "Bad Request!"
                return JsonResponse(data)

            serializer = self.serializer_class(sku_snp,data=dict(self.request.data),partial=True)
            
            if serializer.is_valid():
                serializer.save()
                data['data'] = serializer.data
                data['response'] = 200
                data['message'] = "Updated Successfully!"
                
            else:
                data['error'] = serializer._errors
                data['response'] = 400
                data['message'] = "Bad Request!"
        except Exception as e:
            data['error'] = str(e)
            data['response'] = 500
            data['message'] = "Internal Server Error!"
        return JsonResponse(data)
    @swagger_auto_schema(method='delete',manual_parameters=[sku_snp_id_query_param] ,responses=({200:success_responses_message, **error_responses}))
    @action(methods=['DELETE'],detail='delete sku_snp details with their respective id')
    def delete(self, *args, **kwargs):
        data = {}
        Id = self.request.GET.get('sku_snp_id',None)
        if Id:
            sku_snp = SKU_SNP.objects.get(Id=Id)
        else:
            data['field'] = 'Id is required!'
            data['response'] = 400
            data['message'] = "Bad Request!"
            return JsonResponse(data)
        try:
            sku_snp.delete()
        except SKU_SNP.DoesNotExist:
            return Response({"error":{},"error_message":"sku_snp not found","status":"NOT_FOUND_ERR"},status=404)
        except Exception as e:
            return JsonResponse({"error":{e},"error_message":"some unexpected error ocurred","status":"INTERNAL_SERVER_ERR"},status=500)
        return JsonResponse({"message": "sku_snp successfully deleted"},status=200)
          
class Branch_SKUView(APIView,PaginationHandlerMixin):
    pagination_class = BasicPagination
    serializer_class = Branch_SKUSerializer
    def get(self, *args, **kwargs):
        filter_set = query_set_for_filter(self.request.GET)
        Id = self.request.GET.get('branch_sku_id',None)
        try:
            if Id:
                branch_sku = Branch_SKU.objects.get(Id=Id)
                serializer = self.serializer_class(branch_sku)
                return Response({"data":serializer.data})
            else:
                branch_sku = Branch_SKU.objects.filter(**filter_set).order_by('-Id')
        except Branch_SKU.DoesNotExist:
            return Response({"error":{},"error_message":"branch_sku not found","status":"NOT_FOUND_ERR"},status=404)
        except Exception as e:
            return Response({"error":{e},"error_message":"some unexpected error ocurred","status":"INTERNAL_SERVER_ERR"},status=500)
        page = self.paginate_queryset(branch_sku)
        if page is not None:
            serializer = self.get_paginated_response(self.serializer_class(page,many=True).data)
        else:
            serializer = self.serializer_class(branch_sku, many=True)
        return self.get_paginated_response(serializer.data)

    def post(self, *args, **kwargs):
        try:
            self.request.data["Id"] = Branch_SKU.objects.all().last().Id + 1
        except:
            self.request.data["Id"] = 1
        self.request.data['CreatedBy'] = ScmUser.object.all().first()
        serializer = self.serializer_class(data=dict(self.request.data),many=False)
        data = {}
        if serializer.is_valid():
            serializer.save()
            data['data'] = serializer.data
            data['response'] = 201
            data['message'] = "Created Successfully!"
            
        else:
            data['error'] = serializer._errors
            data['response'] = 400
            data['message'] = "Bad Request!"
        return Response(data)
    





    



    

         

      


 



    