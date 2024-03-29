from django.shortcuts import render
from django.core.files.uploadedfile import TemporaryUploadedFile
import json
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse, HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.urls import reverse 
from django.http import QueryDict
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView
from django.contrib.auth import get_user_model
from .models import IcnReport, ActivityReport, ActivityReportImpact,ActivityReportImplementationArea,  IcnReportImplementationArea,  Impact, IcnReportSubmit, IcnReportDocument,  IcnReportSubmitApproval_P, IcnReportSubmitApproval_F, IcnReportSubmitApproval_T, ActivityReportDocument, ActivityReportSubmit, ActivityReportSubmitApproval_F,ActivityReportSubmitApproval_P,ActivityReportSubmitApproval_T, IcnReportImpact, ActivityImpact
from .forms import IcnReportForm, ActivityReportForm,ActivityReportImpactForm, ActivityReportImpactForm, ActivityReportAreaFormE, IcnReportAreaFormE, IcnReportSubmitForm,  IcnReportDocumentForm, IcnReportApprovalTForm, IcnReportApprovalFForm, IcnReportApprovalPForm, ActivityReportSubmitForm, ActivityReportDocumentForm, ActivityReportApprovalFForm, ActivityReportApprovalPForm,ActivityReportApprovalTForm,IcnReportImpactForm
from program.models import  Program
from django.http import QueryDict
from django.conf import settings
from django.core.mail import send_mail
from django.forms.models import modelformset_factory
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.db.models import Max, Avg,Sum,Count
from conceptnote.models import Icn, Activity, IcnImplementationArea
from django.forms import formset_factory 
from django.views.generic.edit import CreateView
from django.utils import timezone
# Create your views here.


def icnreports(request):
    if IcnReport.objects.exists():
        reports = IcnReport.objects.all().order_by('-id')
        icns = Icn.objects.all().order_by('-id')
        context = {'reports':reports, 'icns':icns}
    else:
        icns = Icn.objects.all().order_by('-id')
        context = {'icns':icns}
    
    return render(request, 'report/reports.html', context)

def icnreport_add(request, id): 
    icn = Icn.objects.get(pk=id)
    impacts =  Impact.objects.filter(icn_id=2)
    if request.method == "POST":
        form = IcnReportForm(request.POST,request.FILES, user=request.user, icn=icn)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            
            instance.save()
           
            for impact in impacts:
                 IcnReportImpact.objects.create(icnreport=instance, impact=impact)
            return redirect('icnreport_detail',instance.pk) 
        
        
        form = IcnReportForm(request.POST,request.FILES, user=request.user, icn=icn)   
        context = {'form':form}
        return render(request, 'report/icnreport_add.html', context)
    
    form = IcnReportForm(user=request.user, icn=icn)   
    context = {'form':form, 'icn':icn}
    return render(request, 'report/icnreport_add.html', context)



 
def icnreport_edit(request, id): 
    icnreport = IcnReport.objects.get(pk=id)
    icn = Icn.objects.get(pk=id)
    impacts = Impact.objects.filter(icn_id=id)
    
    if request.method == "POST":
       
        form = IcnReportForm(request.POST,request.FILES, instance=icnreport, user=request.user)
        if form.is_valid():
            instance = form.save()
            
            return redirect('icnreport_detail',instance.pk) 
        
        form = IcnReportForm(request.POST, request.FILES, instance=icnreport, user=request.user, icn=icn) 
        context = {'form':form, 'icn':icn, 'icnreport':icnreport}
        return render(request, 'report/icnreport_add.html', context)
            
    elif request.method == "GET" and icnreport.status == False:    

        form = IcnReportForm(instance=icnreport,  user=request.user, icn=icn) 
        context = {'form':form, 'icn':icn, 'icnreport':icnreport}
        return render(request, 'report/icnreport_add.html', context)
    else:
        return HttpResponseRedirect(request.path_info)
                


 
def icnreport_detail(request, pk):
    
    context ={}
 
    # add the dictionary during initialization
  
    icnreport = IcnReport.objects.get(pk=pk)
   
    if IcnReportSubmit.objects.filter(icnreport_id=icnreport.id).exists():
        icnreportsubmit = IcnReportSubmit.objects.filter(icnreport_id=icnreport.id).latest('id')
        context = {'icnreport':icnreport, 'icnreportsubmit':icnreportsubmit}
    else:
        context = {'icnreport':icnreport}
    
    #icnsubmit= IcnReportSubmit.objects.filter(icnreport_id=icnreport.id).latest('id')
    #icnsubmit = get_object_or_404(IcnReportSubmit, icnreport_id=icnreport.id).latest('id')


    return render(request, 'report/icnreport_detail.html', context)


 



