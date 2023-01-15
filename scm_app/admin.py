from django.contrib import admin

# Register your models here.
from scm_app.models import * #Tenant,ScmUser#,Channel,BU,Division,Category,Brand,tblForecastDtl,SalesOrder_Exim_SFTP
# admin.site.register(Tenant)
admin.site.register(ScmUser)
admin.site.register(Channel)
admin.site.register(BU)
admin.site.register(Branch)
admin.site.register(Division)
admin.site.register(Category)
admin.site.register(Brand)
admin.site.register(MSL_report)
admin.site.register(JobScheduler)
admin.site.register(JobSchedulerDetails)
admin.site.register(Job)
admin.site.register(RPRules)

# admin.site.register(tblForecastDtl)
# admin.site.register(SalesOrder_Exim_SFTP)









