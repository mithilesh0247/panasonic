from django.db import models
from django.contrib.auth.models import *
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager

# Create your models here.

STATUS_CHOICES = (
        (1, 'Active'),
        (0, 'In-Active'),
        )

USER_TYPE = (
    ('PP','PP'),
    ('RP','RP'),
)

JOB_NAME = (
    ('MSL Planning', 'MSL Planning'),
    ('MSL Reporting', 'MSL Reporting'),
    ('Replenishment Planning', 'Replenishment Planning'),
    ('Replenishment Reporting', 'Replenishment Reporting'),
    ('DOS Calculation', 'DOS Calculation'),
    ('PP Planning', 'PP Planning'),
)
JOB_STATUS = (
    ('In-Process','In-Process'),
    ('Complete','Complete'),
    ('Failed','Failed'),
)

JOB_FREQUENCY = (
    ('YEARLY', 'YEARLY'),
    ('MONTHLY', 'MONTHLY'),
    ('WEEKLY', 'WEEKLY'),
    ('DAILY', 'DAILY'),
    ('HOURLY', 'HOURLY'),
)

MTO_RULES = (
    ("Safety stock Gap -> MSL Gap -> Forecast Gap","Safety stock Gap -> MSL Gap -> Forecast Gap"),
    ("MSL Gap -> Sales Order Gap / Shortage -> Forecast Gap","MSL Gap -> Sales Order Gap / Shortage -> Forecast Gap"),
    ("Stock Out Gap -> MSL Gap -> Order Gap ->Forecast Gap","Stock Out Gap -> MSL Gap -> Order Gap ->Forecast Gap")
)

FORECAST_TYPES = (
    ("Operational Forecast","Operational Forecast"),
    ("Final Forecast" ,"Final Forecast"),
)

class UsersManager(BaseUserManager):
    def create_user(self, email, password=None):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(
        email=self.normalize_email(email),
        )
        user.set_password(password)
        user.save(using=self._db)
        scmuser = ScmUser()
        scmuser.email = email
        scmuser.admin = True
        scmuser.save()
        return user
    def create_staffuser(self, email, password):
        """
        Creates and saves a staff user with the given email and password.
        """
        user = self.create_user(
        email,
        password=password,
        )
        user.staff = True
        user.save(using=self._db)
        scmuser = ScmUser()
        scmuser.email = email
        scmuser.staff = True
        scmuser.save()
        return user
    def create_superuser(self, email, password):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(
        email,
        password=password,
        )
        user.staff = True
        user.admin = True
        user.save(using=self._db)
        scmuser = ScmUser()
        scmuser.email = email
        scmuser.staff = True
        scmuser.save()
        return user


class ScmUser(AbstractBaseUser):
   email=models.CharField(primary_key=True,max_length=300)
   active=models.BooleanField(default=True)
   staff=models.BooleanField(default=False)
   admin=models.BooleanField(default=False)
   time_stamp=models.TimeField(auto_now_add=True)
   USERNAME_FIELD='email'
   REQUIRED_FIELDS=[]
   def get_first_name(self):
      return self.email
   def get_short_name(self):
      return self.email
   def __str__(self):
      return self.email
   def has_perm(self,perm,obj=None):
      return True
   def has_module_perms(self,app_label):
      return True
   @property
   def is_staff(self):
      "Is the user a member of staff?"
      return self.staff
   @property
   def is_admin(self):
      "Is the user a admin member?"
      return self.admin
   @property
   def is_active(self):
      "Is the user active?"
      return self.active
   
   object=UsersManager()
  



class Tenant(models.Model):
    Id = models.IntegerField(primary_key=True)
    Code=models.CharField(max_length=300,null=True,blank=True)
    Name=models.CharField(max_length=300,null=True,blank=True)
    Description=models.TextField(null=True,blank=True,default='')
    CreatedDate= models.DateField(auto_now_add=True)
    CreatedBy=models.ForeignKey(ScmUser,db_column = 'CreatedBy', on_delete=models.CASCADE)
    UpdatedDate=models.DateField(auto_now=True,null=True,blank=True)
    UpdatedBy=models.IntegerField(default=None,blank=True,null=True)
    IPAddress = models.CharField(max_length=300,null=True,blank=True)
    Status=models.IntegerField(choices=STATUS_CHOICES)
    class Meta:
        db_table = "Tenant"

class Channel(models.Model):
    Id = models.IntegerField(primary_key=True)
    TenantId = models.ForeignKey(Tenant, db_column = 'TenantId',on_delete = models.CASCADE)
    Code=models.CharField(max_length=300,null=True,blank=True)
    Name=models.CharField(max_length=300,null=True,blank=True)
    Description=models.TextField(null=True,blank=True,default='')
    CreatedDate= models.DateField(auto_now_add=True)
    CreatedBy=models.ForeignKey(ScmUser, db_column = 'CreatedBy', on_delete=models.CASCADE)
    UpdatedDate=models.DateField(auto_now=True,null=True,blank=True)
    UpdatedBy=models.IntegerField(default=None,blank=True,null=True)
    IPAddress = models.CharField(max_length=300,null=True,blank=True)
    Status=models.IntegerField(choices=STATUS_CHOICES)
    class Meta:
        db_table = "Channel"
#trying for this........

class BU(models.Model):
    Id = models.IntegerField(primary_key=True)
    TenantId = models.ForeignKey(Tenant, db_column = 'TenantId',on_delete = models.CASCADE)
    Code=models.CharField(max_length=300,null=True,blank=True)
    Name=models.CharField(max_length=300,null=True,blank=True)
    Description=models.TextField(null=True,blank=True,default='')
    CreatedDate= models.DateTimeField(auto_now_add=True)
    CreatedBy=models.ForeignKey(ScmUser, db_column = 'CreatedBy', on_delete=models.CASCADE)
    UpdatedDate=models.DateField(auto_now=True,null=True,blank=True)
    UpdatedBy=models.IntegerField(default=None,blank=True,null=True)
    IPAddress = models.CharField(max_length=300,null=True,blank=True)
    Status=models.IntegerField(choices=STATUS_CHOICES)
    channelID=models.ForeignKey(Channel, db_column="channelID", on_delete=models.CASCADE)
    class Meta:
        db_table = "BU"

class Division(models.Model):
    Id = models.IntegerField(primary_key=True)
    TenantId = models.ForeignKey(Tenant, db_column = 'TenantId',on_delete = models.CASCADE)
    Code=models.CharField(max_length=300,null=True,blank=True)
    Name=models.CharField(max_length=300,null=True,blank=True)
    Description=models.TextField(null=True,blank=True,default='')
    CreatedDate= models.DateField(auto_now_add=True)
    CreatedBy=models.ForeignKey(ScmUser, db_column = 'CreatedBy', on_delete=models.CASCADE)
    UpdatedDate=models.DateField(auto_now=True,null=True,blank=True)
    UpdatedBy=models.IntegerField(default=None,blank=True,null=True)
    Status=models.IntegerField(choices=STATUS_CHOICES)
    IPAddress = models.CharField(max_length=300,null=True,blank=True)
    class Meta:
        db_table = "Division"

