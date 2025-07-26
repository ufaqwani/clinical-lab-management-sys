from django.core.management.base import BaseCommand
from reports.models import ReportTemplate, ReportSection

class Command(BaseCommand):
    help = 'Create default report template'

    def handle(self, *args, **options):
        # Create default template
        template, created = ReportTemplate.objects.get_or_create(
            name='Standard Laboratory Report',
            defaults={
                'description': 'Standard clinical laboratory report template',
                'template_type': 'standard',
                'footer_text': 'This report is electronically generated and digitally signed. All results have been reviewed by qualified laboratory personnel.',
                'is_default': True
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created default template: {template.name}'))
        else:
            self.stdout.write(f'Template already exists: {template.name}')

        # Create template sections
        sections_data = [
            {'section_type': 'HEADER', 'title': 'Laboratory Header', 'content_template': 'Laboratory report header', 'order': 1},
            {'section_type': 'PATIENT_INFO', 'title': 'Patient Information', 'content_template': 'Patient demographics and details', 'order': 2},
            {'section_type': 'TEST_RESULTS', 'title': 'Test Results', 'content_template': 'Laboratory test results and values', 'order': 3},
            {'section_type': 'FOOTER', 'title': 'Report Footer', 'content_template': 'Report footer with signatures', 'order': 4},
        ]
        
        for section_data in sections_data:
            section, created = ReportSection.objects.get_or_create(
                template=template,
                section_type=section_data['section_type'],
                defaults=section_data
            )
            if created:
                self.stdout.write(f'Created section: {section.title}')

        self.stdout.write(self.style.SUCCESS('Default report template setup complete'))
