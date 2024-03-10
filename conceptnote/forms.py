from django import forms
from django.core.exceptions import ValidationError
from .models import Icn, Activity,Impact,ActivityImpact, IcnImplementationArea,  ActivityImplementationArea,IcnSubmit, Document, IcnSubmitApproval_F, IcnSubmitApproval_T, IcnSubmitApproval_P, ActivityDocument, ActivitySubmit,ActivitySubmitApproval_F,ActivitySubmitApproval_P,ActivitySubmitApproval_T
from django import forms

from program.models import  Program, ImplementationArea, Indicator, UserRoles
from portfolio.models import Portfolio
from datetime import datetime
from django.forms.models import modelformset_factory
from django_select2 import forms as s2forms
from app_admin.models import Country , Region , Zone , Woreda 
from django.contrib.auth.models import User
CHOICE1 =(
    ("1", "Low"),
    ("2", "Medium"),
    ("3", "High"),
    
)
CHOICE2 =(
    ("0", "No"),
    ("1", "Yes"),
  
    
)
class IcnForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
      
        if user:
            self.fields['program'].queryset = Program.objects.filter(users_role=user)
            self.fields['program'].initial=Program.objects.filter(users_role=user).first()
            program = Program.objects.filter(users_role=user)
            self.fields['program_lead'].queryset =  UserRoles.objects.filter(program__in=program, is_pcn_program_approver=True).exclude(user=user)
            self.fields['program_lead'].initial=UserRoles.objects.filter(program__in=program, is_pcn_program_approver=True).exclude(user=user).first()
            self.fields['technical_lead'].queryset = UserRoles.objects.filter(program__in=program, is_pcn_technical_approver=True).exclude(user=user)
            self.fields['technical_lead'].initial=UserRoles.objects.filter(program__in=program, is_pcn_technical_approver=True).exclude(user=user).first()
            self.fields['finance_lead'].queryset = UserRoles.objects.filter(program__in=program, is_pcn_finance_approver=True).exclude(user=user)
            self.fields['finance_lead'].initial=UserRoles.objects.filter(program__in=program, is_pcn_finance_approver=True).exclude(user=user).first()
           
        myfield = ['title',
            'program',
            'description',
            'proposed_start_date', 
            'proposed_end_date',
            'ilead_agency',
            'final_report_due_date',
            'program_lead',
            'technical_lead',
            'finance_lead',
           
            'mc_budget_usd',
           
            'cost_sharing_budget_usd',
            
            'eniromental_impact',
            
            
           
          


           
            

            ]
        for field in myfield:
            self.fields[field].required = True 

        
    

       
       
        self.fields['proposed_start_date'].widget = forms.widgets.DateInput(
          
            attrs={
               'type': 'date', 'placeholder': 'yyyy-mm-dd',
                'class': 'form-control',
                'required': 'true'
                
                
                }
            )
  
        self.fields['proposed_end_date'].widget = forms.widgets.DateInput(
            attrs={
                'type': 'date', 'placeholder': 'yyyy-mm-dd (DOB)',
                'class': 'form-control'
                }
            )
        self.fields['final_report_due_date'].widget = forms.widgets.DateInput(
            attrs={
                'type': 'date', 'placeholder': 'yyyy-mm-dd (DOB)',
                'class': 'form-control'
                }
            )
        self.fields['description'].widget = forms.widgets.Textarea(attrs={'type':'textarea', 'class': 'form-contro-sm', 'rows':'3', 'required':'required'  }    )
        self.fields['eniromental_impact'].widget = forms.widgets.Select(choices = CHOICE1,attrs={'type': 'choice', 'class': 'form-control form-control-sm', 'rows':'1', 'placeholder':''   }    )
        self.fields['ilead_co_agency'].widget =  s2forms.Select2MultipleWidget(attrs={ 'type': 'checkbox', 'class':'form-control form-control-sm select',  'data-width': '100%'})
        self.fields['ilead_co_agency'].queryset = Portfolio.objects.all()
        self.fields['iworeda'].widget =  s2forms.Select2MultipleWidget(attrs={ 'type': 'checkbox', 'class':'form-control form-control-sm select',  'data-width': '100%'})
        self.fields['iworeda'].queryset = ImplementationArea.objects.all()
    class Meta:
        model = Icn
        fields=['title',
            'program',
            'description',
            'proposed_start_date', 
            'proposed_end_date',
            
            'final_report_due_date',
            'program_lead',
            'technical_lead',
            'finance_lead',
            'iworeda',
            'mc_budget_usd',
           
            'cost_sharing_budget_usd',
            
            'eniromental_impact',
            'environmental_assessment_att',
            'ilead_agency',
            'ilead_co_agency',
           
          


           
            

            ]

        exclude=  ['status', 'approval_status',  'user',]
        
    def clean(self):
         cleaned_data = super().clean()
         
         program_lead = self.cleaned_data.get('program_lead')
         finance_lead = self.cleaned_data.get('finance_lead')
         technical_lead = self.cleaned_data.get('technical_lead')
         eniromental_impact = self.cleaned_data.get('eniromental_impact')
         environmental_assessment_att = self.cleaned_data.get('environmental_assessment_att')
         proposed_start_date = self.cleaned_data.get('proposed_start_date')
         proposed_end_date = self.cleaned_data.get('proposed_end_date')
         final_report_due_date = self.cleaned_data.get('final_report_due_date')

         if (technical_lead==program_lead or technical_lead==finance_lead):
              self._errors['technical_lead'] = self.error_class(['Lead should take up only one role'])
         elif (program_lead==technical_lead or program_lead==finance_lead):
              self._errors['program_lead'] = self.error_class(['Lead should take up only one role'])
         
         elif (finance_lead==technical_lead or finance_lead==program_lead):
              self._errors['finance_lead'] = self.error_class(['Lead should take up only one role'])
         elif (eniromental_impact == '3' and environmental_assessment_att==None):
              self._errors['eniromental_impact'] = self.error_class(['Attachment required for High Impact'])
         elif ( proposed_end_date != None and proposed_start_date != None and proposed_end_date < proposed_start_date):
               self._errors['proposed_end_date'] = self.error_class(['End date should always be after start date'])
         elif (final_report_due_date != None and proposed_end_date != None and final_report_due_date < proposed_end_date):
             self._errors['final_report_due_date'] = self.error_class(['Reporting Date should always be after end date'])
         return cleaned_data