class Category(models.Model):
    Id = models.IntegerField(primary_key=True)
    TenantId = models.ForeignKey(Tenant, db_column = 'TenantId',on_delete = models.CASCADE)
    Code=models.CharField(max_length=300,null=True,blank=True)
    Name=models.CharField(max_length=300,null=True,blank=True)
    Description=models.TextField(null=True,blank=True,default='')
    CreatedDate= models.DateField(auto_now_add=True)
    CreatedBy=models.ForeignKey(ScmUser, db_column = 'CreatedBy', on_delete=models.CASCADE)
    UpdatedDate=models.DateField(auto_now=True,null=True,blank=True)
    UpdatedBy=models.IntegerField(default=None,blank=True,null=True)
    Status=models.IntegerField(choices=STATUS_CHOICES)
    IPAddress = models.CharField(max_length=300,null=True,blank=True)
    class Meta:
        db_table = "Category"

class Brand(models.Model):
    Id = models.IntegerField(primary_key=True)
    TenantId = models.ForeignKey(Tenant, db_column = 'TenantId',on_delete = models.CASCADE)
    Code=models.CharField(max_length=300,null=True,blank=True)
    Name=models.CharField(max_length=300,null=True,blank=True)
    Description=models.TextField(null=True,blank=True,default='')
    CreatedDate= models.DateField(auto_now_add=True)
    CreatedBy=models.ForeignKey(ScmUser, db_column = 'CreatedBy', on_delete=models.CASCADE)
    UpdatedDate=models.DateField(auto_now=True,null=True,blank=True)
    UpdatedBy=models.IntegerField(default=None,blank=True,null=True)
    Status=models.IntegerField(choices=STATUS_CHOICES)
    IPAddress = models.CharField(max_length=300,null=True,blank=True)
    class Meta:
        db_table = "Brand"

class Branch(models.Model):
    Id = models.IntegerField(primary_key=True)
    TenantId = models.ForeignKey(Tenant, db_column = 'TenantId',on_delete = models.CASCADE)
    BUId = models.ForeignKey(BU, db_column = "BUId", on_delete=models.CASCADE)
    channelID=models.ForeignKey(Channel, db_column = "channelID", on_delete=models.CASCADE)
    Code=models.CharField(max_length=300,null=True,blank=True)
    Name=models.CharField(max_length=300,null=True,blank=True)
    Description=models.TextField(null=True,blank=True,default='')
    BranchType = models.CharField(max_length=300,null=True,blank=True)
    TotalVolume = models.CharField(max_length=100,null=True,blank=True)
    TotalArea = models.CharField(max_length=100,null=True,blank=True)
    OperatinHours = models.CharField(max_length=100,null=True,blank=True)
    OpertingDaysoftheWeek = models.CharField(max_length=100,null=True,blank=True)
    operating_times = models.CharField(max_length=100,null=True,blank=True)
    LoadingTimes = models.CharField(max_length=100,null=True,blank=True)
    UnloadingTimes = models.CharField(max_length=100,null=True,blank=True)
    CreatedDate= models.DateField(auto_now_add=True)
    CreatedBy=models.ForeignKey(ScmUser, db_column = 'CreatedBy', on_delete=models.CASCADE)
    UpdatedDate=models.DateField(auto_now=True,null=True,blank=True)
    UpdatedBy=models.IntegerField(default=None,blank=True,null=True)
    IPAddress = models.CharField(max_length=300,null=True,blank=True)
    Status=models.IntegerField(choices=STATUS_CHOICES)
    class Meta:
        db_table = "Branch"

class SKU_SNP(models.Model):
    Id = models.IntegerField(primary_key=True)
    TenantId = models.ForeignKey(Tenant, db_column = 'TenantId',on_delete = models.CASCADE)
    BUId = models.ForeignKey(BU, db_column = "BUId", on_delete=models.CASCADE)
    Code=models.CharField(max_length=300,null=True,blank=True)
    Name=models.CharField(max_length=300,null=True,blank=True)
    Description=models.TextField(null=True,blank=True,default='')
    UOM = models.CharField(max_length=100,null=True,blank=True)
    CategoryId = models.ForeignKey(Category, db_column="CategoryId", on_delete=models.CASCADE)
    DivisionId = models.ForeignKey(Division, db_column="DivisionId", on_delete=models.CASCADE)
    Brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    LeadTime = models.CharField(max_length=100,null=True,blank=True)
    CreatedDate= models.DateField(auto_now_add=True)
    CreatedBy=models.ForeignKey(ScmUser, db_column = 'CreatedBy', on_delete=models.CASCADE)
    UpdatedDate=models.DateField(auto_now=True,null=True,blank=True)
    UpdatedBy=models.IntegerField(default=None,blank=True,null=True)
    Status=models.IntegerField(choices=STATUS_CHOICES)
    IPAddress = models.CharField(max_length=300,null=True,blank=True)
    class Meta:
        db_table = "SKU_SNP"

class Network(models.Model):
    Id = models.IntegerField(primary_key=True)
    SupplyBranch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    SupplyBranchType = models.CharField(max_length=300,null=True,blank=True)
    DemandBranch = models.CharField(max_length=300,null=True,blank=True)
    DemandBranchType = models.CharField(max_length=300,null=True,blank=True)
    DeliveryLeadTime = models.CharField(max_length=300,null=True,blank=True)
    CreatedDate= models.DateField(auto_now_add=True)
    CreatedBy=models.ForeignKey(ScmUser, db_column = 'CreatedBy', on_delete=models.CASCADE)
    UpdatedDate=models.DateField(auto_now=True,null=True,blank=True)
    UpdatedBy=models.IntegerField(default=None,blank=True,null=True)
    IPAddress = models.CharField(max_length=300,null=True,blank=True)
    class Meta:
        db_table = "Network"

class Branch_SKU(models.Model):
    Id = models.IntegerField(primary_key=True)
    BranchId = models.ForeignKey(Branch, db_column="BranchId", on_delete=models.CASCADE)
    SkuId = models.ForeignKey(SKU_SNP, db_column="SkuId", on_delete=models.CASCADE)
    MSL = models.IntegerField(default=None)
    CreatedDate= models.DateField(auto_now_add=True)
    CreatedBy=models.ForeignKey(ScmUser, db_column = 'CreatedBy', on_delete=models.CASCADE)
    UpdatedDate=models.DateField(auto_now=True,null=True,blank=True)
    UpdatedBy=models.IntegerField(default=None,blank=True,null=True)
    Status=models.IntegerField(choices=STATUS_CHOICES)
    class Meta:
        db_table = "Branch_SKU"

