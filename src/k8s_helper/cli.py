"""
Command-line interface for k8s-helper
"""

import typer
from typing import Optional, List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from .core import K8sClient
from .config import get_config
from .utils import (
    format_pod_list,
    format_deployment_list,
    format_service_list,
    format_events,
    format_yaml_output,
    format_json_output,
    validate_name,
    validate_image,
    parse_env_vars,
    parse_labels
)
from . import __version__

def version_callback(value: bool):
    """Version callback for the CLI"""
    if value:
        typer.echo(f"k8s-helper-cli version {__version__}")
        raise typer.Exit()

app = typer.Typer(help="k8s-helper: Simplified Kubernetes operations")
console = Console()

@app.callback()
def main(
    version: Optional[bool] = typer.Option(None, "--version", callback=version_callback, is_eager=True, help="Show version and exit")
):
    """Main callback to handle global options"""
    return

# Global options
namespace_option = typer.Option(None, "--namespace", "-n", help="Kubernetes namespace")
output_option = typer.Option("table", "--output", "-o", help="Output format: table, yaml, json")


@app.command()
def config(
    namespace: Optional[str] = typer.Option(None, help="Set default namespace"),
    output_format: Optional[str] = typer.Option(None, help="Set output format"),
    timeout: Optional[int] = typer.Option(None, help="Set default timeout"),
    verbose: Optional[bool] = typer.Option(None, help="Enable verbose output"),
    show: bool = typer.Option(False, "--show", help="Show current configuration")
):
    """Configure k8s-helper settings"""
    config_obj = get_config()
    
    if show:
        console.print(Panel(format_yaml_output(config_obj.to_dict()), title="Current Configuration"))
        return
    
    if namespace:
        config_obj.set_namespace(namespace)
        console.print(f"✅ Default namespace set to: {namespace}")
    
    if output_format:
        try:
            config_obj.set_output_format(output_format)
            console.print(f"✅ Output format set to: {output_format}")
        except ValueError as e:
            console.print(f"❌ {e}")
            return
    
    if timeout:
        config_obj.set_timeout(timeout)
        console.print(f"✅ Timeout set to: {timeout} seconds")
    
    if verbose is not None:
        config_obj.set_verbose(verbose)
        console.print(f"✅ Verbose mode: {'enabled' if verbose else 'disabled'}")
    
    if any([namespace, output_format, timeout, verbose is not None]):
        config_obj.save_config()
        console.print("✅ Configuration saved")


@app.command()
def create_deployment(
    name: str = typer.Argument(..., help="Deployment name"),
    image: str = typer.Argument(..., help="Container image"),
    replicas: int = typer.Option(1, "--replicas", "-r", help="Number of replicas"),
    port: int = typer.Option(80, "--port", "-p", help="Container port"),
    env: Optional[str] = typer.Option(None, "--env", "-e", help="Environment variables (KEY1=value1,KEY2=value2)"),
    labels: Optional[str] = typer.Option(None, "--labels", "-l", help="Labels (key1=value1,key2=value2)"),
    namespace: Optional[str] = namespace_option,
    wait: bool = typer.Option(False, "--wait", help="Wait for deployment to be ready")
):
    """Create a new deployment"""
    if not validate_name(name):
        console.print(f"❌ Invalid deployment name: {name}")
        return
    
    if not validate_image(image):
        console.print(f"❌ Invalid image name: {image}")
        return
    
    # Parse environment variables and labels
    env_vars = parse_env_vars(env) if env else None
    label_dict = parse_labels(labels) if labels else None
    
    # Get client
    ns = namespace or get_config().get_namespace()
    client = K8sClient(namespace=ns)
    
    # Create deployment
    with console.status(f"Creating deployment {name}..."):
        result = client.create_deployment(
            name=name,
            image=image,
            replicas=replicas,
            container_port=port,
            env_vars=env_vars,
            labels=label_dict
        )
    
    if result:
        console.print(f"✅ Deployment {name} created successfully")
        
        if wait:
            with console.status(f"Waiting for deployment {name} to be ready..."):
                if client.wait_for_deployment_ready(name):
                    console.print(f"✅ Deployment {name} is ready")
                else:
                    console.print(f"❌ Deployment {name} failed to become ready")
    else:
        console.print(f"❌ Failed to create deployment {name}")