def icnreport_submit_form(request, id): 
    icnreport = get_object_or_404(IcnReport, pk=id)
    form = IcnReportSubmitForm(user=request.user,icnreport=icnreport)
    
    subject = 'Request for Approval'
    
    message = 'A new Intervention Concept Note has been submitted'
    email_from = None 
    recipient_list = [icnreport.user.email,icnreport.technical_lead.user.email, icnreport.program_lead.user.email, icnreport.finance_lead.user.email]

    if request.method == "POST":
        form = IcnReportSubmitForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.icnreport = icnreport
            
            instance.user = request.user
            instance.save()
            #document = IcnReportSubmit.objects.filter(icnreport_id=icnreport.id).latest('id')
            #document_i = Document.objects.filter(icnreport=instance.icnreport, user=icnreport.user).count()+1
            
            icnreportsubmit = get_object_or_404(IcnReportSubmit, pk=instance.pk)
            #Document.objects.create(user = icnreport.user, document = instance.document,  icnreport=instance.icnreport, description = document_i)
            if icnreportsubmit.submission_status == 2:
                IcnReport.objects.filter(pk=id).update(status=True)
                IcnReport.objects.filter(pk=id).update(approval_status="Pending")
                IcnReportSubmitApproval_T.objects.create(user = icnreport.technical_lead,submit_id = instance, document = instance.document, approval_status=1)
                IcnReportSubmitApproval_P.objects.create(user = icnreport.program_lead,submit_id = instance,document = instance.document, approval_status=1)
                IcnReportSubmitApproval_F.objects.create(user = icnreport.finance_lead,submit_id = instance,document = instance.document, approval_status=1)

                send_mail(subject, message, email_from, recipient_list)
                return HttpResponse(
                status=204,
                headers={
                    'HX-Trigger': json.dumps({
                        "SubmitApprovalListChanged": None,
                        "showMessage": f"{instance.id} added."
                    })
                })
            elif icnreportsubmit.submission_status == 1:
                IcnReport.objects.filter(pk=id).update(status=False)
                IcnReport.objects.filter(pk=id).update(approval_status="Pending Submission")
                subject = 'Request withdrawn temporarly'
                message = "The Intervention Concept Note approval request has been withdrawn for further update/changes & will notify you when it's re-submitted for approval process"
                send_mail(subject, message, email_from, recipient_list)
                return HttpResponse(
                status=204,
                headers={
                    'HX-Trigger': json.dumps({
                        "SubmitApprovalListChanged": None,
                        "showMessage": f"{instance.id} added."
                    })
                })

      
    context = {'form':form, 'icnreport':icnreport}
    return render(request, 'report/icnreport_submit_form copy.html', context)

def icnreport_submit_detail(request, pk):
    
    context ={}
 
    # add the dictionary during initialization
  
    icnreportsubmit = IcnReportSubmit.objects.get(pk=pk,  submission_status=2)
    
   

    context = {'icnreportsubmit':icnreportsubmit}

    return render(request, 'report/icnreportsubmit_detail.html', context)

 
def icnreport_approvalt(request, id):
     
    icnreportsubmitApproval_t = get_object_or_404(IcnReportSubmitApproval_T, submit_id_id=id)
    icnreportsubmit = get_object_or_404(IcnReportSubmit, pk=id)
    
    icnreport =  get_object_or_404(IcnReport, id=icnreportsubmit.icnreport_id)
    subject = 'Approval Status changed'
    message = 'Reviewed & status has been updated to this Concept Note has been submitted'
    email_from = None 
    recipient_list = [icnreport.technical_lead.user.email, icnreport.program_lead.user.email, icnreport.finance_lead.user.email]
       
    if request.method == "GET":
        icnreportsubmitApproval_t = get_object_or_404(IcnReportSubmitApproval_T, submit_id_id=id)
        form = IcnReportApprovalTForm(instance=icnreportsubmitApproval_t)
        context = {'icnreportsubmitapproval_t':icnreportsubmitApproval_t, 'form': form, 'icnreport':icnreport, }
        return render(request, 'report/icnreport_approval_tform.html', context)
    
    elif request.method == "PUT":
        icnreportsubmitApproval_t = get_object_or_404(IcnReportSubmitApproval_T, submit_id_id=id)
        data = QueryDict(request.body).dict()
        form = IcnReportApprovalTForm(data, instance=icnreportsubmitApproval_t)
        if form.is_valid():
            instance =form.save()
            IcnReport.objects.filter(pk=id).update(status=True)
            icnreportsubmit = get_object_or_404(IcnReportSubmit, pk=id)
            icnreport =  get_object_or_404(IcnReport, id=icnreportsubmit.icnreport_id)
            update_approval_status(icnreportsubmit.id)
            context = {'icnreport':icnreport, 'icnreportsubmit':icnreportsubmit }
            send_mail(subject, message, email_from, recipient_list)
            return HttpResponse(
                status=204,
                headers={
                    'HX-Trigger': json.dumps({
                        "SubmitApprovalListChanged": None,
                        "showMessage": f"{instance.id} added."
                    })
                })
        
        return render(request, 'report/icnreport_approval_tform.html', {'form':form})
  

def icnreport_approvalp(request, id):
    
    icnreportsubmitApproval_p = get_object_or_404(IcnReportSubmitApproval_P, submit_id_id=id)
    icnreportsubmit = get_object_or_404(IcnReportSubmit, pk=id)
    
    icnreport =  get_object_or_404(IcnReport, id=icnreportsubmit.icnreport_id)
    subject = 'Approval Status changed'
    message = 'Reviewed & status has been updated to this Concept Note has been submitted'
    email_from = None 
    recipient_list = [icnreport.user ,icnreport.technical_lead.user.email, icnreport.program_lead.user.email, icnreport.finance_lead.user.email]
       
    if request.method == "GET":
        icnreportsubmitApproval_p = get_object_or_404(IcnReportSubmitApproval_P, submit_id_id=id)
        form = IcnReportApprovalPForm(instance=icnreportsubmitApproval_p)
        context = {'icnreportsubmitapproval_p':icnreportsubmitApproval_p, 'form': form, 'icnreport':icnreport, }
        return render(request, 'report/icnreport_approval_pform.html', context)
    
    elif request.method == "PUT":
        icnreportsubmitApproval_p = get_object_or_404(IcnReportSubmitApproval_P, submit_id_id=id)
        data = QueryDict(request.body).dict()
        form = IcnReportApprovalPForm(data, instance=icnreportsubmitApproval_p)
        if form.is_valid():
            instance = form.save()
            icnreportsubmit = get_object_or_404(IcnReportSubmit, pk=id)
            update_approval_status(icnreportsubmit.id)
            icnreport =  get_object_or_404(IcnReport, id=icnreportsubmit.icnreport_id)
            context = {'icnreport':icnreport, 'icnreportsubmit':icnreportsubmit }
            send_mail(subject, message, email_from, recipient_list)
            return HttpResponse(
                status=204,
                headers={
                    'HX-Trigger': json.dumps({
                        "SubmitApprovalListChanged": None,
                        "showMessage": f"{instance.id} added."
                    })
                })
        
        return render(request, 'report/icnreport_approval_pform.html', {'form':form})


 
