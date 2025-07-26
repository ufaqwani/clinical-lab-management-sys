from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from .models import Patient
from .forms import PatientForm, PatientSearchForm

def patient_list(request):
    """List all patients with search and filtering"""
    form = PatientSearchForm(request.GET)
    patients = Patient.objects.filter(is_active=True)
    
    if form.is_valid():
        search_query = form.cleaned_data.get('search_query')
        gender = form.cleaned_data.get('gender')
        blood_group = form.cleaned_data.get('blood_group')
        
        if search_query:
            patients = patients.filter(
                Q(patient_id__icontains=search_query) |
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(phone_number__icontains=search_query)
            )
        
        if gender:
            patients = patients.filter(gender=gender)
            
        if blood_group:
            patients = patients.filter(blood_group__icontains=blood_group)
    
    # Pagination
    paginator = Paginator(patients, 10)  # Show 10 patients per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'patients': page_obj,
        'form': form,
        'total_patients': patients.count()
    }
    return render(request, 'patients/patient_list.html', context)

def patient_detail(request, patient_id):
    """View patient details"""
    patient = get_object_or_404(Patient, patient_id=patient_id, is_active=True)
    
    # Get recent tests for this patient
    recent_tests = patient.test_set.all()[:5]  # Last 5 tests
    
    context = {
        'patient': patient,
        'recent_tests': recent_tests
    }
    return render(request, 'patients/patient_detail.html', context)

@login_required
def patient_create(request):
    """Create a new patient"""
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            patient = form.save()
            messages.success(request, f'Patient {patient.full_name} created successfully!')
            return redirect('patient_detail', patient_id=patient.patient_id)
    else:
        form = PatientForm()
    
    return render(request, 'patients/patient_form.html', {
        'form': form,
        'title': 'Add New Patient'
    })

@login_required
def patient_update(request, patient_id):
    """Update patient information"""
    patient = get_object_or_404(Patient, patient_id=patient_id)
    
    if request.method == 'POST':
        form = PatientForm(request.POST, instance=patient)
        if form.is_valid():
            patient = form.save()
            messages.success(request, f'Patient {patient.full_name} updated successfully!')
            return redirect('patient_detail', patient_id=patient.patient_id)
    else:
        form = PatientForm(instance=patient)
    
    return render(request, 'patients/patient_form.html', {
        'form': form,
        'patient': patient,
        'title': f'Edit Patient - {patient.full_name}'
    })

@login_required
def patient_delete(request, patient_id):
    """Soft delete a patient (set is_active=False)"""
    patient = get_object_or_404(Patient, patient_id=patient_id)
    
    if request.method == 'POST':
        patient.is_active = False
        patient.save()
        messages.success(request, f'Patient {patient.full_name} has been deactivated.')
        return redirect('patient_list')
    
    return render(request, 'patients/patient_confirm_delete.html', {'patient': patient})