class Production_Plant(models.Model):
    Id = models.IntegerField(primary_key=True)
    Name=models.CharField(max_length=300,null=True,blank=True)
    Location=models.CharField(max_length=300,null=True,blank=True)
    CreatedDate= models.DateField(auto_now_add=True)
    CreatedBy=models.ForeignKey(ScmUser, db_column = 'CreatedBy', on_delete=models.CASCADE)
    UpdatedDate=models.DateField(auto_now=True,null=True,blank=True)
    UpdatedBy=models.IntegerField(default=None,blank=True,null=True)
    IPAddress = models.CharField(max_length=300,null=True,blank=True)
    Status=models.IntegerField(choices=STATUS_CHOICES)
    class Meta:
        db_table = "Production_Plant"

class Production_Plant_SKU(models.Model):
    Id = models.IntegerField(primary_key=True)
    ProductionPlantId = models.ForeignKey(Production_Plant,db_column="ProductionPlantId", on_delete=models.CASCADE)
    SKUId = models.ForeignKey(SKU_SNP,db_column="SKUId", on_delete=models.CASCADE)
    CreatedDate= models.DateField(auto_now_add=True)
    CreatedBy=models.ForeignKey(ScmUser, db_column = 'CreatedBy', on_delete=models.CASCADE)
    UpdatedDate=models.DateField(auto_now=True,null=True,blank=True)
    UpdatedBy=models.IntegerField(default=None,blank=True,null=True)
    IPAddress = models.CharField(max_length=300,null=True,blank=True)
    Status=models.IntegerField(choices=STATUS_CHOICES)
    class Meta:
        db_table = "Production_Plant_SKU"

class tblForecastDtl(models.Model):
    forecastid=models.CharField(max_length=100,null=True,blank=True)
    productid=models.CharField(max_length=100,null=True,blank=True)
    Compid=models.CharField(max_length=100,null=True,blank=True)
    salesmonth=models.CharField(max_length=100,null=True,blank=True)
    salesYr=models.CharField(max_length=100,null=True,blank=True)
    salesDt=models.CharField(max_length=100,null=True,blank=True)
    statsQty=models.CharField(max_length=200,null=True,blank=True)
    OprtnQty=models.CharField(max_length=250,null=True,blank=True)
    asp=models.CharField(max_length=250,null=True,blank=True)
    abc=models.CharField(max_length=200,null=True,blank=True)
    M0_QTY_3SC=models.CharField(max_length=250,null=True,blank=True)
    M1_QTY_3SC=models.CharField(max_length=250,null=True,blank=True)
    M2_QTY_3SC=models.CharField(max_length=250,null=True,blank=True)
    M3_QTY_3SC=models.CharField(max_length=250,null=True,blank=True)
    M4_QTY_3SC=models.CharField(max_length=250,null=True,blank=True)
    M5_QTY_3SC=models.CharField(max_length=250,null=True,blank=True)
    M6_QTY_3SC=models.CharField(max_length=250,null=True,blank=True)
    M7_QTY_3SC=models.CharField(max_length=250,null=True,blank=True)
    M8_QTY_3SC=models.CharField(max_length=250,null=True,blank=True)
    M8_QTY_3SC=models.CharField(max_length=250,null=True,blank=True)
    M9_QTY_3SC=models.CharField(max_length=250,null=True,blank=True)
    M10_QTY_3SC=models.CharField(max_length=250,null=True,blank=True)
    M11_QTY_3SC=models.CharField(max_length=250,null=True,blank=True)
    M12_QTY_3SC=models.CharField(max_length=250,null=True,blank=True)
    M0_QTY_3SC=models.CharField(max_length=250,null=True,blank=True)
    M1_QTY=models.CharField(max_length=250,null=True,blank=True)
    M2_QTY=models.CharField(max_length=250,null=True,blank=True)
    M3_QTY=models.CharField(max_length=250,null=True,blank=True)
    M4_QTY=models.CharField(max_length=250,null=True,blank=True)
    M5_QTY=models.CharField(max_length=250,null=True,blank=True)
    M6_QTY=models.CharField(max_length=250,null=True,blank=True)
    M7_QTY=models.CharField(max_length=250,null=True,blank=True)
    M8_QTY=models.CharField(max_length=250,null=True,blank=True)
    M9_QTY=models.CharField(max_length=250,null=True,blank=True)
    M10_QTY=models.CharField(max_length=250,null=True,blank=True)
    M11_QTY=models.CharField(max_length=250,null=True,blank=True)
    M12_QTY=models.CharField(max_length=250,null=True,blank=True)
    M6_Avg_Sales=models.CharField(max_length=400,blank=True,null=True)
    M3_Avg_Sales=models.CharField(max_length=400,blank=True,null=True)
    L3M_Qty_Avg=models.CharField(max_length=400,blank=True,null=True)
    LYSM1_Sales=models.CharField(max_length=400,blank=True,null=True)
    LYSM2_Sales=models.CharField(max_length=400,blank=True,null=True)
    LYSM3_Sales=models.CharField(max_length=400,blank=True,null=True)
    LM_Sales=models.CharField(max_length=300,blank=True,null=True)
    L3M_Pri_QTY=models.CharField(max_length=250,null=True,blank=True)
    ReasonId=models.CharField(max_length=250,null=True,blank=True)
    IsChanged=models.BooleanField(default=False)
    IsApproved=models.BooleanField(default=True)
    SKUStatus=models.BooleanField(default=True)
    CreatedBy=models.CharField(max_length=300,blank=True,null=True)
    CreatedDt=models.DateTimeField(auto_now_add=True)
    UpdatedBy=models.CharField(max_length=400,blank=True,null=True)
    UpdateDt=models.DateTimeField(auto_now_add=True)
    L12Min=models.CharField(max_length=250,null=True,blank=True)
    L12Max=models.CharField(max_length=250,null=True,blank=True)
    M1=models.CharField(max_length=300,blank=True,null=True)
    M2=models.CharField(max_length=300,blank=True,null=True)
    M3=models.CharField(max_length=300,blank=True,null=True)
    M4=models.CharField(max_length=300,blank=True,null=True)
    M5=models.CharField(max_length=300,blank=True,null=True)
    M6=models.CharField(max_length=300,blank=True,null=True)
    Category=models.CharField(max_length=300,blank=True,null=True)
    Category1=models.CharField(max_length=300,blank=True,null=True)
    Line1=models.CharField(max_length=300,blank=True,null=True)
    Line2=models.CharField(max_length=300,blank=True,null=True)
    Line3=models.CharField(max_length=300,blank=True,null=True)
    Line4=models.CharField(max_length=300,blank=True,null=True)
    SKU=models.ForeignKey(SKU_SNP,db_column="SKU", on_delete=models.CASCADE)
    Channel=models.ForeignKey(Channel,db_column="Channel", on_delete=models.CASCADE)
    LocationID=models.CharField(max_length=100,null=True,blank=True)
    class Meta:
        db_table = "tblForecastDtl"