def icnreport_approvalf(request, id):
    icnreportsubmitApproval_f = get_object_or_404(IcnReportSubmitApproval_F, submit_id_id=id)
    icnreportsubmit = get_object_or_404(IcnReportSubmit, pk=id)
    
    icnreport =  get_object_or_404(IcnReport, id=icnreportsubmit.icnreport_id)
    subject = 'Approval Status changed'
    message = 'Reviewed & status has been updated to this Concept Note has been submitted'
    email_from = None 
    recipient_list = [icnreport.user ,icnreport.technical_lead.user.email, icnreport.program_lead.user.email, icnreport.finance_lead.user.email]
       
    if request.method == "GET":
        icnreportsubmitApproval_f = get_object_or_404(IcnReportSubmitApproval_F, submit_id_id=id)
        form = IcnReportApprovalFForm(instance=icnreportsubmitApproval_f)
        context = {'icnreportsubmitapproval_f':icnreportsubmitApproval_f, 'form': form, 'icnreport':icnreport, }
        return render(request, 'report/icnreport_approval_fform.html', context)
    
    elif request.method == "PUT":
        icnreportsubmitApproval_f = get_object_or_404(IcnReportSubmitApproval_F, submit_id_id=id)
        data = QueryDict(request.body).dict()
        form = IcnReportApprovalFForm(data, instance=icnreportsubmitApproval_f)
        if form.is_valid():
            instance = form.save()
            icnreportsubmit = get_object_or_404(IcnReportSubmit, pk=id)
            update_approval_status(icnreportsubmit.id)
            icnreport =  get_object_or_404(IcnReport, id=icnreportsubmit.icnreport_id)
            context = {'icnreport':icnreport, 'icnreportsubmit':icnreportsubmit }
            send_mail(subject, message, email_from, recipient_list)
            return HttpResponse(
                status=204,
                headers={
                    'HX-Trigger': json.dumps({
                        "SubmitApprovalListChanged": None,
                        "showMessage": f"{instance.id} added."
                    })
                })
        
        return render(request, 'report/icnreport_approval_fform.html', {'form':form})

def icnreport_submit_approval(request, pk):
    icnreport = get_object_or_404(IcnReport, pk=pk)
    context ={}
 
    # add the dictionary during initialization
    icnreport = IcnReport.objects.get(pk=pk)
    if IcnReportSubmit.objects.filter(icnreport_id=icnreport.id).exists():
        icnreportsubmit = IcnReportSubmit.objects.filter(icnreport_id=icnreport.id).latest('id')
        context = {'icnreport':icnreport, 'icnreportsubmit':icnreportsubmit}
    else:
        context = {'icnreport':icnreport}
    

    return render(request, 'report/icnreport_submit_approval.html', context)

 
def icnreport_submit_list(request, id):
    context ={}
 
    # add the dictionary during initialization
  
    icnreport = IcnReport.objects.get(pk=id)
    if IcnReportSubmit.objects.filter(icnreport_id=icnreport.id).exists():
        icnsubmit = IcnReportSubmit.objects.filter(icnreport_id=icnreport.id).latest('id')
        context = {'icnreport':icnreport, 'icnsubmit':icnsubmit}
    else:
        context = {'icnreport':icnreport}

    return render(request, 'report/partial/submit_list.html', context)


 
def icnreport_submit_document(request, id):
    context ={}
    icnreport = get_object_or_404(IcnReport, pk=id)
    dform = IcnReportDocumentForm()
    major = IcnReportDocument.objects.filter(icnreport=icnreport.id, user=icnreport.user).count() 
    minor = IcnReportDocument.objects.filter(icnreport=icnreport.id).exclude(user=icnreport.user)
    minor = minor.count()
    context = {'dform':dform}
    if request.method == 'POST':
        dform = IcnReportDocumentForm(request.POST, request.FILES)
        if dform.is_valid():
            instance = dform.save(commit=False)
            instance.icnreport = icnreport
            instance.user = request.user
            if instance.user == icnreport.user:
                 major = major + 1
                 minor = minor
            else:
                 major = major 
                 minor = minor + 1
              
            instance.ver = "%s%s%s" %(major,'.',minor)

            instance.save()
            
            
            return HttpResponse(
                status=204,
                headers={
                    'HX-Trigger': json.dumps({
                        "DocListChanged": None,
                        "showMessage": f"{instance.id} added."
                    })
                })
            
    else:
       dform = IcnReportDocumentForm()
       context = {'dform':dform}
       return render(request, 'report/partial/icnreport_document_form copy.html', context)
           
            
       
   
       
