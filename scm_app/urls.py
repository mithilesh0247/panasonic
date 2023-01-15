from scm_app.views import *
from django.urls import path, re_path as url
from rest_framework_swagger.views import get_swagger_view

schema_view = get_swagger_view(title='RP Api')
urlpatterns = [
    path('get-msl-value/', MSLReports.as_view(), name='get-msl-value'),
    path('scheduler/', scheduler.as_view(), name='scheduler'),
    # path('check-celery/',checkcelery,name="check-celery"),
    url(r'^$', schema_view),
    path('job/', JobSchedulerPostV1.as_view(), name='job-scheduler-v1'),
    path('job/<int:job_id>/', JobSchedulerV1.as_view(), name='job-scheduler-v1-with-job-id'),
    path('jobs/detail/', GetJobDetails.as_view(), name='jobs-detail-v1'),
    path('master/channel/', ChannelMaster.as_view(), name='master-channel'),
    path('master/bu/', BUMaster.as_view(), name='master-bu'),
    path('master/division/', DivisionMaster.as_view(), name='master-division'),
    path('master/category/', CategoryMaster.as_view(), name='master-category'),
    path('master/brand/',BrandView.as_view(),name='master-brand'),
    path('master/branch/',BranchView.as_view(),name='master-branch'),
    path('master/sku_snp/',SKU_SNPView.as_view(),name='master-sku-snp'),
    path('master/branch_sku/',Branch_SKUView.as_view(),name='master-branch-sku'),
    path('rp-rules/',RPRulesView.as_view(),name='rp-rules'),


    
]