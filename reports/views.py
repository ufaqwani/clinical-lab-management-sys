from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from django.core.files.base import ContentFile
from django.utils import timezone
from .models import Report, ReportTemplate
from .forms import ReportGenerationForm, ReportSearchForm
from .pdf_generator import LabReportGenerator
from tests.models import Test
from patients.models import Patient


def report_list(request):
    """List all reports with search and filtering"""
    form = ReportSearchForm(request.GET)
    reports = Report.objects.select_related('patient', 'generated_by', 'signed_by').all()

    if form.is_valid():
        search_query = form.cleaned_data.get('search_query')
        status = form.cleaned_data.get('status')
        date_from = form.cleaned_data.get('date_from')
        date_to = form.cleaned_data.get('date_to')

        if search_query:
            reports = reports.filter(
                Q(report_id__icontains=search_query) |
                Q(patient__first_name__icontains=search_query) |
                Q(patient__last_name__icontains=search_query) |
                Q(patient__patient_id__icontains=search_query)
            )
        if status:
            reports = reports.filter(status=status)
        if date_from:
            reports = reports.filter(generated_date__date__gte=date_from)
        if date_to:
            reports = reports.filter(generated_date__date__lte=date_to)

    paginator = Paginator(reports, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    stats = {
        'total': reports.count(),
        'draft': reports.filter(status='DRAFT').count(),
        'generated': reports.filter(status='GENERATED').count(),
        'signed': reports.filter(status='SIGNED').count(),
    }

    context = {
        'reports': page_obj,
        'form': form,
        'stats': stats
    }
    return render(request, 'reports/report_list.html', context)


@login_required
def generate_report(request):
    """Generate a new report"""
    if request.method == 'POST':
        form = ReportGenerationForm(request.POST)
        if form.is_valid():
            report = Report.objects.create(
                patient=form.cleaned_data['patient'],
                template=form.cleaned_data['template'],
                report_format=form.cleaned_data['report_format'],
                generated_by=request.user,
                notes=form.cleaned_data.get('notes', ''),
                lab=form.cleaned_data['patient'].lab
            )
            tests = form.cleaned_data['tests']
            report.tests.set(tests)

            if form.cleaned_data['report_format'] == 'PDF':
                try:
                    pdf_generator = LabReportGenerator(report)
                    pdf_content = pdf_generator.generate_pdf()
                    filename = f"report_{report.report_id}.pdf"
                    report.report_file.save(
                        filename,
                        ContentFile(pdf_content),
                        save=True
                    )
                    report.status = 'GENERATED'
                    report.save()
                    messages.success(request, f'Report {report.report_id} generated successfully!')
                    return redirect('report_detail', report_id=report.report_id)
                except Exception as e:
                    messages.error(request, f'Error generating PDF: {str(e)}')
                    report.delete()
            else:
                report.status = 'GENERATED'
                report.save()
                messages.success(request, f'Report {report.report_id} created successfully!')
                return redirect('report_detail', report_id=report.report_id)
    else:
        form = ReportGenerationForm()
        test_id = request.GET.get('test_id')
        patient_id = request.GET.get('patient_id')

        if test_id:
            try:
                test = Test.objects.get(test_id=test_id)
                form.fields['patient'].initial = test.patient
                form.fields['tests'].initial = [test]
            except Test.DoesNotExist:
                pass
        elif patient_id:
            try:
                patient = Patient.objects.get(patient_id=patient_id)
                form.fields['patient'].initial = patient
            except Patient.DoesNotExist:
                pass

        form.fields['template'].initial = ReportTemplate.objects.filter(is_default=True).first()

    available_templates = ReportTemplate.objects.filter(is_default=True)
    context = {
        'form': form,
        'available_templates': available_templates
    }
    return render(request, 'reports/generate_report.html', context)


def report_detail(request, report_id):
    """View report details"""
    report = get_object_or_404(Report, report_id=report_id)

    if request.method == 'POST' and 'sign_report' in request.POST:
        if request.user.is_authenticated:
            report.signed_by = request.user
            report.signed_date = timezone.now()
            report.status = 'SIGNED'
            report.save()
            messages.success(request, 'Report signed successfully!')
            return redirect('report_detail', report_id=report.report_id)

    context = {
        'report': report,
        'tests': report.tests.all(),
        'can_sign': request.user.is_authenticated and not report.signed_by
    }
    return render(request, 'reports/report_detail.html', context)


def download_report(request, report_id):
    """Download report PDF"""
    report = get_object_or_404(Report, report_id=report_id)

    if not report.report_file and report.report_format == 'PDF':
        try:
            pdf_generator = LabReportGenerator(report)
            pdf_content = pdf_generator.generate_pdf()
            filename = f"report_{report.report_id}.pdf"
            report.report_file.save(
                filename,
                ContentFile(pdf_content),
                save=True
            )
        except Exception as e:
            messages.error(request, f'Error generating PDF: {str(e)}')
            return redirect('report_detail', report_id=report_id)

    if not report.report_file:
        raise Http404("Report file not found")

    response = HttpResponse(report.report_file.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="report_{report.report_id}.pdf"'
    return response


@login_required
def batch_generate_reports(request):
    """Generate multiple reports for selected tests"""
    if request.method == 'POST':
        test_ids = request.POST.getlist('test_ids')
        template_id = request.POST.get('template_id')

        if not test_ids or not template_id:
            messages.error(request, 'Please select tests and a template.')
            return redirect('test_list')

        try:
            template = ReportTemplate.objects.get(id=template_id)
            reports_created = []

            for test_id in test_ids:
                test = Test.objects.get(test_id=test_id)

                existing_report = Report.objects.filter(
                    patient=test.patient,
                    tests=test
                ).first()

                if existing_report:
                    continue

                report = Report.objects.create(
                    patient=test.patient,
                    template=template,
                    generated_by=request.user
                )
                report.tests.add(test)

                pdf_generator = LabReportGenerator(report)
                pdf_content = pdf_generator.generate_pdf()

                filename = f"report_{report.report_id}.pdf"
                report.report_file.save(
                    filename,
                    ContentFile(pdf_content),
                    save=True
                )

                report.status = 'GENERATED'
                report.save()
                reports_created.append(report.report_id)

            if reports_created:
                messages.success(request, f'Successfully generated {len(reports_created)} reports: {", ".join(reports_created)}')
            else:
                messages.info(request, 'No new reports were generated. Reports may already exist for selected tests.')

        except Exception as e:
            messages.error(request, f'Error in batch generation: {str(e)}')

    return redirect('test_list')