def document_list(request, id):
    documents = IcnReportDocument.objects.filter(icnreport_id=id)
    context = {'documents':documents}
           
          
    
    return render(request,'report/partial/icnreport_document_list.html', context)
       


def download(request, id):
    document = get_object_or_404(IcnReportDocument, id=id)
    response = HttpResponse(document.document, content_type='application/docx')
    response['Content-Disposition'] = f'attachment; filename="{document.document}"'
    return response


def icnreport_filter(request):
    query = request.GET.get('search', '')
    print(query)
    if query:
        qs1 = IcnReport.objects.filter(icn__title__icontains=query)
        qs2 = IcnReport.objects.distinct().filter(icn__program__title__icontains=query)
        
        
        icnreports = qs1.union(qs2).order_by('id')
    else:
        icnreports = IcnReport.objects.all()

    context = {'icnreports': icnreports, }
    return render(request, 'partial/icnreport_list.html', context)













def submit_approval_list(request, id):
    icnreport_submit_list = IcnReportSubmit.objects.filter(icnreport_id = id, submission_status=2)
    
    context = {'icnreport_submit_list': icnreport_submit_list }
    return render(request, 'report/partial/icnreport_submit_approval_list.html', context )

def current_submit_approval_list(request, id):
    
    icnreport = IcnReport.objects.get(pk=id)
    if IcnReportSubmit.objects.filter(icnreport_id=icnreport.id).exists():
        icnreportsubmit = IcnReportSubmit.objects.filter(icnreport_id=icnreport.id).latest('id')
        context = {'icnreport':icnreport, 'icnreportsubmit':icnreportsubmit}
    else:
        context = {'icnreport':icnreport}
  
    
    return render(request, 'report/partial/icnreport_submit_list.html', context)

def update_approval_status(id):
    icnsubmit = get_object_or_404(IcnReportSubmit, pk=id)
    icnsubmitapproval_t = get_object_or_404(IcnReportSubmitApproval_T, submit_id_id=id)
    icnsubmitapproval_p = get_object_or_404(IcnReportSubmitApproval_P, submit_id_id=id)
    icnsubmitapproval_f = get_object_or_404(IcnReportSubmitApproval_F, submit_id_id=id)
    
    approval_t = icnsubmitapproval_t.approval_status
    approval_p = icnsubmitapproval_p.approval_status
    approval_f = icnsubmitapproval_f.approval_status
    
    if approval_t == 4 or approval_p== 4 or approval_f== 4:
        IcnReport.objects.filter(pk=icnsubmit.icnreport_id).update(approval_status="Rejected")
    elif approval_t < 3 and approval_p < 3 and approval_p < 3:
        IcnReport.objects.filter(pk=icnsubmit.icnreport_id).update(approval_status="Pending Approval")
    elif approval_t == 3 and approval_p ==3 and approval_f==3:
         IcnReport.objects.filter(pk=icnsubmit.icnreport_id).update(approval_status="100% Approved")
    elif (approval_t == 3 and approval_p ==3 and approval_f !=3) or (approval_t == 3 and approval_p !=3 and approval_f ==3) or (approval_t != 3 and approval_p ==3 and approval_f ==3):
        IcnReport.objects.filter(pk=icnsubmit.icnreport_id).update(approval_status="67% Approved")
    elif (approval_t == 3 and approval_p !=3 and approval_f !=3) or (approval_t != 3 and approval_p ==3 and approval_f !=3) or (approval_t != 3 and approval_p !=3 and approval_f ==3):
        IcnReport.objects.filter(pk=icnsubmit.icnreport_id).update(approval_status="33% Approved") 
        
    

    
def add_icnreport_impact(request, id):
    icnreport = get_object_or_404(IcnReport, pk=id)
   
    
    if request.method == "POST":
        myformset = formset_factory(IcnReportImpactForm) 
        formset = myformset() 
        formset = formset(request.POST or None)
        if formset.is_valid():
            for form in formset:
                instance = form.save(commit=False)
                instance.icnreport = icnreport
                instance.save()
            
               
            return HttpResponse(
                status=204,
                headers={
                    'HX-Trigger': json.dumps({
                        "ImpactListChanged": None,
                        "showMessage": f"{instance.icnreport} added."
                    })
                })
    else:
        myformset = formset_factory(IcnReportImpactForm) 
        formset = myformset() 
        formset = formset()
    return render(request, 'partial/impact_form.html', {
        'formset': formset,
    })


def icnreport_impact_list(request, id):
    impacts = IcnReportImpact.objects.filter(icnreport_id=id)
    context = {'impacts':impacts}
    return render(request, 'report/partial/impact_list.html', context)


def edit_impact(request, pk):
    impact = get_object_or_404(IcnReportImpact, pk=pk)
    icnreport = get_object_or_404(IcnReport, pk=impact.icnreport_id)
    
   
    if request.method == "POST":
        impact = IcnReportImpact.objects.get(pk=pk)
        form = IcnReportImpactForm(request.POST, instance=impact)
        if form.is_valid():
            instance = form.save()
            return HttpResponse(
                status=204,
                headers={
                    'HX-Trigger': json.dumps({
                        "ImpactListChanged": None,
                        "showMessage": f"{instance.pk} updated."
                    })
                })
    else:
        form = IcnReportImpactForm(instance=impact)
    return render(request, 'report/partial/impact_form_edit.html', {
        'form': form,
        'impact': impact,
    })