class SalesOrder(models.Model):
    order_no=models.CharField(max_length=100,null=True,blank=True)
    Order_Date=models.DateTimeField()
    pick_slip_no=models.CharField(max_length=100,null=True,blank=True)
    SHIPPER_Exporter_Name=models.CharField(max_length=300,null=True,blank=True)
    shipper_exporter_address=models.CharField(max_length=600,null=True,blank=True)
    consignee_Name=models.CharField(max_length=300,null=True,blank=True)
    consignee_address=models.CharField(max_length=600,null=True,blank=True)
    warehouse_Code=models.ForeignKey(Branch,db_column="warehouse_Code" ,on_delete=models.CASCADE)
    warehouse_Name=models.CharField(max_length=400,null=True,blank=True)
    warehouse_address=models.CharField(max_length=600,null=True,blank=True)
    bill_to_Name=models.CharField(max_length=300,null=True,blank=True)
    bill_to_address=models.CharField(max_length=300,null=True,blank=True)
    Exportersref=models.CharField(max_length=300,null=True,blank=True)
    Exportersref=models.CharField(max_length=300,null=True,blank=True)
    others_ref=models.CharField(max_length=300,null=True,blank=True)
    cust_po_no=models.CharField(max_length=100,null=True,blank=True)
    cust_po_date=models.DateTimeField(auto_now_add=True)
    gst_invoice_no=models.CharField(max_length=200,null=True,blank=True)
    gst_inv_date=models.DateTimeField(auto_now_add=True)
    currency=models.CharField(max_length=400)
    cgst_rate=models.CharField(max_length=100,null=True,blank=True)
    cgst_amount=models.CharField(max_length=100,null=True,blank=True)
    sgst_rate=models.CharField(max_length=400,blank=True,null=True)
    sgst_amount=models.CharField(max_length=100,null=True,blank=True)
    igst_rate=models.CharField(max_length=100,null=True,blank=True)
    igst_amount=models.CharField(max_length=100,null=True,blank=True)
    tcs_rate=models.CharField(max_length=100,null=True,blank=True)
    tcs_amount=models.CharField(max_length=100,null=True,blank=True)
    invoice_total_amount=models.CharField(max_length=100,null=True,blank=True)
    invoice_amount_in_words=models.CharField(max_length=600,null=True,blank=True)
    bank_name=models.CharField(max_length= 1000,null=True,blank=True)
    branch_branch=models.CharField(max_length=600,null=True,blank=True)
    bank_ifsc_code=models.CharField(max_length=400,null=True,blank=True)
    bank_account_no=models.CharField(max_length=100,null=True,blank=True)
    ifsc_code=models.CharField(max_length=400,null=True,blank=True)
    micr_code=models.CharField(max_length= 1000,null=True,blank=True)
    swift_code=models.CharField(max_length=100,null=True,blank=True)
    payment_term=models.CharField(max_length=400,null=True,blank=True)
    incoterm=models.CharField(max_length=400,null=True,blank=True)
    shipment_type=models.CharField(max_length= 1000,null=True,blank=True)
    shipment_mode=models.CharField(max_length= 1000,null=True,blank=True)
    port_of_loading=models.CharField(max_length= 1000,null=True,blank=True)
    port_of_discharge=models.CharField(max_length= 1000,null=True,blank=True)
    country_of_origin=models.CharField(max_length= 1000,null=True,blank=True)
    state_of_origin=models.CharField(max_length= 1000,null=True,blank=True)
    district_of_origin=models.CharField(max_length= 1000,null=True,blank=True)
    final_destination=models.CharField(max_length= 1000,null=True,blank=True)
    country_of_final_destination=models.CharField(max_length=600,null=True,blank=True)
    pre_carriage_by=models.CharField(max_length= 1000,null=True,blank=True)
    place_of_receipt_of_pre_carr=models.CharField(max_length= 1000,null=True,blank=True)
    vessel_flight_no=models.CharField(max_length=100,null=True,blank=True)
    adcode=models.CharField(max_length= 1000,null=True,blank=True)
    totalquantity=models.CharField(max_length= 1000,null=True,blank=True)
    totalnetweight=models.CharField(max_length=100,null=True,blank=True)
    totalgrossweight=models.CharField(max_length=100,null=True,blank=True)
    custom_division=models.CharField(max_length=100,null=True,blank=True)
    gstin=models.CharField(max_length= 1000,null=True,blank=True)
    name_of_commissionarate=models.CharField(max_length= 1000,null=True,blank=True)
    item_code=models.ForeignKey(SKU_SNP,db_column="item_code",on_delete=models.CASCADE)
    item_description=models.CharField(max_length=700,null=True,blank=True)
    product_category=models.CharField(max_length=300,null=True,blank=True)
    hsn_code=models.CharField(max_length=100,null=True,blank=True)
    qty=models.CharField(max_length=100,null=True,blank=True)
    product_category=models.CharField(max_length=300,null=True,blank=True)
    uom=models.CharField(max_length=300,null=True,blank=True)
    unit_rate=models.CharField(max_length=100,null=True,blank=True)
    net_weight=models.CharField(max_length=100,null=True,blank=True)
    gross_weight=models.CharField(max_length=100,null=True,blank=True)
    total_price=models.CharField(max_length=100,null=True,blank=True)
    warehousecode=models.CharField(max_length=100,null=True,blank=True)
    header_id=models.CharField(max_length=100,null=True,blank=True)
    line_id=models.CharField(max_length=100,null=True,blank=True)
    delivery_detail_id=models.CharField(max_length=100,null=True,blank=True)
    delivery_assignment_id=models.CharField(max_length=100,null=True,blank=True)
    delivery_id=models.CharField(max_length=100,null=True,blank=True)
    exim_state_origin=models.CharField(max_length=300,null=True,blank=True)
    exim_district_origin=models.CharField(max_length=300,null=True,blank=True)
    consignee_country=models.CharField(max_length=300,null=True,blank=True)
    consignee_tel_no=models.CharField(max_length=100,null=True,blank=True)
    ship_to_details=models.CharField(max_length=300,null=True,blank=True)
    export_pincode=models.CharField(max_length=100,null=True,blank=True)
    export_country=models.CharField(max_length=100,null=True,blank=True)
    buyer_ord_count_date=models.DateTimeField(auto_now_add=True)
    other_ref_count_tel_no=models.CharField(max_length=100,blank=True,null=True)
    add_inf_payment_term=models.CharField(max_length=300,blank=True,null=True)
    hdr_status=models.CharField(max_length=100,blank=True,null=True)
    line_status=models.CharField(max_length=100,blank=True,null=True)
    shipping_status=models.CharField(max_length=100,blank=True,null=True)
    order_type=models.CharField(max_length=150,blank=True,null=True)
    reference_type=models.CharField(max_length=100,blank=True,null=True)
    reference_no=models.CharField(max_length=100,blank=True,null=True)
    reference_line_no=models.CharField(max_length=100,null=True,blank=True)
    custom_exchange_currency=models.CharField(max_length=300,null=True,blank=True)
    custom_exchange_rate=models.CharField(max_length=200,null=True,blank=True)
    class Meta:
        db_table = "SalesOrder"

