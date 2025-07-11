#!/usr/bin/env python3
"""
Example: Cleanup script for removing applications
This script demonstrates how to clean up resources created by k8s-helper
"""

from k8s_helper import K8sClient, format_deployment_list, format_service_list, format_pod_list

def cleanup_application(client, app_name):
    """Clean up a specific application"""
    print(f"🧹 Cleaning up application: {app_name}")
    
    # Delete deployment
    print(f"  Deleting deployment: {app_name}")
    if client.delete_deployment(app_name):
        print(f"  ✅ Deployment {app_name} deleted")
    else:
        print(f"  ❌ Failed to delete deployment {app_name}")
    
    # Delete service
    service_name = f"{app_name}-service"
    print(f"  Deleting service: {service_name}")
    if client.delete_service(service_name):
        print(f"  ✅ Service {service_name} deleted")
    else:
        print(f"  ❌ Failed to delete service {service_name}")


def cleanup_namespace(client, namespace):
    """Clean up all resources in a namespace"""
    print(f"🧹 Cleaning up namespace: {namespace}")
    
    # Get all resources
    deployments = client.list_deployments()
    services = client.list_services()
    pods = client.list_pods()
    
    print(f"\nFound resources to clean up:")
    print(f"  Deployments: {len(deployments)}")
    print(f"  Services: {len(services)}")
    print(f"  Pods: {len(pods)}")
    
    if not deployments and not services and not pods:
        print("  No resources found to clean up")
        return
    
    # Show what will be deleted
    if deployments:
        print("\nDeployments to delete:")
        for deployment in deployments:
            print(f"  - {deployment['name']}")
    
    if services:
        print("\nServices to delete:")
        for service in services:
            print(f"  - {service['name']}")
    
    # Ask for confirmation
    response = input("\nProceed with cleanup? (y/N): ")
    if response.lower() != 'y':
        print("❌ Cleanup cancelled")
        return
    
    # Delete deployments
    if deployments:
        print("\nDeleting deployments...")
        for deployment in deployments:
            name = deployment['name']
            if client.delete_deployment(name):
                print(f"  ✅ Deleted deployment: {name}")
            else:
                print(f"  ❌ Failed to delete deployment: {name}")
    
    # Delete services
    if services:
        print("\nDeleting services...")
        for service in services:
            name = service['name']
            if client.delete_service(name):
                print(f"  ✅ Deleted service: {name}")
            else:
                print(f"  ❌ Failed to delete service: {name}")
    
    print("\n✅ Cleanup completed!")


def show_cleanup_status(client):
    """Show remaining resources after cleanup"""
    print("\n📊 Remaining resources:")
    
    resources = client.get_namespace_resources()
    for resource, count in resources.items():
        print(f"  {resource.capitalize()}: {count}")
    
    if sum(resources.values()) == 0:
        print("  🎉 Namespace is clean!")


def main():
    print("🧹 k8s-helper Cleanup Script")
    print("This script helps you clean up Kubernetes resources")
    
    # Get namespace
    namespace = input("Enter namespace to clean up (default: default): ").strip()
    if not namespace:
        namespace = "default"
    
    client = K8sClient(namespace=namespace)
    
    # Show current resources
    print(f"\n📊 Current resources in namespace '{namespace}':")
    
    deployments = client.list_deployments()
    services = client.list_services()
    pods = client.list_pods()
    
    if deployments:
        print("\nDeployments:")
        print(format_deployment_list(deployments))
    
    if services:
        print("\nServices:")
        print(format_service_list(services))
    
    if pods:
        print("\nPods:")
        print(format_pod_list(pods))
    
    if not deployments and not services and not pods:
        print("  No resources found")
        return
    
    # Cleanup options
    print("\nCleanup options:")
    print("1. Clean up specific application")
    print("2. Clean up entire namespace")
    print("3. Exit")
    
    choice = input("Select option (1-3): ").strip()
    
    if choice == "1":
        app_name = input("Enter application name: ").strip()
        if app_name:
            cleanup_application(client, app_name)
        else:
            print("❌ Invalid application name")
    
    elif choice == "2":
        cleanup_namespace(client, namespace)
    
    elif choice == "3":
        print("👋 Goodbye!")
        return
    
    else:
        print("❌ Invalid choice")
        return
    
    # Show final status
    show_cleanup_status(client)


if __name__ == "__main__":
    main()