def icnreport_remove_impact(request, pk):
    impact = get_object_or_404(Impact, pk=pk)
    impact.delete()
    return HttpResponse(
        status=204,
        headers={
            'HX-Trigger': json.dumps({
                "ImpactListChanged": None,
                "showMessage": f"{impact} deleted."
            })
        })


def download_env_att(request, id):
    document = get_object_or_404(IcnReport, id=id)
    response = HttpResponse(document.environmental_assessment_att, content_type='application/docx')
    response['Content-Disposition'] = f'attachment; filename="{document.environmental_assessment_att}"'
    return response

def icnreport_submit_form_partial(request, id): 
    icnreport = get_object_or_404(IcnReport, pk=id)
    form = IcnReportSubmitForm(user=request.user,icnreport=icnreport)
    
    context = {'form':form, 'icnreport':icnreport}
    return render(request, 'report/partial/icnreport_partial_doc_form.html', context)

 
def activitiesreport(request):
    if ActivityReport.objects.exists():
        reports = ActivityReport.objects.all().order_by('-id')
        acns = Activity.objects.all().order_by('-id')
        context = {'reports':reports, 'acns':acns}
    else:
        acns = Activity.objects.all().order_by('-id')
        context = {'acns':acns}
    
    
    return render(request, 'report/activitiesreport.html', context)

 
def activityreport_detail(request, pk):
    
    context ={}
 
    # add the dictionary during initialization
  
    activityreport = ActivityReport.objects.get(pk=pk)

    context = {'activityreport':activityreport}
    
    #icnsubmit= IcnReportSubmit.objects.filter(icnreport_id=icnreport.id).latest('id')
    #icnsubmit = get_object_or_404(IcnReportSubmit, icnreport_id=icnreport.id).latest('id')


    return render(request, 'report/activityreport_detail.html', context)

 
def activityreport_add(request, id): 
    acn = Activity.objects.get(pk=id)
    aimpacts =  ActivityImpact.objects.filter(activity_id=id)
    if request.method == "POST":
        form = ActivityReportForm(request.POST,request.FILES, user=request.user, acn=acn)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
           
            instance.save()
           
            for aimpact in aimpacts:
                 ActivityReportImpact.objects.create(activityreport=instance, activityimpact=aimpact)
            return redirect('activityreport_detail',instance.pk) 
        
        
        form = ActivityReportForm(request.POST,request.FILES, user=request.user, acn=acn)   
        context = {'form':form, 'acn':acn}
        return render(request, 'report/activityreport_add.html', context)
    
    form = ActivityReportForm(user=request.user, acn=acn)   
    context = {'form':form, 'acn':acn}
    return render(request, 'report/activityreport_add.html', context)

 
def activityreport_edit(request, id): 
    activityreport = ActivityReport.objects.get(pk=id)
    acn = Activity.objects.get(pk=id)
    
    if request.method == "POST":
       
        form = ActivityReportForm(request.POST, instance=activityreport, user=request.user)
        if form.is_valid():
            instance = form.save()
            return redirect('activityreport_detail',instance.pk) 
        
        form = ActivityReportForm(request.POST,  instance=activityreport, user=request.user, acn=acn) 
        context = {'form':form, 'acn':acn}
        return render(request, 'report/activityreport_add.html', context)
            
    elif request.method == "GET" and activityreport.status == False:    

        form = ActivityReportForm(instance=activityreport,  user=request.user, acn=acn) 
        context = {'form':form, 'acn':acn}
        return render(request, 'report/activityreport_add.html', context)
    else:
        return HttpResponseRedirect(request.path_info)
    
 

def add_activityreport_impact(request, id):
    activityreport = get_object_or_404(ActivityReport, pk=id)
    icnreport = get_object_or_404(IcnReport, pk=activityreport.icnreport_id)
    
    if request.method == "POST":
        form = ActivityReportImpactForm(request.POST or None)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.activityreport = get_object_or_404(ActivityReport, pk=id)
            
            instance.save()
            
               
            return HttpResponse(
                status=204,
                headers={
                    'HX-Trigger': json.dumps({
                        "AImpactListChanged": None,
                        "showMessage": f"{instance.activityreport} added."
                    })
                })
    else:
        form = ActivityReportImpactForm(icnreport=icnreport)
    return render(request, 'partial/activityreport_impact_form.html', {
        'form': form,
    })

   
def activityreport_impact_list(request, id):
    
    activityreport_impacts=ActivityReportImpact.objects.filter(activityreport_id=id)
    context = {'activityreport_impacts':activityreport_impacts }
    return render(request, 'report/partial/activityreport_impact_list.html', context)


def edit_activityreport_impact(request, pk):
    impact = get_object_or_404(ActivityReportImpact, pk=pk)
    activityreport = get_object_or_404(ActivityReport, pk=impact.activityreport_id)
    
   
    if request.method == "POST":
        impact = ActivityReportImpact.objects.get(pk=pk)
        form = ActivityReportImpactForm(request.POST, instance=impact)
        if form.is_valid():
            instance = form.save()
            return HttpResponse(
                status=204,
                headers={
                    'HX-Trigger': json.dumps({
                        "ImpactListChanged": None,
                        "showMessage": f"{instance.pk} updated."
                    })
                })
    else:
        form = ActivityReportImpactForm(instance=impact)
    return render(request, 'report/partial/activityimpact_form_edit.html', {
        'form': form,
        'impact': impact,
    })

