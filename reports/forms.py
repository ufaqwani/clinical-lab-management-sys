from django import forms
from .models import Report, ReportTemplate  
from tests.models import Test
from patients.models import Patient


class ReportGenerationForm(forms.Form):
    patient = forms.ModelChoiceField(
        queryset=Patient.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="Select Patient"
    )
    
    tests = forms.ModelMultipleChoiceField(
        queryset=Test.objects.none(),  # Will be populated dynamically
        widget=forms.CheckboxSelectMultiple,
        required=True
    )
    
    template = forms.ModelChoiceField(
        queryset=ReportTemplate.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    
    report_format = forms.ChoiceField(
        choices=Report.FORMAT_CHOICES,
        initial='PDF',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Show only completed tests with results
        self.fields['tests'].queryset = Test.objects.filter(
            status='COMPLETED'
        ).select_related('patient', 'test_type')
        
        # Set default template if available
        default_template = ReportTemplate.objects.filter(is_default=True).first()
        if default_template:
            self.fields['template'].initial = default_template


class ReportSearchForm(forms.Form):
    search_query = forms.CharField(
        max_length=100, 
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Search reports...'
        })
    )
    
    status = forms.ChoiceField(
        choices=[('', 'All Status')] + Report.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