class FC_Details(models.Model):
    TenantId=models.ForeignKey(Tenant,db_column="TenantId",on_delete=models.CASCADE)
    Forecast_No=models.CharField(max_length=100,null=True,blank=True)
    ChannelId=models.ForeignKey(Channel,db_column="ChannelId",on_delete=models.CASCADE)
    Channel=models.CharField(max_length=300,null=True,blank=True)
    BUId=models.ForeignKey(BU,db_column="BUId",on_delete=models.CASCADE)
    BU=models.CharField(max_length=300,null=True,blank=True)
    BranchId = models.ForeignKey(Branch,db_column="BranchId",on_delete=models.CASCADE,default=None,blank=True,null=True)
    BranchDescription = models.CharField(max_length=300,null=True,blank=True)
    DivisionId=models.ForeignKey(Division,db_column="DivisionId",on_delete=models.CASCADE)
    Division=models.CharField(max_length=300,null=True,blank=True)
    CategoryId=models.ForeignKey(Category,db_column="CategoryId",on_delete=models.CASCADE)
    Category=models.CharField(max_length=300,null=True,blank=True)
    BrandId=models.ForeignKey(Brand,db_column="BrandId",on_delete=models.CASCADE)
    Brand=models.CharField(max_length=300,null=True,blank=True)
    SKUId=models.ForeignKey(SKU_SNP,db_column="SKUId",on_delete=models.CASCADE)
    SKU_Code =models.CharField(max_length=300,null=True,blank=True)
    SKU=models.CharField(max_length=300,null=True,blank=True)
    SKU_Class =models.CharField(max_length=20,null=True,blank=True)
    SKU_Status =models.CharField(max_length= 100,null=True,blank=True)
    Region=models.CharField(max_length=100,null=True,blank=True)
    AGGREGATE_SPEC1 =models.CharField(max_length=100,null=True,blank=True)
    AGGREGATE_SPEC2 =models.CharField(max_length=100,null=True,blank=True)
    DepoCode=models.CharField(max_length= 100,null=True,blank=True)
    ASM= models.CharField(max_length=300,null=True,blank=True)
    LCID=models.CharField(max_length=100,null=True,blank=True)
    Launch_Date =models.DateTimeField(auto_now_add=True)
    Launch_PLSIND_State =models.CharField(max_length=100,null=True,blank=True)
    Launch_PLSIND_StateFlag =models.IntegerField(null=True,blank=True)
    ASP=models.IntegerField(null=True,blank=True)
    YTDAvg_Sales =models.IntegerField(null=True,blank=True)
    YTDAvg_Sales_Val =models.IntegerField(default=0,null=True,blank=True)
    Twelve_Mon_Avg_Sales =models.IntegerField(null=True,blank=True)
    Twelve_Mon_Avg_Sales_val =models.IntegerField(default=0,null=True,blank=True)
    Six_Mon_Avg_Sales = models.IntegerField(null=True,blank=True)
    Six_Mon_Avg_Sales_Val =models.IntegerField(null=True,blank=True)
    Three_Mon_Avg_Sales =models.IntegerField(null=True,blank=True)
    Three_Mon_Avg_Sales_val =models.IntegerField(null=True,blank=True)
    LM_Sales =models.IntegerField(null=True,blank=True)
    LM_Sales_Val =models.IntegerField(null=True,blank=True)
    LMFC_Sales =models.IntegerField(null=True,blank=True)
    LMFC_Sales_Val=models.IntegerField(null=True,blank=True)
    LYSM1_Sales =models.IntegerField(null=True,blank=True)
    LYSM2_Sales =models.IntegerField(null=True,blank=True)
    LYSM3_Sales =models.IntegerField(null=True,blank=True)
    LYSM4_Sales =models.IntegerField(null=True,blank=True)
    LYSM5_Sales =models.IntegerField(null=True,blank=True)
    LYSM6_Sales =models.IntegerField(null=True,blank=True)
    LYSM1_Sales_Val =models.IntegerField(null=True,blank=True)
    LYSM2_Sales_Val =models.IntegerField(null=True,blank=True)
    LYSM3_Sales_Val =models.IntegerField(null=True,blank=True)
    LYSM4_Sales_Val =models.IntegerField(null=True,blank=True)
    LYSM5_Sales_Val =models.IntegerField(null=True,blank=True)
    LYSM6_Sales_Val =models.IntegerField(null=True,blank=True)
    YTM_AOP =models.IntegerField(null=True,blank=True)
    YTM_AOP_Val =models.IntegerField(null=True,blank=True)
    YTM_Sales =models.IntegerField(null=True,blank=True)
    YTM_Sales_Val =models.IntegerField(null=True,blank=True)
    LTSF_Sales=models.IntegerField(null=True,blank=True)
    LTSF_Sales_Val=models.IntegerField(null=True,blank=True)
    LYAS_Sales =models.IntegerField(null=True,blank=True)
    LYAS_Sales_Val =models.IntegerField(null=True,blank=True)
    M1_3SC_QTY =models.IntegerField(null=True,blank=True)
    M2_3SC_QTY =models.IntegerField(null=True,blank=True)
    M3_3SC_QTY =models.IntegerField(null=True,blank=True)
    M4_3SC_QTY =models.IntegerField(null=True,blank=True)
    M5_3SC_QTY =models.IntegerField(null=True,blank=True)
    M6_3SC_QTY =models.IntegerField(null=True,blank=True)
    M7_3SC_QTY =models.IntegerField(null=True,blank=True)
    M8_3SC_QTY =models.IntegerField(null=True,blank=True)
    M9_3SC_QTY =models.IntegerField(null=True,blank=True)
    M10_3SC_QTY =models.IntegerField(null=True,blank=True)
    M11_3SC_QTY =models.IntegerField(null=True,blank=True)
    M12_3SC_QTY =models.IntegerField(null=True,blank=True)
    M1_3SC_Val =models.IntegerField(null=True,blank=True)
    M2_3SC_Val =models.IntegerField(null=True,blank=True)
    M3_3SC_Val =models.IntegerField(null=True,blank=True)
    M4_3SC_Val =models.IntegerField(null=True,blank=True)
    M5_3SC_Val =models.IntegerField(null=True,blank=True)
    M6_3SC_Val =models.IntegerField(null=True,blank=True)
    M7_3SC_Val =models.IntegerField(null=True,blank=True)
    M8_3SC_Val =models.IntegerField(null=True,blank=True)
    M9_3SC_Val =models.IntegerField(null=True,blank=True)
    M10_3SC_Val =models.IntegerField(null=True,blank=True)
    M11_3SC_Val =models.IntegerField(null=True,blank=True)
    M12_3SC_Val =models.IntegerField(null=True,blank=True)
    M1_OPS_QTY =models.IntegerField(null=True,blank=True)
    M2_OPS_QTY =models.IntegerField(null=True,blank=True)
    M3_OPS_QTY =models.IntegerField(null=True,blank=True)
    M4_OPS_QTY =models.IntegerField(null=True,blank=True)
    M5_OPS_QTY =models.IntegerField(null=True,blank=True)
    M6_OPS_QTY =models.IntegerField(null=True,blank=True)
    M7_OPS_QTY =models.IntegerField(null=True,blank=True)
    M8_OPS_QTY =models.IntegerField(null=True,blank=True)
    M9_OPS_QTY =models.IntegerField(null=True,blank=True)
    M10_OPS_QTY =models.IntegerField(null=True,blank=True)
    M11_OPS_QTY =models.IntegerField(null=True,blank=True)
    M12_OPS_QTY =models.IntegerField(null=True,blank=True)
    M1_OPS_VAL =models.IntegerField(null=True,blank=True)
    M2_OPS_VAL =models.IntegerField(null=True,blank=True)
    M3_OPS_VAL =models.IntegerField(null=True,blank=True)
    M4_OPS_VAL =models.IntegerField(null=True,blank=True)
    M5_OPS_VAL =models.IntegerField(null=True,blank=True)
    M6_OPS_VAL =models.IntegerField(null=True,blank=True)
    M7_OPS_VAL =models.IntegerField(null=True,blank=True)
    M8_OPS_VAL =models.IntegerField(null=True,blank=True)
    M9_OPS_VAL =models.IntegerField(null=True,blank=True)
    M10_OPS_VAL =models.IntegerField(null=True,blank=True)
    M11_OPS_VAL =models.IntegerField(null=True,blank=True)
    M12_OPS_VAL =models.IntegerField(null=True,blank=True)
    M1_SALES_QTY =models.IntegerField(null=True,blank=True)
    M1_SALES_QTY =models.IntegerField(null=True,blank=True)
    M2_SALES_QTY =models.IntegerField(null=True,blank=True)
    M3_SALES_QTY =models.IntegerField(null=True,blank=True)
    M3_SALES_QTY =models.IntegerField(null=True,blank=True)
    M4_SALES_QTY =models.IntegerField(null=True,blank=True)
    M5_SALES_QTY =models.IntegerField(null=True,blank=True)
    M6_SALES_QTY =models.IntegerField(null=True,blank=True)
    M7_SALES_QTY =models.IntegerField(null=True,blank=True)
    M8_SALES_QTY =models.IntegerField(null=True,blank=True)
    M9_SALES_QTY =models.IntegerField(null=True,blank=True)
    M10_SALES_QTY =models.IntegerField(null=True,blank=True)
    M11_SALES_QTY =models.IntegerField(null=True,blank=True)
    M12_SALES_QTY =models.IntegerField(null=True,blank=True)
    M1_SALES_VAL =models.IntegerField(null=True,blank=True)
    M2_SALES_VAL =models.IntegerField(null=True,blank=True)
    M3_SALES_VAL =models.IntegerField(null=True,blank=True)
    M4_SALES_VAL =models.IntegerField(null=True,blank=True)
    M5_SALES_VAL =models.IntegerField(null=True,blank=True)
    M6_SALES_VAL =models.IntegerField(null=True,blank=True)
    M7_SALES_VAL =models.IntegerField(null=True,blank=True)
    M8_SALES_VAL =models.IntegerField(null=True,blank=True)
    M9_SALES_VAL =models.IntegerField(null=True,blank=True)
    M10_SALES_VAL =models.IntegerField(null=True,blank=True)
    M11_SALES_VAL =models.IntegerField(null=True,blank=True)
    M12_SALES_VAL =models.IntegerField(null=True,blank=True)
    M1_AOP_QTY =models.IntegerField(null=True,blank=True)
    M2_AOP_QTY =models.IntegerField(null=True,blank=True)
    M3_AOP_QTY =models.IntegerField(null=True,blank=True)
    M1_AOP_VAL =models.IntegerField(null=True,blank=True)
    M2_AOP_VAL =models.IntegerField(null=True,blank=True)
    M3_AOP_VAL =models.IntegerField(null=True,blank=True)
    M1_RTF_QTY=models.IntegerField(null=True,blank=True)
    M2_RTF_QTY=models.IntegerField(null=True,blank=True)
    M3_RTF_QTY=models.IntegerField(null=True,blank=True)
    M1_RTF_VAL=models.IntegerField(null=True,blank=True)
    M2_RTF_VAL=models.IntegerField(null=True,blank=True)
    M3_RTF_VAL=models.IntegerField(null=True,blank=True)
    M1_FINALFC_QTY =models.IntegerField(null=True,blank=True)
    M2_FINALFC_QTY =models.IntegerField(null=True,blank=True)
    M3_FINALFC_QTY =models.IntegerField(null=True,blank=True)
    M1_FINALFC_VAL =models.IntegerField(null=True,blank=True)
    M2_FINALFC_VAL =models.IntegerField(null=True,blank=True)
    M3_FINALFC_VAL =models.IntegerField(null=True,blank=True)
    L12_Min =models.IntegerField(null=True,blank=True)
    L12_Max =models.IntegerField(null=True,blank=True)
    L12_Min_VAL =models.IntegerField(null=True,blank=True)
    L12_Max_VAL =models.IntegerField(null=True,blank=True)
    M_1=models.IntegerField(null=True,blank=True)
    M_2=models.IntegerField(null=True,blank=True)
    M_3=models.IntegerField(null=True,blank=True)
    Status=models.CharField(choices=STATUS_CHOICES,max_length=10)
    Six_Mon_Avg_Forecast =models.IntegerField(null=True,blank=True)
    StockTill=models.IntegerField(null=True,blank=True)
    RemarkID=models.IntegerField(null=True,blank=True)
    Remark=models.IntegerField(null=True,blank=True)
    Active=models.CharField(max_length=10)
    Week1_ActualSales =models.IntegerField(null=True,blank=True)
    Week2_ActualSales =models.IntegerField(null=True,blank=True)
    Week3_ActualSales =models.IntegerField(null=True,blank=True)
    Week4_ActualSales =models.IntegerField(null=True,blank=True)
    First_Year =models.IntegerField(null=True,blank=True)
    FY_M1_QTY =models.IntegerField(null=True,blank=True)
    FY_M2_QTY =models.IntegerField(null=True,blank=True)
    FY_M3_QTY =models.IntegerField(null=True,blank=True)
    FY_M4_QTY =models.IntegerField(null=True,blank=True)
    FY_M5_QTY =models.IntegerField(null=True,blank=True)
    FY_M6_QTY =models.IntegerField(null=True,blank=True)
    FY_M7_QTY =models.IntegerField(null=True,blank=True)
    FY_M8_QTY =models.IntegerField(null=True,blank=True)
    FY_M9_QTY =models.IntegerField(null=True,blank=True)
    FY_M10_QTY =models.IntegerField(null=True,blank=True)
    FY_M11_QTY =models.IntegerField(null=True,blank=True)
    FY_M12_QTY =models.IntegerField(null=True,blank=True)
    FY_M1_Val =models.IntegerField(null=True,blank=True)
    FY_M2_Val =models.IntegerField(null=True,blank=True)
    FY_M3_Val =models.IntegerField(null=True,blank=True)
    FY_M4_Val =models.IntegerField(null=True,blank=True)
    FY_M5_Val =models.IntegerField(null=True,blank=True)
    FY_M6_Val =models.IntegerField(null=True,blank=True)
    FY_M7_Val =models.IntegerField(null=True,blank=True)
    FY_M8_Val =models.IntegerField(null=True,blank=True)
    FY_M9_Val =models.IntegerField(null=True,blank=True)
    FY_M10_Val =models.IntegerField(null=True,blank=True)
    FY_M11_Val =models.IntegerField(null=True,blank=True)
    FY_M12_Val =models.IntegerField(null=True,blank=True)
    Second_YEAR =models.IntegerField(null=True,blank=True)
    SY_M1_QTY =models.IntegerField(null=True,blank=True)
    SY_M2_QTY =models.IntegerField(null=True,blank=True)
    SY_M3_QTY =models.IntegerField(null=True,blank=True)
    SY_M4_QTY =models.IntegerField(null=True,blank=True)
    SY_M5_QTY =models.IntegerField(null=True,blank=True)
    SY_M6_QTY =models.IntegerField(null=True,blank=True)
    SY_M7_QTY =models.IntegerField(null=True,blank=True)
    SY_M8_QTY =models.IntegerField(null=True,blank=True)
    SY_M9_QTY =models.IntegerField(null=True,blank=True)
    SY_M10_QTY =models.IntegerField(null=True,blank=True)
    SY_M11_QTY =models.IntegerField(null=True,blank=True)
    SY_M12_QTY =models.IntegerField(null=True,blank=True)
    SY_M1_Val =models.IntegerField(null=True,blank=True)
    SY_M1_Val =models.IntegerField(null=True,blank=True)
    SY_M1_Val =models.IntegerField(null=True,blank=True)
    SY_M2_Val =models.IntegerField(null=True,blank=True)
    SY_M3_Val =models.IntegerField(null=True,blank=True)
    SY_M4_Val =models.IntegerField(null=True,blank=True)
    SY_M5_Val =models.IntegerField(null=True,blank=True)
    SY_M6_Val =models.IntegerField(null=True,blank=True)
    SY_M7_Val =models.IntegerField(null=True,blank=True)
    SY_M8_Val =models.IntegerField(null=True,blank=True)
    SY_M9_Val =models.IntegerField(null=True,blank=True)
    SY_M10_Val =models.IntegerField(null=True,blank=True)
    SY_M11_Val =models.IntegerField(null=True,blank=True)
    SY_M12_Val =models.IntegerField(null=True,blank=True)
    Third_YEAR =models.IntegerField(null=True,blank=True)
    TY_M1_QTY =models.IntegerField(null=True,blank=True)
    TY_M2_QTY =models.IntegerField(null=True,blank=True)
    TY_M3_QTY =models.IntegerField(null=True,blank=True)
    TY_M4_QTY =models.IntegerField(null=True,blank=True)
    TY_M5_QTY =models.IntegerField(null=True,blank=True)
    TY_M6_QTY =models.IntegerField(null=True,blank=True)
    TY_M7_QTY =models.IntegerField(null=True,blank=True)
    TY_M8_QTY =models.IntegerField(null=True,blank=True)
    TY_M9_QTY =models.IntegerField(null=True,blank=True)
    TY_M10_QTY =models.IntegerField(null=True,blank=True)
    TY_M11_QTY =models.IntegerField(null=True,blank=True)
    TY_M12_QTY =models.IntegerField(null=True,blank=True)
    TY_M1_Val =models.IntegerField(null=True,blank=True)
    TY_M2_Val =models.IntegerField(null=True,blank=True)
    TY_M3_Val =models.IntegerField(null=True,blank=True)
    TY_M4_Val =models.IntegerField(null=True,blank=True)
    TY_M5_Val =models.IntegerField(null=True,blank=True)
    TY_M6_Val =models.IntegerField(null=True,blank=True)
    TY_M7_Val =models.IntegerField(null=True,blank=True)
    TY_M8_Val =models.IntegerField(null=True,blank=True)
    TY_M9_Val =models.IntegerField(null=True,blank=True)
    TY_M10_Val =models.IntegerField(null=True,blank=True)
    TY_M11_Val =models.IntegerField(null=True,blank=True)
    TY_M12_Val =models.IntegerField(null=True,blank=True)
    CreatedDate =models.DateTimeField(auto_now=True)
    CreatedBy=models.ForeignKey(ScmUser, db_column = 'CreatedBy', on_delete=models.CASCADE)
    UpdatedDate=models.DateTimeField(auto_now=True)
    IPAddress=models.CharField(max_length=100,null=True,blank=True)
    class Meta:
        db_table = "FC_Details"