def remove_activityreport_impact(request, pk):
    activityreport_impact = get_object_or_404(ActivityReportImpact, pk=pk)
    activityreport_impact.delete()
    return HttpResponse(
        status=204,
        headers={
            'HX-Trigger': json.dumps({
                "AImpactListChanged": None,
                "showMessage": f"{activityreport_impact.title} deleted."
            })
        })


def search_results_view2(request):
    query = request.GET.get('search', '')
    

    all_activities= ActivityReport.objects.all()
    if query:
        qs1 = ActivityReport.objects.filter(title__icontains=query)
        qs2 = ActivityReport.objects.distinct().filter(icnreport__title__icontains=query)
        
        qs3 = ActivityReport.objects.distinct().filter(icnreport__program__title__icontains=query)
        activitiesreport = qs1.union(qs2, qs3).order_by('id')
       
    else:
        activitiesreport = all_activities

    context = {'activitiesreport': activitiesreport, 'count': activitiesreport.count()}
    return render(request, 'partial/activityreport_list.html', context)

def activityreport_submit_approval(request, pk):
    activityreport = get_object_or_404(ActivityReport, pk=pk)
    context ={}
 
    # add the dictionary during initialization
    activityreport = ActivityReport.objects.get(pk=pk)
    if ActivityReportSubmit.objects.filter(activityreport_id=activityreport.id).exists():
        activityreportsubmit = ActivityReportSubmit.objects.filter(activityreport_id=activityreport.id).latest('id')
        context = {'activityreport':activityreport, 'activityreportsubmit':activityreportsubmit}
    else:
        context = {'activityreport':activityreport}
    

    return render(request, 'report/activityreport_submit_approval.html', context)

 
def current_activityreport_submit_approval_list(request, id):
    context ={}
 
    # add the dictionary during initialization
  
    activityreport = ActivityReport.objects.get(pk=id)
    if ActivityReportSubmit.objects.filter(activityreport_id=activityreport.id).exists():
        activityreportsubmit = ActivityReportSubmit.objects.filter(activityreport_id=activityreport.id).latest('id')
        context = {'activityreport':activityreport, 'activityreportsubmit':activityreportsubmit}
    else:
        context = {'activityreport':activityreport}

    return render(request, 'report/partial/activityreport_submit_list.html', context)


def activityreport_submit_form(request, id): 
    activityreport = get_object_or_404(ActivityReport, pk=id)
    form = ActivityReportSubmitForm(user=request.user,activityreport=activityreport)
    
    subject = 'Request for Approval'
    
    message = 'A new Intervention Concept Note has been submitted'
    email_from = None 
    recipient_list = [activityreport.user.email,activityreport.technical_lead.user.email, activityreport.program_lead.user.email, activityreport.finance_lead.user.email]

    if request.method == "POST":
        form = ActivityReportSubmitForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.activityreport = activityreport
            
            instance.user = request.user
            instance.save()
            #document = IcnReportSubmit.objects.filter(icnreport_id=icnreport.id).latest('id')
            #document_i = Document.objects.filter(icnreport=instance.icnreport, user=icnreport.user).count()+1
            
            activityreportsubmit = get_object_or_404(ActivityReportSubmit, pk=instance.pk)
            #Document.objects.create(user = icnreport.user, document = instance.document,  icnreport=instance.icnreport, description = document_i)
            if activityreportsubmit.submission_status == 2:
                ActivityReport.objects.filter(pk=id).update(status=True)
                ActivityReport.objects.filter(pk=id).update(approval_status="Pending")
                ActivityReportSubmitApproval_T.objects.create(user = activityreport.technical_lead,submit_id = instance, document = instance.document, approval_status=1)
                ActivityReportSubmitApproval_P.objects.create(user = activityreport.program_lead,submit_id = instance,document = instance.document, approval_status=1)
                ActivityReportSubmitApproval_F.objects.create(user = activityreport.finance_lead,submit_id = instance,document = instance.document, approval_status=1)

                send_mail(subject, message, email_from, recipient_list)
                return HttpResponse(
                status=204,
                headers={
                    'HX-Trigger': json.dumps({
                        "SubmitApprovalListChanged": None,
                        "showMessage": f"{instance.id} added."
                    })
                })
            
            elif activityreportsubmit.submission_status == 1:
                ActivityReport.objects.filter(pk=id).update(status=False)
                ActivityReport.objects.filter(pk=id).update(approval_status="Pending Submission")
                subject = 'Request withdrawn temporarly'
                message = "The Intervention Concept Note approval request has been withdrawn for further update/changes & will notify you when it's re-submitted for approval process"
                send_mail(subject, message, email_from, recipient_list)
                return HttpResponse(
                status=204,
                headers={
                    'HX-Trigger': json.dumps({
                        "SubmitApprovalListChanged": None,
                        "showMessage": f"{instance.id} added."
                    })
                })

      
    context = {'form':form, 'activityreport':activityreport}
    return render(request, 'report/activityreport_submit_form.html', context)


 