@app.command()
def delete_deployment(
    name: str = typer.Argument(..., help="Deployment name"),
    namespace: Optional[str] = namespace_option
):
    """Delete a deployment"""
    ns = namespace or get_config().get_namespace()
    client = K8sClient(namespace=ns)
    
    if typer.confirm(f"Are you sure you want to delete deployment {name}?"):
        with console.status(f"Deleting deployment {name}..."):
            if client.delete_deployment(name):
                console.print(f"✅ Deployment {name} deleted successfully")
            else:
                console.print(f"❌ Failed to delete deployment {name}")


@app.command()
def scale_deployment(
    name: str = typer.Argument(..., help="Deployment name"),
    replicas: int = typer.Argument(..., help="Number of replicas"),
    namespace: Optional[str] = namespace_option
):
    """Scale a deployment"""
    ns = namespace or get_config().get_namespace()
    client = K8sClient(namespace=ns)
    
    with console.status(f"Scaling deployment {name} to {replicas} replicas..."):
        if client.scale_deployment(name, replicas):
            console.print(f"✅ Deployment {name} scaled to {replicas} replicas")
        else:
            console.print(f"❌ Failed to scale deployment {name}")


@app.command()
def list_deployments(
    namespace: Optional[str] = namespace_option,
    output: str = output_option
):
    """List deployments"""
    ns = namespace or get_config().get_namespace()
    client = K8sClient(namespace=ns)
    
    deployments = client.list_deployments()
    
    if output == "table":
        console.print(format_deployment_list(deployments))
    elif output == "yaml":
        console.print(format_yaml_output(deployments))
    elif output == "json":
        console.print(format_json_output(deployments))


@app.command()
def create_pod(
    name: str = typer.Argument(..., help="Pod name"),
    image: str = typer.Argument(..., help="Container image"),
    port: int = typer.Option(80, "--port", "-p", help="Container port"),
    env: Optional[str] = typer.Option(None, "--env", "-e", help="Environment variables"),
    labels: Optional[str] = typer.Option(None, "--labels", "-l", help="Labels"),
    namespace: Optional[str] = namespace_option
):
    """Create a new pod"""
    if not validate_name(name):
        console.print(f"❌ Invalid pod name: {name}")
        return
    
    if not validate_image(image):
        console.print(f"❌ Invalid image name: {image}")
        return
    
    env_vars = parse_env_vars(env) if env else None
    label_dict = parse_labels(labels) if labels else None
    
    ns = namespace or get_config().get_namespace()
    client = K8sClient(namespace=ns)
    
    with console.status(f"Creating pod {name}..."):
        result = client.create_pod(
            name=name,
            image=image,
            container_port=port,
            env_vars=env_vars,
            labels=label_dict
        )
    
    if result:
        console.print(f"✅ Pod {name} created successfully")
    else:
        console.print(f"❌ Failed to create pod {name}")


@app.command()
def delete_pod(
    name: str = typer.Argument(..., help="Pod name"),
    namespace: Optional[str] = namespace_option
):
    """Delete a pod"""
    ns = namespace or get_config().get_namespace()
    client = K8sClient(namespace=ns)
    
    if typer.confirm(f"Are you sure you want to delete pod {name}?"):
        with console.status(f"Deleting pod {name}..."):
            if client.delete_pod(name):
                console.print(f"✅ Pod {name} deleted successfully")
            else:
                console.print(f"❌ Failed to delete pod {name}")


@app.command()
def list_pods(
    namespace: Optional[str] = namespace_option,
    output: str = output_option
):
    """List pods"""
    ns = namespace or get_config().get_namespace()
    client = K8sClient(namespace=ns)
    
    pods = client.list_pods()
    
    if output == "table":
        console.print(format_pod_list(pods))
    elif output == "yaml":
        console.print(format_yaml_output(pods))
    elif output == "json":
        console.print(format_json_output(pods))