class Fc_Header(models.Model):
    Id = models.IntegerField(primary_key=True)
    TenantId= models.ForeignKey(Tenant,on_delete=models.CASCADE) 
    Forecast_No = models.CharField(max_length=300,null=True,blank=True) 
    Company_Code = models.CharField(max_length=300,null=True,blank=True) 
    FC_Month = models.CharField(max_length=300,null=True,blank=True) 
    FC_Year = models.CharField(max_length=300,null=True,blank=True) 
    FC_Generate_dt = models.CharField(max_length=300,null=True,blank=True) 
    ASM_Code = models.CharField(max_length=300,null=True,blank=True) 
    Territory = models.CharField(max_length=300,null=True,blank=True) 
    BranchID = models.ForeignKey(Branch,on_delete=models.CASCADE,default=None,blank=True,null=True) 
    BranchDesc = models.CharField(max_length=300,null=True,blank=True) 
    State_Code = models.CharField(max_length=300,null=True,blank=True) 
    State_Desc = models.CharField(max_length=300,null=True,blank=True) 
    Zone = models.CharField(max_length=300,null=True,blank=True) 
    Channel = models.ForeignKey(Channel,on_delete=models.CASCADE) 
    Channel_Desc = models.CharField(max_length=300,null=True,blank=True) 
    BU_Code = models.ForeignKey(BU,on_delete=models.CASCADE)
    Is_FC_Active = models.CharField(max_length=300,null=True,blank=True) 
    Is_ASM_Save = models.CharField(max_length=300,null=True,blank=True) 
    Is_ASM_Approve = models.CharField(max_length=300,null=True,blank=True) 
    FC_Status = models.CharField(max_length=300,null=True,blank=True) 
    FC_date = models.CharField(max_length=300,null=True,blank=True) 
    FC_Upload_on = models.CharField(max_length=300,null=True,blank=True) 
    FC_Upload_ip = models.CharField(max_length=300,null=True,blank=True) 
    FC_Approved_by = models.CharField(max_length=300,null=True,blank=True) 
    FC_Approved_on = models.CharField(max_length=300,null=True,blank=True) 
    FC_Approved_ip = models.CharField(max_length=300,null=True,blank=True) 
    FC_Last_Updated_by = models.CharField(max_length=300,null=True,blank=True) 
    FC_Last_Updated_on = models.CharField(max_length=300,null=True,blank=True) 
    FC_Last_Updated_ip = models.CharField(max_length=300,null=True,blank=True) 
    FC_PendingLevel = models.CharField(max_length=300,null=True,blank=True) 
    FC_PendingAt_Role = models.CharField(max_length=300,null=True,blank=True) 
    FC_PendingAt = models.CharField(max_length=300,null=True,blank=True) 
    FC_Upload_by = models.CharField(max_length=300,null=True,blank=True)
    class Meta:
        db_table = "Fc_Header"

