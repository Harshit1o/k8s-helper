#!/usr/bin/env python3
"""
Example: Basic web application deployment
This script demonstrates how to deploy a simple web application with k8s-helper
"""

from k8s_helper import K8sClient, format_deployment_list, format_service_list, format_pod_list

def main():
    # Initialize client
    client = K8sClient(namespace="web-app-example")
    
    print("🚀 Deploying web application...")
    
    # Create deployment
    print("\n1. Creating deployment...")
    deployment_result = client.create_deployment(
        name="web-app",
        image="nginx:latest",
        replicas=3,
        container_port=80,
        env_vars={
            "ENV": "production",
            "LOG_LEVEL": "info"
        },
        labels={
            "app": "web-app",
            "tier": "frontend",
            "version": "v1.0"
        }
    )
    
    if not deployment_result:
        print("❌ Failed to create deployment")
        return
    
    # Create service
    print("\n2. Creating service...")
    service_result = client.create_service(
        name="web-app-service",
        port=80,
        target_port=80,
        service_type="ClusterIP",
        selector={"app": "web-app"}
    )
    
    if not service_result:
        print("❌ Failed to create service")
        return
    
    # Wait for deployment to be ready
    print("\n3. Waiting for deployment to be ready...")
    if client.wait_for_deployment_ready("web-app", timeout=300):
        print("✅ Deployment is ready!")
    else:
        print("❌ Deployment failed to become ready")
        return
    
    # Show status
    print("\n4. Application status:")
    print("\nDeployments:")
    deployments = client.list_deployments()
    print(format_deployment_list(deployments))
    
    print("\nServices:")
    services = client.list_services()
    print(format_service_list(services))
    
    print("\nPods:")
    pods = client.list_pods()
    print(format_pod_list(pods))
    
    # Show resource summary
    print("\n5. Resource summary:")
    resources = client.get_namespace_resources()
    for resource, count in resources.items():
        print(f"  {resource.capitalize()}: {count}")
    
    print("\n✅ Web application deployed successfully!")
    print(f"Access your application at: http://web-app-service.web-app-example.svc.cluster.local")


if __name__ == "__main__":
    main()
