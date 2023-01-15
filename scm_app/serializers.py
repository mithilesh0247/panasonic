from rest_framework import serializers
from scm_app.models import *
from django_celery_beat.models import IntervalSchedule, PeriodicTask, CrontabSchedule

class ScmUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScmUser
        fields = '__all__'


class JobSchedulerDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobSchedulerDetails
        fields = '__all__'
        read_only_fields = ("job", )

class JobSchedulerSerializer(serializers.ModelSerializer):
    # CreatedBy = ScmUserSerializer(many=True,read_only=True)
    JobDetails = JobSchedulerDetailsSerializer(many=True, read_only=True)
    class Meta:
        model = JobScheduler
        fields = [
        'Id',
        'TenantId',
        'Name',
        'Frequency',
        'DateTime',
        'Status',
        'UserType',
        'UpdatedBy',
        'CreatedBy',
        'IPAddress',
        'JobDetails',
        ]

class MSLSerializer(serializers.ModelSerializer):
    class Meta:
        model=MSL_report
        fields = '__all__'

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['Tenant'] = Tenant.objects.filter(Id=ret['TenantId']).first().Name
        ret['BU'] = BU.objects.filter(Id=ret['BUId']).first().Name
        branch_data = Branch.objects.filter(Id=ret['BranchId']).first()
        if branch_data:
            ret['Source'] = branch_data.Name + " " +branch_data.BranchType
        else:
            ret['Branch'] = '--'
        sku_data = SKU_SNP.objects.filter(Id=ret['SKUId']).first()
        key_source_data = Production_Plant_SKU.objects.filter(SKUId=sku_data.Id).first().ProductionPlantId
        ret['SKU'] = sku_data.Name
        # ret['Item_code'] = sku_data.Code
        ret['LeadTime'] = sku_data.LeadTime
        ret['Division'] = Division.objects.filter(Id=ret['DivisionId']).first().Name
        ret['Category'] = Category.objects.filter(Id=ret['CategoryId']).first().Name
        brand_data = Brand.objects.filter(Id=ret['BrandId']).first()
        ret['Brand'] = brand_data.Name
        ret['Description_on'] = brand_data.Description
        ret['key_source'] = key_source_data.Location
        ret['Demand_sqr'] = int(ret['Demand'])**2
        ret['STD_sqr'] = float(ret['STD'])**2
        ret['SPT_sqr'] = float(ret['SPT'])**2
        ret['MSL'] = round(float(ret['MSL']),2)
        ret['PI'] = round(float(ret['PI']),2)
        ret['CS'] = round(float(ret['CS']),2)
        ret['SS'] = round(float(ret['SS']),2)
        ret['Demand'] = round(float(ret['Demand']),2)
        ret['NLT'] = round(float(ret['NLT']),2)
        ret['MLT'] = round(float(ret['MLT']),2)
        ret['STD'] = round(float(ret['STD']),2)
        ret['CurrentMSL'] = round(float(ret['CurrentMSL']),2)
        ret['FinalMSL'] = round(float(ret['FinalMSL']),2)
        #poping ID section
        ret.pop('TenantId')
        ret.pop('BUId')
        ret.pop('BranchId')
        ret.pop('SKUId')
        ret.pop('DivisionId')
        ret.pop('CategoryId')
        ret.pop('BrandId')
        return ret

class CronSerializer(serializers.ModelSerializer):
    class Meta:
        model = CrontabSchedule
        fields = ('__all__')

class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = "__all__"
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        scheduledJobData = JobSchedulerDetails.objects.filter(Id=ret['JobScheduledDetailsId']).first()
        ret['Date'] = scheduledJobData.CreatedDate
        ret['UpdatedDate'] = scheduledJobData.UpdatedDate
        ret['Run_time'] = ret['CreatedDate']
        return ret

class ChannelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Channel
        fields = "__all__"

    def validate(self, attrs):
        return super().validate(attrs)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        tenantData = Tenant.objects.filter(Id=ret['TenantId']).first()
        ret['TenantName'] = tenantData.Name
        return ret

class BUSerializer(serializers.ModelSerializer):

    class Meta:
        model = BU
        fields = "__all__"

    def validate(self, attrs):
        return super().validate(attrs)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['TenantName'] = Tenant.objects.filter(Id=ret['TenantId']).first().Name
        ret['ChannelName'] = Channel.objects.filter(Id=ret['channelID']).first().Name
        return ret

class DivisionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Division
        fields = "__all__"

    def validate(self, attrs):
        return super().validate(attrs)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['TenantName'] = Tenant.objects.filter(Id=ret['TenantId']).first().Name
        return ret

class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = "__all__"

    def validate(self, attrs):
        return super().validate(attrs)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['TenantName'] = Tenant.objects.filter(Id=ret['TenantId']).first().Name
        return ret
class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = "__all__"
    def validate(self, attrs):
        return super().validate(attrs)


class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model=Branch
        fields='__all__'

    def validate(self, attrs):
        return super().validate(attrs)
    
class SKU_SNPSerializer(serializers.ModelSerializer):
    class Meta:
        model = SKU_SNP
        fields = "__all__"

    def validate(self, attrs):
        return super().validate(attrs)


class Branch_SKUSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch_SKU
        fields = "__all__"

    def validate(self, attrs):
        return super().validate(attrs)
    

    
        
    
class RPRulesSerializer(serializers.ModelSerializer):
    class Meta:
        model=RPRules
        fields='__all__'

    def validate(self,attrs):
        return super().validate(attrs)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['BUName'] = BU.objects.filter(Id=ret['BU']).first().Name
        return ret
class Branch_SKUSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch_SKU
        fields = "__all__"
    def validate(self,attrs):
        return super().validate(attrs)
        
            