class JobScheduler(models.Model):
    Id=models.AutoField(primary_key=True,unique=True)
    TenantId = models.ForeignKey(Tenant,db_column='TenantId',blank=True,null=True,on_delete=models.CASCADE) 
    Name=models.CharField(choices=JOB_NAME, max_length=200, null=False,blank=False)
    Frequency=models.CharField(choices=JOB_FREQUENCY, max_length=200, null=False,blank=False)
    DateTime=models.CharField(max_length=200,null=True,blank=True)
    Status=models.BooleanField(default=True,null=True,blank=True)
    UserType=models.CharField(choices=USER_TYPE, max_length=200, null=False,blank=False)
    CreatedDate=models.DateTimeField(auto_now_add=True)
    CreatedBy=models.ForeignKey(ScmUser,db_column='CreatedBy',on_delete=models.CASCADE,related_name='schedulerCreatedBy',null=True,blank=True)
    UpdatedDate=models.DateTimeField(auto_now=True,null=True,blank=True)
    UpdatedBy=models.CharField(max_length=200,null=True,blank=True)
    IPAddress=models.CharField(max_length=200,null=True,blank=True)
    
    class Meta:
        db_table = "JobScheduler"

class JobSchedulerDetails(models.Model):
    Id = models.AutoField(primary_key=True,unique=True)
    JobSchedulerId = models.ForeignKey(JobScheduler, db_column='JobSchedulerId', related_name='JobDetails', on_delete=models.CASCADE)
    DateTime = models.CharField(max_length=300)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    CreatedBy = models.ForeignKey(ScmUser,db_column='CreatedBy',on_delete=models.CASCADE,related_name='schedulerDetailsCreatedBy',null=True,blank=True)
    UpdatedDate = models.DateTimeField(auto_now=True,null=True,blank=True)
    UpdatedBy = models.CharField(max_length=200,null=True,blank=True)
    IPAddress = models.CharField(max_length=200,null=True,blank=True)
    
    class Meta:
        db_table = "JobSchedulerDetails"
    