@app.command()
def create_service(
    name: str = typer.Argument(..., help="Service name"),
    port: int = typer.Argument(..., help="Service port"),
    target_port: Optional[int] = typer.Option(None, help="Target port (defaults to port)"),
    service_type: str = typer.Option("ClusterIP", help="Service type"),
    selector: Optional[str] = typer.Option(None, help="Selector labels"),
    namespace: Optional[str] = namespace_option
):
    """Create a new service"""
    if not validate_name(name):
        console.print(f"❌ Invalid service name: {name}")
        return
    
    if target_port is None:
        target_port = port
    
    selector_dict = parse_labels(selector) if selector else None
    
    ns = namespace or get_config().get_namespace()
    client = K8sClient(namespace=ns)
    
    with console.status(f"Creating service {name}..."):
        result = client.create_service(
            name=name,
            port=port,
            target_port=target_port,
            service_type=service_type,
            selector=selector_dict
        )
    
    if result:
        console.print(f"✅ Service {name} created successfully")
    else:
        console.print(f"❌ Failed to create service {name}")


@app.command()
def delete_service(
    name: str = typer.Argument(..., help="Service name"),
    namespace: Optional[str] = namespace_option
):
    """Delete a service"""
    ns = namespace or get_config().get_namespace()
    client = K8sClient(namespace=ns)
    
    if typer.confirm(f"Are you sure you want to delete service {name}?"):
        with console.status(f"Deleting service {name}..."):
            if client.delete_service(name):
                console.print(f"✅ Service {name} deleted successfully")
            else:
                console.print(f"❌ Failed to delete service {name}")


@app.command()
def list_services(
    namespace: Optional[str] = namespace_option,
    output: str = output_option
):
    """List services"""
    ns = namespace or get_config().get_namespace()
    client = K8sClient(namespace=ns)
    
    services = client.list_services()
    
    if output == "table":
        console.print(format_service_list(services))
    elif output == "yaml":
        console.print(format_yaml_output(services))
    elif output == "json":
        console.print(format_json_output(services))


@app.command()
def logs(
    pod_name: str = typer.Argument(..., help="Pod name"),
    container: Optional[str] = typer.Option(None, help="Container name"),
    tail: Optional[int] = typer.Option(None, help="Number of lines to tail"),
    namespace: Optional[str] = namespace_option
):
    """Get pod logs"""
    ns = namespace or get_config().get_namespace()
    client = K8sClient(namespace=ns)
    
    logs = client.get_logs(pod_name, container_name=container, tail_lines=tail)
    if logs:
        console.print(logs)
    else:
        console.print(f"❌ Failed to get logs for pod {pod_name}")


@app.command()
def events(
    resource: Optional[str] = typer.Option(None, help="Resource name to filter events"),
    namespace: Optional[str] = namespace_option,
    output: str = output_option
):
    """Get events"""
    ns = namespace or get_config().get_namespace()
    client = K8sClient(namespace=ns)
    
    events = client.get_events(resource_name=resource)
    
    if output == "table":
        console.print(format_events(events))
    elif output == "yaml":
        console.print(format_yaml_output(events))
    elif output == "json":
        console.print(format_json_output(events))


@app.command()
def describe(
    resource_type: str = typer.Argument(..., help="Resource type: pod, deployment, service"),
    name: str = typer.Argument(..., help="Resource name"),
    namespace: Optional[str] = namespace_option,
    output: str = output_option
):
    """Describe a resource"""
    ns = namespace or get_config().get_namespace()
    client = K8sClient(namespace=ns)
    
    if resource_type.lower() == "pod":
        info = client.describe_pod(name)
    elif resource_type.lower() == "deployment":
        info = client.describe_deployment(name)
    elif resource_type.lower() == "service":
        info = client.describe_service(name)
    else:
        console.print(f"❌ Unsupported resource type: {resource_type}")
        return
    
    if info:
        if output == "yaml":
            console.print(format_yaml_output(info))
        elif output == "json":
            console.print(format_json_output(info))
        else:
            console.print(format_yaml_output(info))  # Default to YAML for describe
    else:
        console.print(f"❌ Failed to describe {resource_type} {name}")


