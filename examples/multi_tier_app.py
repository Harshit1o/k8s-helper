#!/usr/bin/env python3
"""
Example: Multi-tier application deployment
This script demonstrates deploying a multi-tier application (frontend + backend + database)
"""

from k8s_helper import K8sClient, format_deployment_list, format_service_list
import time

def deploy_database(client):
    """Deploy database tier"""
    print("📊 Deploying database...")
    
    # Create database deployment
    db_result = client.create_deployment(
        name="database",
        image="postgres:13",
        replicas=1,
        container_port=5432,
        env_vars={
            "POSTGRES_DB": "myapp",
            "POSTGRES_USER": "user",
            "POSTGRES_PASSWORD": "password"
        },
        labels={
            "app": "database",
            "tier": "database"
        }
    )
    
    if not db_result:
        return False
    
    # Create database service
    db_service = client.create_service(
        name="database-service",
        port=5432,
        target_port=5432,
        service_type="ClusterIP",
        selector={"app": "database"}
    )
    
    return db_service is not None


def deploy_backend(client):
    """Deploy backend tier"""
    print("🔧 Deploying backend...")
    
    # Create backend deployment
    backend_result = client.create_deployment(
        name="backend",
        image="python:3.9-slim",
        replicas=2,
        container_port=8000,
        env_vars={
            "DATABASE_URL": "postgresql://user:password@database-service:5432/myapp",
            "ENV": "production"
        },
        labels={
            "app": "backend",
            "tier": "backend"
        }
    )
    
    if not backend_result:
        return False
    
    # Create backend service
    backend_service = client.create_service(
        name="backend-service",
        port=8000,
        target_port=8000,
        service_type="ClusterIP",
        selector={"app": "backend"}
    )
    
    return backend_service is not None


def deploy_frontend(client):
    """Deploy frontend tier"""
    print("🎨 Deploying frontend...")
    
    # Create frontend deployment
    frontend_result = client.create_deployment(
        name="frontend",
        image="nginx:alpine",
        replicas=3,
        container_port=80,
        env_vars={
            "BACKEND_URL": "http://backend-service:8000",
            "ENV": "production"
        },
        labels={
            "app": "frontend",
            "tier": "frontend"
        }
    )
    
    if not frontend_result:
        return False
    
    # Create frontend service (LoadBalancer for external access)
    frontend_service = client.create_service(
        name="frontend-service",
        port=80,
        target_port=80,
        service_type="LoadBalancer",
        selector={"app": "frontend"}
    )
    
    return frontend_service is not None


def wait_for_deployments(client, deployments):
    """Wait for all deployments to be ready"""
    print("\n⏳ Waiting for all deployments to be ready...")
    
    for deployment in deployments:
        print(f"  Waiting for {deployment}...")
        if not client.wait_for_deployment_ready(deployment, timeout=300):
            print(f"❌ {deployment} failed to become ready")
            return False
        print(f"  ✅ {deployment} is ready")
    
    return True


def show_application_status(client):
    """Show the status of the entire application"""
    print("\n📊 Application Status:")
    
    # Show deployments
    print("\nDeployments:")
    deployments = client.list_deployments()
    print(format_deployment_list(deployments))
    
    # Show services
    print("\nServices:")
    services = client.list_services()
    print(format_service_list(services))
    
    # Show resource summary
    print("\nResource Summary:")
    resources = client.get_namespace_resources()
    for resource, count in resources.items():
        print(f"  {resource.capitalize()}: {count}")


def main():
    # Initialize client
    client = K8sClient(namespace="multi-tier-app")
    
    print("🚀 Deploying multi-tier application...")
    print("This will deploy: Database -> Backend -> Frontend")
    
    # Deploy tiers in order
    success = True
    
    # 1. Deploy database first
    if not deploy_database(client):
        print("❌ Database deployment failed")
        return
    
    # Wait a bit for database to start
    print("⏳ Waiting for database to initialize...")
    time.sleep(10)
    
    # 2. Deploy backend
    if not deploy_backend(client):
        print("❌ Backend deployment failed")
        return
    
    # 3. Deploy frontend
    if not deploy_frontend(client):
        print("❌ Frontend deployment failed")
        return
    
    # Wait for all deployments to be ready
    deployments = ["database", "backend", "frontend"]
    if not wait_for_deployments(client, deployments):
        print("❌ Some deployments failed to become ready")
        return
    
    # Show final status
    show_application_status(client)
    
    print("\n✅ Multi-tier application deployed successfully!")
    print("\nApplication Architecture:")
    print("  Frontend (nginx) -> Backend (python) -> Database (postgres)")
    print("  Frontend exposed via LoadBalancer")
    print("  Backend and Database are internal services")


if __name__ == "__main__":
    main()