class Job(models.Model):
    Id = models.AutoField(primary_key=True,unique=True)
    Name=models.CharField(choices=JOB_NAME, max_length=200, null=False,blank=False)
    JobScheduledDetailsId = models.ForeignKey(JobSchedulerDetails, db_column='JobScheduledDetailsId', related_name='JobData', on_delete=models.CASCADE)
    reason = models.TextField(null=True, blank=True)
    status=models.CharField(choices=JOB_STATUS, max_length=200, null=False,blank=False)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(auto_now=True,null=True,blank=True)
    UpdatedBy = models.CharField(max_length=200,null=True,blank=True)
    IPAddress = models.CharField(max_length=200,null=True,blank=True)
    
    class Meta:
        db_table = "Job"

class MSL_report(models.Model):
    Id = models.IntegerField(primary_key=True) 
    JobId = models.ForeignKey(Job,db_column="JobId",blank=True,null=True,on_delete=models.CASCADE)
    TenantId = models.ForeignKey(Tenant,db_column="TenantId",blank=True,null=True,on_delete=models.CASCADE) 
    BUId = models.ForeignKey(BU,db_column="BUId",blank=True,null=True,on_delete=models.CASCADE)
    BranchId = models.ForeignKey(Branch,db_column="BranchId",blank=True,null=True,on_delete=models.CASCADE)
    SKUId = models.ForeignKey(SKU_SNP,db_column="SKUId",blank=True,null=True,on_delete=models.CASCADE) 
    SKU_Code = models.CharField(max_length=200,blank=True,null=True) 
    DivisionId = models.ForeignKey(Division,db_column="DivisionId",blank=True,null=True,on_delete=models.CASCADE) 
    CategoryId = models.ForeignKey(Category,db_column="CategoryId",blank=True,null=True,on_delete=models.CASCADE)
    BrandId = models.ForeignKey(Brand,db_column="BrandId",blank=True,null=True,on_delete=models.CASCADE)
    MSL = models.CharField(max_length=200,blank=True,null=True) 
    PI = models.CharField(max_length=200,blank=True,null=True) 
    CS = models.CharField(max_length=200,blank=True,null=True) 
    SS = models.CharField(max_length=200,blank=True,null=True) 
    Demand = models.CharField(max_length=200,blank=True,null=True) 
    NLT = models.CharField(max_length=200,blank=True,null=True) 
    MLT = models.CharField(max_length=200,blank=True,null=True)
    RP = models.CharField(max_length=200,blank=True,null=True) 
    SP = models.CharField(max_length=200,blank=True,null=True) 
    STD = models.CharField(max_length=200,blank=True,null=True) 
    SPT = models.CharField(max_length=200,blank=True,null=True,default=2) 
    DailySales = models.CharField(max_length=200,blank=True,null=True) 
    MonthlySales = models.CharField(max_length=200,blank=True,null=True) 
    CurrentMSL = models.CharField(max_length=200,blank=True,null=True) 
    FinalMSL = models.CharField(max_length=200,blank=True,null=True) 
    Year = models.CharField(max_length=200,blank=True,null=True) 
    Month = models.CharField(max_length=200,blank=True,null=True) 
    Status = models.CharField(max_length=200,blank=True,null=True) 
    ApprovedBy = models.CharField(max_length=200,blank=True,null=True) 
    ApprovedDate = models.CharField(max_length=200,blank=True,null=True) 
    CreatedDate = models.DateTimeField(auto_now=True) 
    CreatedBy = models.ForeignKey(ScmUser,db_column="CreatedBy" ,blank=True,null=True,on_delete=models.CASCADE) 
    UpdatedDate = models.DateTimeField(blank=True,null=True) 
    UpdatedBy = models.CharField(max_length=200,blank=True,null=True) 
    IPAddress = models.CharField(max_length=200,blank=True,null=True)
    class Meta:
        db_table = "MSL_report"

class RPRules(models.Model):
    Id = models.IntegerField(primary_key=True)
    BU = models.ForeignKey(BU,db_column="BU",blank=True,null=True,on_delete=models.CASCADE)
    ConsiderMTO = models.BooleanField()
    MTO_RP_Rules = models.CharField(choices=MTO_RULES,max_length=250)
    STO_RP_Rules = models.CharField(choices=MTO_RULES,max_length=250)
    ForecastType = models.CharField(choices=FORECAST_TYPES,max_length=200)
    CreatedDate = models.DateTimeField(auto_now=True) 
    CreatedBy = models.ForeignKey(ScmUser,db_column="CreatedBy" ,blank=True,null=True,on_delete=models.CASCADE) 
    UpdatedDate = models.DateTimeField(blank=True,null=True) 
    UpdatedBy = models.CharField(max_length=200,blank=True,null=True) 
    IPAddress = models.CharField(max_length=200,blank=True,null=True)
    class Meta:
        db_table = "RPRules"