def activityreport_submit_document(request, id):
    context ={}
    activityreport = get_object_or_404(ActivityReport, pk=id)
    dform = ActivityReportDocumentForm()
    major = ActivityReportDocument.objects.filter(activityreport=activityreport.id, user=activityreport.user).count() 
    minor = ActivityReportDocument.objects.filter(activityreport=activityreport.id).exclude(user=activityreport.user)
    minor = minor.count()
    context = {'dform':dform}
    if request.method == 'POST':
        dform = ActivityReportDocumentForm(request.POST, request.FILES)
        if dform.is_valid():
            instance = dform.save(commit=False)
            instance.activityreport = activityreport
            instance.user = request.user
            if instance.user == activityreport.user:
                 major = major + 1
                 minor = minor
            else:
                 major = major 
                 minor = minor + 1
              
            instance.ver = "%s%s%s" %(major,'.',minor)

            instance.save()
            
            
            return HttpResponse(
                status=204,
                headers={
                    'HX-Trigger': json.dumps({
                        "DocListChanged": None,
                        "showMessage": f"{instance.id} added."
                    })
                })
            
    else:
       dform = ActivityReportDocumentForm()
       context = {'dform':dform}
       return render(request, 'report/partial/activityreport_document_form.html', context)
           
            
def activityreport_submit_form_partial(request, id): 
    activityreport = get_object_or_404(ActivityReport, pk=id)
    form = ActivityReportSubmitForm(user=request.user,activityreport=activityreport)
    
    context = {'form':form, 'activityreport':activityreport}
    return render(request, 'report/partial/activityreport_partial_doc_form.html', context)

def activityreport_document_list(request, id):
    documents = ActivityReportDocument.objects.filter(activityreport_id=id)
    context = {'documents':documents}
           
          
    
    return render(request,'report/partial/activityreport_document_list.html', context)

def activityreport_submit_approval_list(request, id):
    activityreport_submit_list = ActivityReportSubmit.objects.filter(activityreport_id = id, submission_status=2)
    
    context = {'activityreport_submit_list': activityreport_submit_list }
    return render(request, 'report/partial/activityreport_submit_approval_list.html', context )

 
def activityreport_approvalt(request, id):
     
    activityreportsubmitApproval_t = get_object_or_404(ActivityReportSubmitApproval_T, submit_id_id=id)
    activityreportsubmit = get_object_or_404(ActivityReportSubmit, pk=id)
    
    activityreport =  get_object_or_404(ActivityReport, id=activityreportsubmit.activityreport_id)

    subject = 'Approval Status changed'
    message = 'Reviewed & status has been updated to this Concept Note has been submitted'
    email_from = None 
    recipient_list = [activityreport.technical_lead.user.email, activityreport.program_lead.user.email, activityreport.finance_lead.user.email]
       
    if request.method == "GET":
        activityreportsubmitApproval_t = get_object_or_404(ActivityReportSubmitApproval_T, submit_id_id=id)
        form = ActivityReportApprovalTForm(instance=activityreportsubmitApproval_t)
        context = {'activityreportsubmitapproval_t':activityreportsubmitApproval_t, 'form': form, 'activityreport':activityreport, }
        return render(request, 'report/activityreport_approval_tform.html', context)
    
    elif request.method == "PUT":
        activityreportsubmitApproval_t = get_object_or_404(ActivityReportSubmitApproval_T, submit_id_id=id)
        data = QueryDict(request.body).dict()
        form = ActivityReportApprovalTForm(data, instance=activityreportsubmitApproval_t)
        if form.is_valid():
            instance =form.save()
           
            activityreportsubmit = get_object_or_404(ActivityReportSubmit, pk=id)
            activityreport =  get_object_or_404(ActivityReport, id=activityreportsubmit.activityreport_id)
            update_activityreport_approval_status(activityreportsubmit.id)
            context = {'activityreport':activityreport, 'activityreportsubmit':activityreportsubmit }
            send_mail(subject, message, email_from, recipient_list)
            return HttpResponse(
                status=204,
                headers={
                    'HX-Trigger': json.dumps({
                        "SubmitApprovalListChanged": None,
                        "showMessage": f"{instance.id} added."
                    })
                })
        
        return render(request, 'report/activityreport_approval_tform.html', {'form':form})

 
def activityreport_approvalp(request, id):
     
    activityreportsubmitApproval_p = get_object_or_404(ActivityReportSubmitApproval_P, submit_id_id=id)
    activityreportsubmit = get_object_or_404(ActivityReportSubmit, pk=id)
    
    activityreport =  get_object_or_404(ActivityReport, id=activityreportsubmit.activityreport_id)

    subject = 'Approval Status changed'
    message = 'Reviewed & status has been updated to this Concept Note has been submitted'
    email_from = None 
    recipient_list = [activityreport.technical_lead.user.email, activityreport.program_lead.user.email, activityreport.finance_lead.user.email]
       
    if request.method == "GET":
        activityreportsubmitApproval_p = get_object_or_404(ActivityReportSubmitApproval_P, submit_id_id=id)
        form = ActivityReportApprovalPForm(instance=activityreportsubmitApproval_p)
        context = {'activityreportsubmitapproval_p':activityreportsubmitApproval_p, 'form': form, 'activityreport':activityreport, }
        return render(request, 'report/activityreport_approval_pform.html', context)
    
    elif request.method == "PUT":
        activityreportsubmitApproval_p = get_object_or_404(ActivityReportSubmitApproval_P, submit_id_id=id)
        data = QueryDict(request.body).dict()
        form = ActivityReportApprovalPForm(data, instance=activityreportsubmitApproval_p)
        if form.is_valid():
            instance =form.save()
            
            activityreportsubmit = get_object_or_404(ActivityReportSubmit, pk=id)
            activityreport =  get_object_or_404(ActivityReport, id=activityreportsubmit.activityreport_id)
            update_activityreport_approval_status(activityreportsubmit.id)
            context = {'activityreport':activityreport, 'activityreportsubmit':activityreportsubmit }
            send_mail(subject, message, email_from, recipient_list)
            return HttpResponse(
                status=204,
                headers={
                    'HX-Trigger': json.dumps({
                        "SubmitApprovalListChanged": None,
                        "showMessage": f"{instance.id} added."
                    })
                })
        
        return render(request, 'report/activityreport_approval_pform.html', {'form':form})

 
