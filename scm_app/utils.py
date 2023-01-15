from . models import SKU_SNP,MSL_report,Branch_SKU,FC_Details,Fc_Header, Job,JobSchedulerDetails,SalesOrder
from django.db.models import Sum
import statistics
from datetime import datetime



def mslReport():
    print("============")
    scheduledJob = JobSchedulerDetails.objects.all().last()
    print(scheduledJob)
    JobReport = Job()
    JobReport.JobScheduledId = scheduledJob
    JobReport.Name = "MSL Planning"
    JobReport.status = "In-Process"
    JobReport.save()
    try:
        allskU=SKU_SNP.objects.all()
        for sku in allskU:
            # FOR NOW DEFAULT VALUES FOR NLT , RP AND STP
            MLT = sku.LeadTime  #Manufacturing Lead Time
            # NLT = int(MLT.) + 2
            # NLT = int(10) + 2
            Branch_sku_data = Branch_SKU.objects.filter(SkuId =sku)
            for branch_data in Branch_sku_data:
                NLT = 6
                RP = 3
                STP = 4
                current_msl = branch_data
                if current_msl:
                    current_msl = branch_data.MSL
                else:
                    current_msl = '--'
                Forecast_No = Fc_Header.objects.filter(TenantId=sku.TenantId,BU_Code=sku.BUId)#,BranchID__Id=branch_data.BranchId.Id)
                Forecast_No = Forecast_No.order_by('-FC_date').first()
                year = datetime.now().year
                month = datetime.now().month
                if Forecast_No:
                    """
                    have to send current month here for now under fcdetails
                    """
                    key_to_filter = str(month)
                    key_to_filter = 'M'+key_to_filter+'_3SC_QTY'
                    print(sku.Id,"Forecast_No.Forecast_No ", Forecast_No.Forecast_No,"Forecast_No.BranchID",Forecast_No.BranchID.Id," Forecast_No.Channel ",Forecast_No.Channel.Id)
                    ForeCastDemand = FC_Details.objects.filter(SKUId=sku,Forecast_No=Forecast_No.Forecast_No,BranchId=Forecast_No.BranchID,ChannelId=Forecast_No.Channel).values(
                            key_to_filter).distinct() # current month caluculation for 3 months
                            # 'M1_3SC_QTY','M2_3SC_QTY','M3_3SC_QTY','M4_3SC_QTY','M5_3SC_QTY','M6_3SC_QTY','M7_3SC_QTY','M8_3SC_QTY','M9_3SC_QTY','M10_3SC_QTY','M11_3SC_QTY','M12_3SC_QTY').distinct() # current month caluculation for 3 months
                    ForeCastDemand = ForeCastDemand.first()
                    if ForeCastDemand:
                        ForeCastDemandList = list(ForeCastDemand.values())
                    else:
                        ForeCastDemandList = [0]
                   
                    # D = sum()
                    Demand = sum(ForeCastDemandList)   
                    PI = NLT * Demand # D is demand & NLT= Net Lead Time
                    """
                    D= Qty based on historical
                    Sales / Forecast Qty

                    NLT= MLT(Manufacturing Lead Time) + Transport Lead time b/w WH to CDC + Transport Lead time b/w CDC to branch
                    """
                    CS = Demand * RP #RP= Replenishment Period
                    """
                    RP= Dispatching Freq.(days) at CDCs & WH. [ Obtained from 1 year Inbound Data – Source to customer]
                    """        
                    std_data = [0,0,0,0,0,0]
                    #last 6 month sale from sale order table Have to check || item sale 
                    SalesDemand = SalesOrder.objects.filter(warehouse_Code__Id=Forecast_No.BranchID.Id,item_code__Id=sku.Id)
                    if SalesDemand:
                        if month > 5:
                            month_range = list(range(month-6,month+1))
                            std_data = SalesDemand.filter(Order_Date__month__gte=month-6,Order_Date__year=year).values('totalquantity')
                            std_data = list(map(lambda d: int(d['totalquantity']), std_data))
                        else:
                            month_range =list(range(0,month+1))
                            std_data = SalesDemand.filter(Order_Date__month__in=month_range,Order_Date__year=year).values('totalquantity')
                            left_month = 6-month
                            std_data = list(map(lambda d: int(d['totalquantity']), std_data))
                            left_month_range = list(range(12-left_month,13))
                            left_std_data = SalesDemand.filter(Order_Date__month__in=left_month_range,Order_Date__year=year-1).values('totalquantity')
                            left_std_data = list(map(lambda d: int(d['totalquantity']), left_std_data))
                            std_data = std_data + left_std_data
                    STD = statistics.stdev(std_data) # for STANDARD DEVIATION 
                    """
                    Have to define standard deviation here!
                    """
                    # STD = 10 # HAVE TO MAKE IT DYNAMIC 
                    SS = ((Demand**2)*(STP**2) + (RP + NLT)*(STD**2)) # multiplying by 0.5 to find square root of data
                    SS = SS ** 0.5
                    #FORMULA FOR MSL FINAL FORMULA
                    MSL = PI + CS + SS 
                    """
                    PI is Pipeline inventory
                    CS is  Cyclic Stock
                    SS is Safety Stock
                    """
                    # Code for generating MSL report into Database.
                    MSL_COUNT = list(MSL_report.objects.all())
                    if len(MSL_COUNT) > 0:
                        MSL_COUNT = len(MSL_COUNT) + 1
                    else:
                        MSL_COUNT = 1

                    msl_report_generation = MSL_report()        
                    msl_report_generation.Id = MSL_COUNT
                    msl_report_generation.JobId = JobReport
                    msl_report_generation.TenantId = sku.TenantId
                    msl_report_generation.BUId = sku.BUId
                    msl_report_generation.BranchId = Forecast_No.BranchID
                    msl_report_generation.SKUId = sku
                    msl_report_generation.SKU_Code = sku.Code
                    msl_report_generation.DivisionId = sku.DivisionId
                    msl_report_generation.CategoryId = sku.CategoryId
                    msl_report_generation.BrandId = sku.Brand
                    msl_report_generation.MSL = MSL
                    msl_report_generation.PI = PI
                    msl_report_generation.CS = CS
                    msl_report_generation.SS = SS
                    msl_report_generation.Demand = Demand
                    msl_report_generation.NLT = NLT
                    msl_report_generation.MLT = MLT
                    msl_report_generation.RP = RP
                    # msl_report_generation.SP = ""
                    msl_report_generation.STD = STD
                    # msl_report_generation.DailySales = ""
                    # msl_report_generation.MonthlySales = ""
                    msl_report_generation.CurrentMSL = current_msl
                    msl_report_generation.FinalMSL = MSL
                    msl_report_generation.Year = year
                    msl_report_generation.Month = month
                    msl_report_generation.Status = 1
                    # msl_report_generation.ApprovedBy = ""
                    # msl_report_generation.ApprovedDate = ""
                    # msl_report_generation.CreatedBy =
                    # msl_report_generation.UpdatedDate =
                    # msl_report_generation.UpdatedBy =
                    # msl_report_generation.IPAddress =
                    msl_report_generation.save()
                    msl_report_generation.UpdatedDate = msl_report_generation.CreatedDate
                    msl_report_generation.save()
        
        msl_report = MSL_report.objects.all().values().order_by('-Id')[:10]
        JobReport.status = "Complete"
        JobReport.save()
        return msl_report
    except Exception as e:
        JobReport.status = "Failed"
        JobReport.reason = str(e)
        JobReport.save()
        return str(e)


def query_set_for_filter(data,search_for=None):
    dictionary_filter = {}
    if data.get("search") and search_for:
        dictionary_filter[search_for+"__Name__icontains"] = data.get("search")
    elif data.get("search"):
        dictionary_filter["Name__icontains"] = data.get("search")
    if data.get("from_date"):
        dictionary_filter["CreatedDate__gte"] = data["from_date"]
    if data.get("to_date"):
        dictionary_filter["CreatedDate__lte"] = data["to_date"]
    return dictionary_filter
