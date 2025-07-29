from django import forms
from django.contrib.auth.models import User
from .models import Test, TestResult, TestType
from patients.models import Patient
import uuid

class TestOrderForm(forms.ModelForm):
    patient = forms.ModelChoiceField(
        queryset=Patient.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="Select Patient"
    )
    test_type = forms.ModelChoiceField(
        queryset=TestType.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="Select Test Type"
    )
    
    class Meta:
        model = Test
        fields = ['patient', 'test_type', 'priority', 'notes']
        widgets = {
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Any special instructions...'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            # Get user's active lab (assuming user.lab_memberships exists)
            lab_membership = self.user.lab_memberships.filter(is_active=True).first()
            if lab_membership:
                self.fields['test_type'].queryset = TestType.objects.filter(
                    lab=lab_membership.lab, is_active=True
                )
            else:
                self.fields['test_type'].queryset = TestType.objects.none()

    def save(self, commit=True):
        test = super().save(commit=False)
        if not test.test_id:
            # Generate unique test ID
            test.test_id = f"TEST{uuid.uuid4().hex[:6].upper()}"
        if self.user:
            test.ordered_by = self.user
        if commit:
            test.save()
        return test

class TestResultForm(forms.ModelForm):
    class Meta:
        model = TestResult
        fields = ['result_value', 'is_abnormal', 'technician_notes']
        widgets = {
            'result_value': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter test result'}),
            'is_abnormal': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'technician_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Technical notes...'}),
        }

class TestSearchForm(forms.Form):
    search_query = forms.CharField(
        max_length=100, 
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Search by test ID, patient name...'
        })
    )
    status = forms.ChoiceField(
        choices=[('', 'All Status')] + Test.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    priority = forms.ChoiceField(
        choices=[('', 'All Priorities')] + Test.PRIORITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    test_type = forms.ModelChoiceField(
        queryset=TestType.objects.filter(is_active=True),
        required=False,
        empty_label="All Test Types",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class SampleCollectionForm(forms.Form):
    sample_collected = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    collection_notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Collection notes...'})
    )


# enable labs to add tests
class TestTypeForm(forms.ModelForm):
    class Meta:
        model = TestType
        fields = ['name', 'code', 'category', 'sample_type', 'cost', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'sample_type': forms.TextInput(attrs={'class': 'form-control'}),
            'cost': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

