#!/usr/bin/env python3
"""
Comprehensive Test Runner for GitHub Commit Tracker

This script runs all unit tests, functional tests, and generates coverage reports
for the entire microservices architecture.

Usage:
    python run_tests.py                    # Run all tests
    python run_tests.py --unit             # Run only unit tests
    python run_tests.py --functional       # Run only functional tests
    python run_tests.py --coverage         # Run tests with coverage report
    python run_tests.py --service github   # Run tests for specific service
"""

import os
import sys
import subprocess
import argparse
import time
from pathlib import Path

def run_command(command, cwd=None, capture_output=False):
    """Run a command and return the result."""
    try:
        if capture_output:
            result = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True)
        else:
            result = subprocess.run(command, shell=True, cwd=cwd)
        return result.returncode == 0, result.stdout if capture_output else None
    except Exception as e:
        print(f"❌ Error running command: {e}")
        return False, None

def check_docker_services():
    """Check if Docker services are running."""
    print("🔍 Checking Docker services...")
    
    services = [
        "commit-tracker-api-gateway",
        "commit-tracker-github-service", 
        "commit-tracker-ai-service",
        "commit-tracker-postgres"
    ]
    
    success, output = run_command("docker-compose ps", capture_output=True)
    if not success:
        print("❌ Docker Compose not available or services not running")
        return False
    
    for service in services:
        if service not in output:
            print(f"❌ Service {service} not running")
            return False
    
    print("✅ All Docker services are running")
    return True

def run_unit_tests(service=None):
    """Run unit tests for specified service or all services."""
    print("\n🧪 Running Unit Tests...")
    
    services = {
        "github": "services/github-service",
        "api-gateway": "services/api-gateway", 
        "ai": "services/ai-service"
    }
    
    if service and service not in services:
        print(f"❌ Unknown service: {service}")
        return False
    
    test_services = [services[service]] if service else services.values()
    
    all_passed = True
    
    for service_path in test_services:
        if not os.path.exists(service_path):
            print(f"⚠️ Service path not found: {service_path}")
            continue
            
        print(f"\n📦 Testing {service_path}...")
        
        # Install dependencies if needed
        if os.path.exists(os.path.join(service_path, "requirements.txt")):
            print("📦 Installing dependencies...")
            success, _ = run_command("pip install -r requirements.txt", cwd=service_path)
            if not success:
                print(f"❌ Failed to install dependencies for {service_path}")
                all_passed = False
                continue
        
        # Run tests
        test_command = "python -m pytest tests/ -v --tb=short"
        success, output = run_command(test_command, cwd=service_path, capture_output=True)
        
        if success:
            print(f"✅ {service_path} tests passed")
            if output:
                print(output)
        else:
            print(f"❌ {service_path} tests failed")
            if output:
                print(output)
            all_passed = False
    
    return all_passed

def run_functional_tests():
    """Run functional tests for the entire system."""
    print("\n🔗 Running Functional Tests...")
    
    # Check if services are running
    if not check_docker_services():
        print("❌ Docker services not running. Please start them first:")
        print("   docker-compose up -d")
        return False
    
    # Wait for services to be ready
    print("⏳ Waiting for services to be ready...")
    time.sleep(10)
    
    # Install test dependencies
    print("📦 Installing test dependencies...")
    run_command("pip install pytest requests")
    
    # Run functional tests
    print("🧪 Running functional tests...")
    success, output = run_command("python -m pytest tests/test_functional.py -v", capture_output=True)
    
    if success:
        print("✅ Functional tests passed")
        if output:
            print(output)
    else:
        print("❌ Functional tests failed")
        if output:
            print(output)
    
    return success

def run_coverage_tests():
    """Run tests with coverage reporting."""
    print("\n📊 Running Tests with Coverage...")
    
    services = {
        "github": "services/github-service",
        "api-gateway": "services/api-gateway", 
        "ai": "services/ai-service"
    }
    
    all_passed = True
    
    for service_name, service_path in services.items():
        if not os.path.exists(service_path):
            print(f"⚠️ Service path not found: {service_path}")
            continue
            
        print(f"\n📦 Running coverage for {service_name}...")
        
        # Install dependencies
        if os.path.exists(os.path.join(service_path, "requirements.txt")):
            run_command("pip install -r requirements.txt", cwd=service_path)
        
        # Run tests with coverage
        coverage_command = "python -m pytest tests/ -v --cov=. --cov-report=html --cov-report=term-missing"
        success, output = run_command(coverage_command, cwd=service_path, capture_output=True)
        
        if success:
            print(f"✅ {service_name} coverage tests passed")
            if output:
                print(output)
            
            # Check coverage report
            coverage_html = os.path.join(service_path, "htmlcov", "index.html")
            if os.path.exists(coverage_html):
                print(f"📊 Coverage report: {coverage_html}")
        else:
            print(f"❌ {service_name} coverage tests failed")
            if output:
                print(output)
            all_passed = False
    
    return all_passed

def generate_test_report():
    """Generate a comprehensive test report."""
    print("\n📋 Generating Test Report...")
    
    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "services": {},
        "functional_tests": False,
        "overall_status": "PENDING"
    }
    
    # Check each service
    services = {
        "github": "services/github-service",
        "api-gateway": "services/api-gateway", 
        "ai": "services/ai-service"
    }
    
    for service_name, service_path in services.items():
        if os.path.exists(service_path):
            report["services"][service_name] = {
                "path": service_path,
                "tests_exist": os.path.exists(os.path.join(service_path, "tests")),
                "status": "UNKNOWN"
            }
    
    # Save report
    report_file = "test_report.json"
    import json
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"📋 Test report saved to: {report_file}")
    return report

def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="GitHub Commit Tracker Test Runner")
    parser.add_argument("--unit", action="store_true", help="Run only unit tests")
    parser.add_argument("--functional", action="store_true", help="Run only functional tests")
    parser.add_argument("--coverage", action="store_true", help="Run tests with coverage")
    parser.add_argument("--service", choices=["github", "api-gateway", "ai"], help="Run tests for specific service")
    parser.add_argument("--report", action="store_true", help="Generate test report")
    
    args = parser.parse_args()
    
    print("🚀 GitHub Commit Tracker Test Runner")
    print("=" * 50)
    
    # Generate report if requested
    if args.report:
        generate_test_report()
        return
    
    # Run tests based on arguments
    if args.unit:
        success = run_unit_tests(args.service)
    elif args.functional:
        success = run_functional_tests()
    elif args.coverage:
        success = run_coverage_tests()
    else:
        # Run all tests
        print("🧪 Running All Tests...")
        
        unit_success = run_unit_tests(args.service)
        functional_success = run_functional_tests()
        coverage_success = run_coverage_tests()
        
        success = unit_success and functional_success and coverage_success
    
    # Final status
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