@app.command()
def status(
    namespace: Optional[str] = namespace_option
):
    """Show namespace status"""
    ns = namespace or get_config().get_namespace()
    client = K8sClient(namespace=ns)
    
    console.print(f"\n[bold]Namespace: {ns}[/bold]")
    
    # Get resource counts
    resources = client.get_namespace_resources()
    
    table = Table(title="Resource Summary")
    table.add_column("Resource", style="cyan")
    table.add_column("Count", style="magenta")
    
    for resource, count in resources.items():
        table.add_row(resource.capitalize(), str(count))
    
    console.print(table)
    
    # Show recent events
    events = client.get_events()
    if events:
        console.print(f"\n[bold]Recent Events (last 5):[/bold]")
        recent_events = events[:5]
        for event in recent_events:
            event_type = event['type']
            color = "green" if event_type == "Normal" else "red"
            console.print(f"[{color}]{event['type']}[/{color}] {event['reason']}: {event['message']}")


@app.command()
def apply(
    name: str = typer.Argument(..., help="Application name"),
    image: str = typer.Argument(..., help="Container image"),
    replicas: int = typer.Option(1, "--replicas", "-r", help="Number of replicas"),
    port: int = typer.Option(80, "--port", "-p", help="Container port"),
    service_type: str = typer.Option("ClusterIP", help="Service type"),
    env: Optional[str] = typer.Option(None, "--env", "-e", help="Environment variables"),
    labels: Optional[str] = typer.Option(None, "--labels", "-l", help="Labels"),
    namespace: Optional[str] = namespace_option,
    wait: bool = typer.Option(True, "--wait/--no-wait", help="Wait for deployment to be ready")
):
    """Deploy an application (deployment + service)"""
    if not validate_name(name):
        console.print(f"❌ Invalid application name: {name}")
        return
    
    if not validate_image(image):
        console.print(f"❌ Invalid image name: {image}")
        return
    
    env_vars = parse_env_vars(env) if env else None
    label_dict = parse_labels(labels) if labels else None
    
    ns = namespace or get_config().get_namespace()
    client = K8sClient(namespace=ns)
    
    console.print(f"🚀 Deploying application: {name}")
    
    # Create deployment
    with console.status(f"Creating deployment {name}..."):
        deployment_result = client.create_deployment(
            name=name,
            image=image,
            replicas=replicas,
            container_port=port,
            env_vars=env_vars,
            labels=label_dict
        )
    
    if not deployment_result:
        console.print(f"❌ Failed to create deployment {name}")
        return
    
    # Create service
    with console.status(f"Creating service {name}-service..."):
        service_result = client.create_service(
            name=f"{name}-service",
            port=port,
            target_port=port,
            service_type=service_type,
            selector=label_dict or {"app": name}
        )
    
    if not service_result:
        console.print(f"❌ Failed to create service {name}-service")
        return
    
    console.print(f"✅ Application {name} deployed successfully")
    
    if wait:
        with console.status(f"Waiting for deployment {name} to be ready..."):
            if client.wait_for_deployment_ready(name):
                console.print(f"✅ Application {name} is ready")
            else:
                console.print(f"❌ Application {name} failed to become ready")


@app.command()
def cleanup(
    name: str = typer.Argument(..., help="Application name"),
    namespace: Optional[str] = namespace_option
):
    """Clean up an application (delete deployment + service)"""
    ns = namespace or get_config().get_namespace()
    client = K8sClient(namespace=ns)
    
    if typer.confirm(f"Are you sure you want to delete application {name} and its service?"):
        console.print(f"🧹 Cleaning up application: {name}")
        
        # Delete deployment
        with console.status(f"Deleting deployment {name}..."):
            deployment_deleted = client.delete_deployment(name)
        
        # Delete service
        with console.status(f"Deleting service {name}-service..."):
            service_deleted = client.delete_service(f"{name}-service")
        
        if deployment_deleted and service_deleted:
            console.print(f"✅ Application {name} cleaned up successfully")
        else:
            console.print(f"⚠️  Partial cleanup completed for application {name}")


if __name__ == "__main__":
    app()
