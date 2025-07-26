import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clms_project.settings')
django.setup()

from django.urls import reverse
from patients.models import Patient
from tests.models import Test, TestType
from reports.models import Report

def test_system():
    print("=== CLMS System Debug ===")
    
    # Test URL reversals
    urls_to_test = [
        'home', 'patient_list', 'patient_create', 
        'test_list', 'test_order', 'generate_report', 'report_list'
    ]
    
    print("\n1. Testing URL reversals:")
    for url_name in urls_to_test:
        try:
            url = reverse(url_name)
            print(f"✓ {url_name}: {url}")
        except Exception as e:
            print(f"✗ {url_name}: {e}")
    
    # Test model relationships
    print("\n2. Testing models:")
    print(f"Patients: {Patient.objects.count()}")
    print(f"Tests: {Test.objects.count()}")
    print(f"Reports: {Report.objects.count()}")
    
    # Test completed tests
    completed_tests = Test.objects.filter(status='COMPLETED')
    print(f"Completed tests: {completed_tests.count()}")
    
    print("\n=== Debug Complete ===")

if __name__ == "__main__":
    test_system()