def activityreport_approvalf(request, id):
     
    activityreportsubmitApproval_f = get_object_or_404(ActivityReportSubmitApproval_F, submit_id_id=id)
    activityreportsubmit = get_object_or_404(ActivityReportSubmit, pk=id)
    
    activityreport =  get_object_or_404(ActivityReport, id=activityreportsubmit.activityreport_id)

    subject = 'Approval Status changed'
    message = 'Reviewed & status has been updated to this Concept Note'
    email_from = None 
    recipient_list = [activityreport.technical_lead.user.email, activityreport.program_lead.user.email, activityreport.finance_lead.user.email]
       
    if request.method == "GET":
        activityreportsubmitApproval_f = get_object_or_404(ActivityReportSubmitApproval_F, submit_id_id=id)
        form = ActivityReportApprovalFForm(instance=activityreportsubmitApproval_f)
        context = {'activityreportsubmitapproval_f':activityreportsubmitApproval_f, 'form': form, 'activityreport':activityreport, }
        return render(request, 'report/activityreport_approval_fform.html', context)
    
    elif request.method == "PUT":
        activityreportsubmitApproval_f = get_object_or_404(ActivityReportSubmitApproval_F, submit_id_id=id)
        data = QueryDict(request.body).dict()
        form = ActivityReportApprovalFForm(data, instance=activityreportsubmitApproval_f)
        if form.is_valid():
            instance =form.save()
            
            activityreportsubmit = get_object_or_404(ActivityReportSubmit, pk=id)
            activityreport =  get_object_or_404(ActivityReport, id=activityreportsubmit.activityreport_id)
            update_activityreport_approval_status(activityreportsubmit.id)
            context = {'activityreport':activityreport, 'activityreportsubmit':activityreportsubmit }
            send_mail(subject, message, email_from, recipient_list)
            return HttpResponse(
                status=204,
                headers={
                    'HX-Trigger': json.dumps({
                        "SubmitApprovalListChanged": None,
                        "showMessage": f"{instance.id} added."
                    })
                })
        
        return render(request, 'report/activityreport_approval_fform.html', {'form':form})

def update_activityreport_approval_status(id):
    activityreportsubmit = get_object_or_404(ActivityReportSubmit, pk=id)
    activityreportsubmitapproval_t = get_object_or_404(ActivityReportSubmitApproval_T, submit_id_id=id)
    activityreportsubmitapproval_p = get_object_or_404(ActivityReportSubmitApproval_P, submit_id_id=id)
    activityreportsubmitapproval_f = get_object_or_404(ActivityReportSubmitApproval_F, submit_id_id=id)
    
    approval_t = activityreportsubmitapproval_t.approval_status
    approval_p = activityreportsubmitapproval_p.approval_status
    approval_f = activityreportsubmitapproval_f.approval_status
    
    if approval_t == 4 or approval_p== 4 or approval_f== 4:
        ActivityReport.objects.filter(pk=activityreportsubmit.activityreport_id).update(approval_status="Rejected")
    elif approval_t < 3 and approval_p < 3 and approval_p < 3:
        ActivityReport.objects.filter(pk=activityreportsubmit.activityreport_id).update(approval_status="Pending Approval")
    elif approval_t == 3 and approval_p ==3 and approval_f==3:
        ActivityReport.objects.filter(pk=activityreportsubmit.activityreport_id).update(approval_status="100% Approved")
    elif (approval_t == 3 and approval_p ==3 and approval_f !=3) or (approval_t == 3 and approval_p !=3 and approval_f ==3) or (approval_t != 3 and approval_p ==3 and approval_f ==3):
        ActivityReport.objects.filter(pk=activityreportsubmit.activityreport_id).update(approval_status="67% Approved")
    elif (approval_t == 3 and approval_p !=3 and approval_f !=3) or (approval_t != 3 and approval_p ==3 and approval_f !=3) or (approval_t != 3 and approval_p !=3 and approval_f ==3):
        ActivityReport.objects.filter(pk=activityreportsubmit.activityreport_id).update(approval_status="33% Approved") 

def downloada(request, id):
    document = get_object_or_404(ActivityReportDocument, id=id)
    response = HttpResponse(document.document, content_type='application/docx')
    response['Content-Disposition'] = f'attachment; filename="{document.document}"'
    return response

def latest_submit_approval_list(request, id):
    if IcnReportSubmit.objects.filter(icn_id=id).exists():
         list = IcnReportSubmit.objects.filter(icn_id = id, submission_status=2).latest('id')
         context = {'list':list}
    else: 
        context = {}
    
    return render(request, 'partial/recent_submit_approval_list.html', context)

def latest_submit_approval_list_activity(request, id):
    if ActivityReportSubmit.objects.filter(activity_id = id).exists():
        list = ActivityReportSubmit.objects.filter(activity_id = id, submission_status=2).latest('id')
        context = {'list':list}
    else: 
        context = {}
    return render(request, 'partial/recent_submit_approval_list_activity.html', context)