IcnAreaFormset = modelformset_factory(
    IcnImplementationArea,
    fields=('region', 'zone','woreda'),
    extra=4,
   
) 





class IcnAreaFormEdit(forms.ModelForm):
    
    class Meta:
        model = IcnImplementationArea
        fields=['region',
            'zone',
            'woreda',
            ]
        exclude=  ['icn']

class IcnAreaFormE(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['region'].queryset = Region.objects.all()

        self.fields['zone'].queryset = Zone.objects.none()
        self.fields['woreda'].queryset = Woreda.objects.none()
        if 'region' in self.data:
            try:
                region = int(self.data.get('region'))
                self.fields['zone'].queryset = Zone.objects.filter(region_id=region).order_by('name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        elif self.instance.pk:
            self.fields['zone'].queryset = self.instance.region.zone_set.order_by('name')

        self.fields['woreda'].queryset = Woreda.objects.none()
        if 'zone' in self.data:
            try:
                zone = int(self.data.get('zone'))
                self.fields['woreda'].queryset = Woreda.objects.filter(zone_id=zone).order_by('name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        elif self.instance.pk:
            self.fields['woreda'].queryset = self.instance.zone.woreda_set.order_by('name')

        myfield = ['region',
            'zone','woreda'          

            ]
        for field in myfield:
            self.fields[field].required = True 
    
    class Meta:
            model = IcnImplementationArea
            fields=['region',
            'zone',
            'woreda',
            ]
            exclude=  ['icn']

class IcnSubmitForm(forms.ModelForm):
     #document = forms.ChoiceField(
         #choices=[(document.id, document.document) for document in Document.objects.all()]
#)

     def __init__(self, *args, **kwargs):
         user = kwargs.pop('user', None)
         icn = kwargs.pop('icn', None)
         super(IcnSubmitForm, self).__init__(*args, **kwargs)

         self.fields['document'].choices = [
             (document.pk, document) for document in Document.objects.filter(user=user, icn=icn)
         ]
             
      # invalid input from the client; ignore and fallback to empty City queryset
        
  
    

         self.fields['submission_note'].widget = forms.widgets.Textarea(attrs={'type':'textarea', 'class': 'form-control', 'rows':'3', 'required':'True'   }    )
         self.fields['submission_note'].required = True 
        
     class Meta:
            model = IcnSubmit
            fields=['submission_status',
            'submission_note',
            'document',
           
           
            ]
            exclude=  ['icn',]
            
          


class IcnDocumentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
              
        self.fields['description'].widget = forms.widgets.Textarea(attrs={'type':'textarea', 'class': 'form-control', 'rows':'3', 'required':'required'  }    )
        self.fields['description'].required = True 
        self.fields['document'].required = True 
    
    
        
    class Meta:
        model = Document
        fields = ('description', 'document',)

        exclude=  ['icn','user', 'ver']


class IcnApprovalTForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['approval_note'].widget = forms.widgets.Textarea(attrs={'type':'textarea', 'class': 'form-control', 'rows':'3'  }    )
        
        
    class Meta:
            model = IcnSubmitApproval_T
            fields = ('approval_note','approval_status','document')

            exclude=  ['icn','user',]
            


class IcnApprovalFForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['approval_note'].widget = forms.widgets.Textarea(attrs={'type':'textarea', 'class': 'form-control', 'rows':'3', 'required':'True'   }    )
        
        
    class Meta:
            model = IcnSubmitApproval_F
            fields =  ('approval_note','approval_status','document')

            exclude=  ['icn','user']

class IcnApprovalPForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['approval_note'].widget = forms.widgets.Textarea(attrs={'type':'textarea', 'class': 'form-control', 'rows':'3', 'required':'True'   }    )
        
    
               
    class Meta:
            model = IcnSubmitApproval_P
            fields =  ('approval_note','approval_status','document')

            exclude=  ['icn','user']
    
    



class ImpactForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        program = kwargs.pop('program', None)
        super().__init__(*args, **kwargs)
    

        self.fields['indicators'].widget =  s2forms.Select2MultipleWidget(attrs={ 'type': 'checkbox', 'class':'form-control form-control-sm select', 'data-width': '100%'})
        if program:
             self.fields['indicators'].queryset = Indicator.objects.filter(program_id=program.id)
        else:
            self.fields['indicators'].queryset = Indicator.objects.all()
        self.fields['indicators'].required = True 
        self.fields['title'].required = True 
        self.fields['description'].required = True 
        self.fields['impact_pilot'].required = True 
        self.fields['impact_scaleup'].required = True 
    class Meta:
        model = Impact
        fields = ['title','description', 'impact_pilot' ,'impact_scaleup',
                    'indicators']
        exclude=  ['icn']

class ActivityForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
      
        if user:
            
            program = Program.objects.filter(users_role=user)
            self.fields['program_lead'].queryset =  UserRoles.objects.filter(program__in=program, is_pcn_program_approver=True).exclude(user=user)
            self.fields['program_lead'].initial=UserRoles.objects.filter(program__in=program, is_pcn_program_approver=True).exclude(user=user).first()
            self.fields['technical_lead'].queryset = UserRoles.objects.filter(program__in=program, is_pcn_technical_approver=True).exclude(user=user)
            self.fields['technical_lead'].initial=UserRoles.objects.filter(program__in=program, is_pcn_technical_approver=True).exclude(user=user).first()
            self.fields['finance_lead'].queryset = UserRoles.objects.filter(program__in=program, is_pcn_finance_approver=True).exclude(user=user)
            self.fields['finance_lead'].initial=UserRoles.objects.filter(program__in=program, is_pcn_finance_approver=True).exclude(user=user).first()
       
           
        myfield = ['title',
            'icn',
            'description',
            'proposed_start_date', 
            'proposed_end_date',
            'alead_agency',
            'final_report_due_date',
            'program_lead',
            'technical_lead',
            'finance_lead',
           
            'mc_budget_usd',
           
            'cost_sharing_budget_usd',
            
            
            
           
          


           
            

            ]
        for field in myfield:
            self.fields[field].required = True 

        
    

       
       
        self.fields['proposed_start_date'].widget = forms.widgets.DateInput(
          
            attrs={
               'type': 'date', 'placeholder': 'yyyy-mm-dd',
                'class': 'form-control',
                'required': 'true'
                
                
                }
            )
  
        self.fields['proposed_end_date'].widget = forms.widgets.DateInput(
            attrs={
                'type': 'date', 'placeholder': 'yyyy-mm-dd (DOB)',
                'class': 'form-control'
                }
            )
        self.fields['final_report_due_date'].widget = forms.widgets.DateInput(
            attrs={
                'type': 'date', 'placeholder': 'yyyy-mm-dd (DOB)',
                'class': 'form-control'
                }
            )
        self.fields['description'].widget = forms.widgets.Textarea(attrs={'type':'textarea', 'class': 'form-contro-sm', 'rows':'3', 'required':'required'  }    )
       
        self.fields['alead_co_agency'].widget =  s2forms.Select2MultipleWidget(attrs={ 'type': 'checkbox', 'class':'form-control form-control-sm select',  'data-width': '100%'})
        self.fields['alead_co_agency'].queryset = Portfolio.objects.all()
        self.fields['aworeda'].widget =  s2forms.Select2MultipleWidget(attrs={ 'type': 'checkbox', 'class':'form-control form-control-sm select',  'data-width': '100%'})
        self.fields['aworeda'].queryset = ImplementationArea.objects.all()
         
    class Meta:
        model = Activity
        fields=['title',
            'icn',
            'description',
            'proposed_start_date', 
            'proposed_end_date',
            
            'final_report_due_date',
            'program_lead',
            'technical_lead',
            'finance_lead',
            'aworeda',
            'mc_budget_usd',
           
            'cost_sharing_budget_usd',
            
          
            'alead_agency',
            'alead_co_agency',
           
          


           
            

            ]

        exclude=  ['status', 'approval_status',  'user',]
        
    def clean(self):
         cleaned_data = super().clean()
         
         program_lead = self.cleaned_data.get('program_lead')
         finance_lead = self.cleaned_data.get('finance_lead')
         technical_lead = self.cleaned_data.get('technical_lead')
         
         proposed_start_date = self.cleaned_data.get('proposed_start_date')
         proposed_end_date = self.cleaned_data.get('proposed_end_date')
         final_report_due_date = self.cleaned_data.get('final_report_due_date')

         if (technical_lead==program_lead or technical_lead==finance_lead):
              self._errors['technical_lead'] = self.error_class(['Lead should take up only one role'])
         elif (program_lead==technical_lead or program_lead==finance_lead):
              self._errors['program_lead'] = self.error_class(['Lead should take up only one role'])
         
         elif (finance_lead==technical_lead or finance_lead==program_lead):
              self._errors['finance_lead'] = self.error_class(['Lead should take up only one role'])
        
         elif ( proposed_end_date != None and proposed_start_date != None and proposed_end_date < proposed_start_date):
               self._errors['proposed_end_date'] = self.error_class(['End date should always be after start date'])
         elif (final_report_due_date != None and proposed_end_date != None and final_report_due_date < proposed_end_date):
             self._errors['final_report_due_date'] = self.error_class(['Reporting Date should always be after end date'])
         return cleaned_data

class ActivityAreaFormE(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['region'].queryset = Region.objects.all()

        self.fields['zone'].queryset = Zone.objects.none()
        self.fields['woreda'].queryset = Woreda.objects.none()
        if 'region' in self.data:
            try:
                region = int(self.data.get('region'))
                self.fields['zone'].queryset = Zone.objects.filter(region_id=region).order_by('name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        elif self.instance.pk:
            self.fields['zone'].queryset = self.instance.region.zone_set.order_by('name')

        self.fields['woreda'].queryset = Woreda.objects.none()
        if 'zone' in self.data:
            try:
                zone = int(self.data.get('zone'))
                self.fields['woreda'].queryset = Woreda.objects.filter(zone_id=zone).order_by('name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        elif self.instance.pk:
            self.fields['woreda'].queryset = self.instance.zone.woreda_set.order_by('name')

        myfield = ['region',
            'zone','woreda'          

            ]
        for field in myfield:
            self.fields[field].required = True 
    
    class Meta:
            model = ActivityImplementationArea
            fields=['region',
            'zone',
            'woreda',
            ]
            exclude=  ['activity']

class ActivityImpactForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        icn = kwargs.pop('icn', None)
        super().__init__(*args, **kwargs)
    

        self.fields['impact'].widget =  s2forms.Select2MultipleWidget(attrs={ 'type': 'checkbox', 'class':'form-control form-control-sm select', 'data-width': '100%'})
        if icn:
             self.fields['impact'].queryset = Impact.objects.filter(icn_id=icn.id)
        else:
            self.fields['impact'].queryset = Impact.objects.all()
        self.fields['impact'].required = True 
        self.fields['title'].required = True 
        self.fields['description'].required = True 
        self.fields['impact_pilot'].required = True 
        self.fields['impact_scaleup'].required = True 
    class Meta:
        model = ActivityImpact
        fields = ['title','description', 'impact_pilot' ,'impact_scaleup',
                    'impact']
        exclude=  ['activity']

class ActivitySubmitForm(forms.ModelForm):
     #document = forms.ChoiceField(
         #choices=[(document.id, document.document) for document in Document.objects.all()]
#)

     def __init__(self, *args, **kwargs):
         user = kwargs.pop('user', None)
         activity = kwargs.pop('activity', None)
         super(ActivitySubmitForm, self).__init__(*args, **kwargs)

         self.fields['document'].choices = [
             (document.pk, document) for document in ActivityDocument.objects.filter(user=user, activity=activity)
         ]
             
      # invalid input from the client; ignore and fallback to empty City queryset
        
  
    

         self.fields['submission_note'].widget = forms.widgets.Textarea(attrs={'type':'textarea', 'class': 'form-control', 'rows':'3', 'required':'True'   }    )
         self.fields['submission_note'].required = True 
        
     class Meta:
            model = ActivitySubmit
            fields=['submission_status',
            'submission_note',
            'document',
           
           
            ]
            exclude=  ['activity',]
            
          


class ActivityDocumentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
              
        self.fields['description'].widget = forms.widgets.Textarea(attrs={'type':'textarea', 'class': 'form-control', 'rows':'3', 'required':'required'  }    )
        self.fields['description'].required = True 
        self.fields['document'].required = True 
    
    
        
    class Meta:
        model = ActivityDocument
        fields = ('description', 'document',)

        exclude=  ['activity','user', 'ver']

class ActivityApprovalTForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['approval_note'].widget = forms.widgets.Textarea(attrs={'type':'textarea', 'class': 'form-control', 'rows':'3'  }    )
        
        
    class Meta:
            model = ActivitySubmitApproval_T
            fields = ('approval_note','approval_status','document')

            exclude=  ['activity','user',]

class ActivityApprovalPForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['approval_note'].widget = forms.widgets.Textarea(attrs={'type':'textarea', 'class': 'form-control', 'rows':'3'  }    )
        
        
    class Meta:
            model = ActivitySubmitApproval_P
            fields = ('approval_note','approval_status','document')

            exclude=  ['activity','user',]

class ActivityApprovalFForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['approval_note'].widget = forms.widgets.Textarea(attrs={'type':'textarea', 'class': 'form-control', 'rows':'3'  }    )
        
        
    class Meta:
            model = ActivitySubmitApproval_F
            fields = ('approval_note','approval_status','document')

            exclude=  ['activity','user',]