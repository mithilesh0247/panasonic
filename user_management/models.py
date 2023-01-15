from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from scm_app.models import *

# Create your models here.

class RoleCategory(models.Model):
    Id = models.AutoField(primary_key=True,unique=True)
    TenantId = models.ForeignKey(Tenant,db_column='TenantId', on_delete=models.CASCADE)
    Code = models.CharField(max_length=50,null=True,blank=True)
    Name = models.CharField(max_length=300,null=True,blank=True)
    Description = models.TextField()
    CreatedDate = models.DateField(auto_now=True,null=False,blank=False)
    CreatedBy = models.ForeignKey(ScmUser,db_column='CreatedBy',on_delete=models.CASCADE)
    UpdatedDate = models.DateField(auto_now=True,null=True,blank=True)
    UpdatedBy = models.CharField(max_length=300,default=None,blank=True,null=True)
    IPAddress = models.CharField(max_length=300,null=True,blank=True)
    Status = models.BooleanField(default=False,null=False,blank=False)
    
    class Meta:
        db_table = "RoleCategory"

class Role(models.Model):
    Id = models.AutoField(primary_key=True,unique=True)	
    TenantId = models.ForeignKey(Tenant,db_column='TenantId', on_delete=models.CASCADE)
    ChannelId = models.ForeignKey(Channel,db_column='ChannelId', on_delete=models.CASCADE)
    BUId = models.ForeignKey(BU,db_column='BUId', on_delete=models.CASCADE)
    RoleCategoryId = models.ForeignKey(RoleCategory,db_column='RoleCategoryId', on_delete=models.CASCADE)
    Code = models.CharField(max_length=50,null=True,blank=True)
    Name = models.CharField(max_length=300,null=True,blank=True)
    Description = models.TextField()
    AuthLevel = models.IntegerField()	
    CreatedDate = models.DateField(auto_now=True,null=False,blank=False)
    CreatedBy = models.ForeignKey(ScmUser,db_column='CreatedBy',on_delete=models.CASCADE)
    UpdatedDate = models.DateField(auto_now=True,null=True,blank=True)
    UpdatedBy = models.CharField(max_length=300,default=None,blank=True,null=True)
    IPAddress = models.CharField(max_length=300,null=True,blank=True)
    Status = models.BooleanField(default=False,null=False,blank=False)
    
    class Meta:
        db_table = "Role"
        
class RolePermission(models.Model):
    Id = models.AutoField(primary_key=True,unique=True)
    RoleId = models.OneToOneField(Role,db_column='RoleId', on_delete=models.CASCADE)
    TenantMenuId = models.IntegerField(null=True,blank=True) # maybe a foreign key ---
    View = models.BooleanField(null=True,blank=True)
    Add = models.BooleanField(null=True,blank=True)
    Edit = models.BooleanField(null=True,blank=True)
    Delete = models.BooleanField(null=True,blank=True)
    CreatedDate = models.DateField(auto_now=True,null=False,blank=False)
    CreatedBy = models.ForeignKey(ScmUser,db_column='CreatedBy',on_delete=models.CASCADE)
    UpdatedDate = models.DateField(auto_now=True,null=True,blank=True)
    UpdatedBy = models.CharField(max_length=300,default=None,blank=True,null=True)
    IPAddress = models.CharField(max_length=300,null=True,blank=True)
    Status = models.BooleanField(default=False,null=False,blank=False)
    
    class Meta:
        db_table = "RolePermission"

class User(models.Model):
    Id = models.AutoField(primary_key=True,unique=True)
    TenantId = models.ForeignKey(Tenant,db_column='TenantId', on_delete=models.CASCADE)
    UserName = models.CharField(max_length=300,null=False,blank=False,unique=True)
    Email = models.EmailField(max_length=300,null=False,blank=False,unique=True)
    FirstName = models.CharField(max_length=300,null=False,blank=False)
    LastName = models.CharField(max_length=300,null=True,blank=True)
    EmailConfirmed = models.BooleanField(default=False,null=False,blank=False)
    Password = models.CharField(max_length=512,null=False,blank=False,)
    PhoneNo = PhoneNumberField()
    PhoneNoConfirmed = models.BooleanField(default=False,null=False,blank=False)
    LockoutEnd = models.DateField(auto_now=True,null=True,blank=True)
    LockoutEnabled = models.BooleanField()
    AccessFailedCount = models.PositiveIntegerField()
    RoleId = models.ForeignKey(Role,db_column='RoleId',related_name='RoleDetails', on_delete=models.CASCADE)
    BranchId = models.ForeignKey(Branch,db_column='BranchId', on_delete=models.CASCADE)
    TerritoryId = models.IntegerField(db_column='TerritoryId',)  # maybe a foreign key ---
    CreatedDate = models.DateField(auto_now=True,null=False,blank=False)
    CreatedBy = models.ForeignKey(ScmUser,db_column='CreatedBy',on_delete=models.CASCADE)
    UpdatedDate = models.DateField(auto_now=True,null=True,blank=True)
    UpdatedBy = models.CharField(max_length=300,default=None,blank=True,null=True)
    IPAddress = models.CharField(max_length=300,null=True,blank=True)
    Status = models.BooleanField(default=False,null=False,blank=False)
    
    class Meta:
        db_table = "User"

class UserToken(models.Model):
    Id = models.AutoField(primary_key=True,unique=True)
    UserId = models.OneToOneField(User,db_column='UserId',on_delete=models.CASCADE)
    Token = models.TextField(null=True,blank=False)
    CreatedDate = models.DateField(auto_now=True,null=False,blank=False)
    ExpiryDate = models.DateField(null=True,blank=True)
    IPAddress = models.CharField(max_length=300,null=True,blank=True)
    CreatedBy = models.ForeignKey(ScmUser,db_column='CreatedBy',on_delete=models.CASCADE)
    Status = models.BooleanField(default=False,null=False,blank=False)
    
    class Meta:
        db_table = "UserToken"