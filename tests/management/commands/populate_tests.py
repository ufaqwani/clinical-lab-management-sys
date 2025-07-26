from django.core.management.base import BaseCommand
from tests.models import TestCategory, TestType

class Command(BaseCommand):
    help = 'Populate test categories and types'

    def handle(self, *args, **options):
        # Create Test Categories
        categories_data = [
            {'name': 'Hematology', 'code': 'HEM', 'description': 'Blood cell analysis and coagulation studies'},
            {'name': 'Clinical Chemistry', 'code': 'CHEM', 'description': 'Biochemical analysis of blood and body fluids'},
            {'name': 'Microbiology', 'code': 'MICRO', 'description': 'Detection and identification of microorganisms'},
            {'name': 'Immunology', 'code': 'IMMUNO', 'description': 'Immune system and antibody testing'},
            {'name': 'Pathology', 'code': 'PATH', 'description': 'Tissue and cellular examination'},
        ]

        for cat_data in categories_data:
            category, created = TestCategory.objects.get_or_create(
                code=cat_data['code'],
                defaults=cat_data
            )
            if created:
                self.stdout.write(f"Created category: {category.name}")

        # Create Test Types
        tests_data = [
            # Hematology Tests
            {'category_code': 'HEM', 'name': 'Complete Blood Count', 'code': 'CBC', 'sample_type': 'Blood', 'reference_range': '4.5-11.0 x10³/μL', 'units': 'x10³/μL', 'hours': 2, 'cost': 25.00},
            {'category_code': 'HEM', 'name': 'Hemoglobin', 'code': 'HGB', 'sample_type': 'Blood', 'reference_range': '12.0-15.5 g/dL', 'units': 'g/dL', 'hours': 1, 'cost': 15.00},
            {'category_code': 'HEM', 'name': 'Platelet Count', 'code': 'PLT', 'sample_type': 'Blood', 'reference_range': '150-450 x10³/μL', 'units': 'x10³/μL', 'hours': 1, 'cost': 20.00},
            
            # Clinical Chemistry Tests
            {'category_code': 'CHEM', 'name': 'Blood Glucose', 'code': 'GLU', 'sample_type': 'Blood', 'reference_range': '70-100 mg/dL', 'units': 'mg/dL', 'hours': 1, 'cost': 10.00},
            {'category_code': 'CHEM', 'name': 'Cholesterol Total', 'code': 'CHOL', 'sample_type': 'Blood', 'reference_range': '<200 mg/dL', 'units': 'mg/dL', 'hours': 2, 'cost': 18.00},
            {'category_code': 'CHEM', 'name': 'Creatinine', 'code': 'CREAT', 'sample_type': 'Blood', 'reference_range': '0.6-1.2 mg/dL', 'units': 'mg/dL', 'hours': 2, 'cost': 12.00},
            
            # Microbiology Tests
            {'category_code': 'MICRO', 'name': 'Urine Culture', 'code': 'UCULT', 'sample_type': 'Urine', 'reference_range': 'No growth', 'units': 'CFU/mL', 'hours': 48, 'cost': 30.00},
            {'category_code': 'MICRO', 'name': 'Blood Culture', 'code': 'BCULT', 'sample_type': 'Blood', 'reference_range': 'No growth', 'units': 'CFU/mL', 'hours': 72, 'cost': 45.00},
            
            # Immunology Tests
            {'category_code': 'IMMUNO', 'name': 'HIV Antibody', 'code': 'HIV', 'sample_type': 'Blood', 'reference_range': 'Non-reactive', 'units': '', 'hours': 4, 'cost': 35.00},
            {'category_code': 'IMMUNO', 'name': 'Hepatitis B Surface Antigen', 'code': 'HBSAG', 'sample_type': 'Blood', 'reference_range': 'Non-reactive', 'units': '', 'hours': 3, 'cost': 28.00},
        ]

        for test_data in tests_data:
            category = TestCategory.objects.get(code=test_data.pop('category_code'))
            test_type, created = TestType.objects.get_or_create(
                code=test_data['code'],
                defaults={
                    'category': category,
                    'name': test_data['name'],
                    'sample_type': test_data['sample_type'],
                    'reference_range': test_data['reference_range'],
                    'units': test_data['units'],
                    'normal_turnaround_time': test_data['hours'],
                    'cost': test_data['cost'],
                    'description': f"{test_data['name']} - {test_data['sample_type']} sample"
                }
            )
            if created:
                self.stdout.write(f"Created test: {test_type.name}")

        self.stdout.write(self.style.SUCCESS('Successfully populated test data'))
