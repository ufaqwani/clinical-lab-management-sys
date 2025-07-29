from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator  
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import JsonResponse

from .models import Test, TestResult, TestType, TestCategory
from .forms import TestOrderForm, TestResultForm, TestSearchForm, TestTypeForm
from patients.models import Patient
from accounts.models import LabMembership


def test_list(request):
    """List all tests with search and filtering"""
    form = TestSearchForm(request.GET)
    tests = Test.objects.select_related('patient', 'test_type', 'ordered_by').all()
    
    if form.is_valid():
        search_query = form.cleaned_data.get('search_query')
        status = form.cleaned_data.get('status')
        priority = form.cleaned_data.get('priority')
        test_type = form.cleaned_data.get('test_type')
        
        if search_query:
            tests = tests.filter(
                Q(test_id__icontains=search_query) |
                Q(patient__first_name__icontains=search_query) |
                Q(patient__last_name__icontains=search_query) |
                Q(patient__patient_id__icontains=search_query)
            )
        
        if status:
            tests = tests.filter(status=status)
            
        if priority:
            tests = tests.filter(priority=priority)
            
        if test_type:
            tests = tests.filter(test_type=test_type)
    
    # Pagination
    paginator = Paginator(tests, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Summary stats
    stats = {
        'total': tests.count(),
        'pending': tests.filter(status='ORDERED').count(),
        'processing': tests.filter(status__in=['COLLECTED', 'PROCESSING']).count(),
        'completed': tests.filter(status='COMPLETED').count(),
    }
    
    context = {
        'tests': page_obj,
        'form': form,
        'stats': stats
    }
    return render(request, 'tests/test_list.html', context)

@login_required
def test_order(request):
    """Order a new test"""
    if request.method == 'POST':
        form = TestOrderForm(request.POST, user=request.user)
        if form.is_valid():
            test = form.save()
            messages.success(request, f'Test {test.test_id} ordered successfully for {test.patient.full_name}!')
            return redirect('test_detail', test_id=test.test_id)
    else:
        form = TestOrderForm(user=request.user)
        
        # Pre-select patient if provided in URL
        patient_id = request.GET.get('patient_id')
        if patient_id:
            try:
                patient = Patient.objects.get(patient_id=patient_id, is_active=True)
                form.fields['patient'].initial = patient
            except Patient.DoesNotExist:
                pass
    
    return render(request, 'tests/test_order.html', {
        'form': form,
        'test_categories': TestCategory.objects.prefetch_related('testtype_set').all()
    })

def test_detail(request, test_id):
    """View test details and manage test workflow"""
    test = get_object_or_404(Test, test_id=test_id)
    
    # Handle sample collection
    if request.method == 'POST' and 'collect_sample' in request.POST:
        if request.user.is_authenticated:
            test.sample_collected_date = timezone.now()
            test.sample_collected_by = request.user
            test.status = 'COLLECTED'
            test.save()
            messages.success(request, 'Sample collection recorded!')
            return redirect('test_detail', test_id=test.test_id)
    
    # Handle processing start
    if request.method == 'POST' and 'start_processing' in request.POST:
        if request.user.is_authenticated:
            test.status = 'PROCESSING'
            test.processed_by = request.user
            test.save()
            messages.success(request, 'Test processing started!')
            return redirect('test_detail', test_id=test.test_id)
    
    context = {
        'test': test,
        'can_collect': test.status == 'ORDERED',
        'can_process': test.status == 'COLLECTED',
        'can_enter_results': test.status == 'PROCESSING',
    }
    return render(request, 'tests/test_detail.html', context)

@login_required
def test_enter_results(request, test_id):
    """Enter test results"""
    test = get_object_or_404(Test, test_id=test_id)
    
    if test.status not in ['PROCESSING', 'COMPLETED']:
        messages.error(request, 'Test must be in processing status to enter results.')
        return redirect('test_detail', test_id=test.test_id)
    
    try:
        result = test.result
    except TestResult.DoesNotExist:
        result = None
    
    if request.method == 'POST':
        form = TestResultForm(request.POST, instance=result)
        if form.is_valid():
            result = form.save(commit=False)
            result.test = test
            result.save()
            
            # Update test status
            test.status = 'COMPLETED'
            test.processed_date = timezone.now()
            test.save()
            
            messages.success(request, 'Test results entered successfully!')
            return redirect('test_detail', test_id=test.test_id)
    else:
        form = TestResultForm(instance=result)
    
    context = {
        'test': test,
        'form': form,
        'result': result
    }
    return render(request, 'tests/test_enter_results.html', context)

def dashboard(request):
    """Laboratory dashboard with key metrics"""
    # Get recent tests
    recent_tests = Test.objects.select_related('patient', 'test_type').order_by('-ordered_date')[:10]
    
    # Get pending tests by priority
    pending_tests = Test.objects.filter(status='ORDERED').order_by('priority', 'ordered_date')[:5]
    
    # Calculate metrics
    today = timezone.now().date()
    metrics = {
        'total_tests_today': Test.objects.filter(ordered_date__date=today).count(),
        'completed_today': Test.objects.filter(processed_date__date=today).count(),
        'pending_total': Test.objects.filter(status__in=['ORDERED', 'COLLECTED', 'PROCESSING']).count(),
        'overdue_tests': Test.objects.filter(
            status__in=['ORDERED', 'COLLECTED', 'PROCESSING'],
            ordered_date__lt=timezone.now() - timezone.timedelta(days=1)
        ).count(),
    }
    
    context = {
        'recent_tests': recent_tests,
        'pending_tests': pending_tests,
        'metrics': metrics
    }
    return render(request, 'tests/dashboard.html', context)


# enable test type for labs

@login_required
def create_test_type(request):
    """Allow lab users to create new test types within their lab"""
    lab_membership = request.user.lab_memberships.filter(is_active=True).first()
    if not lab_membership:
        messages.error(request, "You must be associated with an active lab to add test types.")
        return redirect('test_order')

    if request.method == 'POST':
        form = TestTypeForm(request.POST)
        if form.is_valid():
            test_type = form.save(commit=False)
            test_type.lab = lab_membership.lab
            test_type.save()
            messages.success(request, f"Test Type '{test_type.name}' created successfully.")
            return redirect('test_order')
    else:
        form = TestTypeForm()

    return render(request, 'tests/create_test_type.html', {'form': form})


