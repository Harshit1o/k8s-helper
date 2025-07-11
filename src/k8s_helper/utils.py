"""
Utility functions for k8s-helper
"""

from typing import Dict, List, Any, Optional
import yaml
import json
from datetime import datetime, timezone
import re


def format_age(timestamp) -> str:
    """Format a timestamp to show age (e.g., '2d', '3h', '45m')"""
    if not timestamp:
        return "Unknown"
    
    now = datetime.now(timezone.utc)
    if hasattr(timestamp, 'replace'):
        # Handle timezone-aware datetime
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)
    
    diff = now - timestamp
    
    days = diff.days
    hours, remainder = divmod(diff.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    
    if days > 0:
        return f"{days}d"
    elif hours > 0:
        return f"{hours}h"
    elif minutes > 0:
        return f"{minutes}m"
    else:
        return "Just now"


def format_resource_table(resources: List[Dict[str, Any]], headers: List[str]) -> str:
    """Format a list of resources as a table"""
    if not resources:
        return "No resources found"
    
    # Calculate column widths
    col_widths = {}
    for header in headers:
        col_widths[header] = len(header)
    
    for resource in resources:
        for header in headers:
            value = str(resource.get(header, 'N/A'))
            col_widths[header] = max(col_widths[header], len(value))
    
    # Build the table
    header_line = " | ".join(header.ljust(col_widths[header]) for header in headers)
    separator = "-" * len(header_line)
    
    lines = [header_line, separator]
    
    for resource in resources:
        row = " | ".join(str(resource.get(header, 'N/A')).ljust(col_widths[header]) for header in headers)
        lines.append(row)
    
    return "\n".join(lines)


def format_pod_list(pods: List[Dict[str, Any]]) -> str:
    """Format pod list for display"""
    if not pods:
        return "No pods found"
    
    formatted_pods = []
    for pod in pods:
        formatted_pod = {
            'NAME': pod['name'],
            'READY': '1/1' if pod['ready'] else '0/1',
            'STATUS': pod['phase'],
            'RESTARTS': pod['restarts'],
            'AGE': format_age(pod['age']),
            'NODE': pod.get('node', 'N/A')
        }
        formatted_pods.append(formatted_pod)
    
    return format_resource_table(formatted_pods, ['NAME', 'READY', 'STATUS', 'RESTARTS', 'AGE', 'NODE'])


def format_deployment_list(deployments: List[Dict[str, Any]]) -> str:
    """Format deployment list for display"""
    if not deployments:
        return "No deployments found"
    
    formatted_deployments = []
    for deployment in deployments:
        formatted_deployment = {
            'NAME': deployment['name'],
            'READY': f"{deployment['ready_replicas']}/{deployment['replicas']}",
            'UP-TO-DATE': deployment['available_replicas'],
            'AVAILABLE': deployment['available_replicas'],
            'AGE': format_age(deployment['created'])
        }
        formatted_deployments.append(formatted_deployment)
    
    return format_resource_table(formatted_deployments, ['NAME', 'READY', 'UP-TO-DATE', 'AVAILABLE', 'AGE'])


def format_service_list(services: List[Dict[str, Any]]) -> str:
    """Format service list for display"""
    if not services:
        return "No services found"
    
    formatted_services = []
    for service in services:
        ports_str = ','.join([f"{port['port']}/{port.get('protocol', 'TCP')}" for port in service['ports']])
        
        formatted_service = {
            'NAME': service['name'],
            'TYPE': service['type'],
            'CLUSTER-IP': service['cluster_ip'],
            'EXTERNAL-IP': service['external_ip'] or '<none>',
            'PORTS': ports_str,
            'AGE': format_age(service['created'])
        }
        formatted_services.append(formatted_service)
    
    return format_resource_table(formatted_services, ['NAME', 'TYPE', 'CLUSTER-IP', 'EXTERNAL-IP', 'PORTS', 'AGE'])


def format_events(events: List[Dict[str, Any]]) -> str:
    """Format events for display"""
    if not events:
        return "No events found"
    
    formatted_events = []
    for event in events:
        formatted_event = {
            'LAST SEEN': format_age(event['last_timestamp'] or event['first_timestamp']),
            'TYPE': event['type'],
            'REASON': event['reason'],
            'OBJECT': event['resource'],
            'MESSAGE': event['message'][:60] + '...' if len(event['message']) > 60 else event['message']
        }
        formatted_events.append(formatted_event)
    
    return format_resource_table(formatted_events, ['LAST SEEN', 'TYPE', 'REASON', 'OBJECT', 'MESSAGE'])


def validate_name(name: str) -> bool:
    """Validate Kubernetes resource name"""
    # K8s names must be lowercase alphanumeric with hyphens, max 63 chars
    pattern = r'^[a-z0-9]([a-z0-9\-]*[a-z0-9])?$'
    return bool(re.match(pattern, name)) and len(name) <= 63


def validate_namespace(namespace: str) -> bool:
    """Validate Kubernetes namespace name"""
    return validate_name(namespace)


def validate_image(image: str) -> bool:
    """Basic validation for Docker image names"""
    # Very basic validation - just check it's not empty and has reasonable format
    return bool(image) and len(image) > 0 and ' ' not in image


def parse_env_vars(env_string: str) -> Dict[str, str]:
    """Parse environment variables from a string like 'KEY1=value1,KEY2=value2'"""
    env_vars = {}
    if not env_string:
        return env_vars
    
    pairs = env_string.split(',')
    for pair in pairs:
        if '=' in pair:
            key, value = pair.split('=', 1)
            env_vars[key.strip()] = value.strip()
    
    return env_vars


def parse_labels(labels_string: str) -> Dict[str, str]:
    """Parse labels from a string like 'key1=value1,key2=value2'"""
    return parse_env_vars(labels_string)  # Same format


def safe_get(dictionary: Dict, key: str, default: Any = None) -> Any:
    """Safely get a value from a dictionary with nested key support"""
    try:
        value = dictionary
        for k in key.split('.'):
            value = value[k]
        return value
    except (KeyError, TypeError):
        return default


def format_yaml_output(data: Any) -> str:
    """Format data as YAML string"""
    try:
        return yaml.dump(data, default_flow_style=False, indent=2)
    except Exception:
        return str(data)


def format_json_output(data: Any) -> str:
    """Format data as JSON string"""
    try:
        return json.dumps(data, indent=2, default=str)
    except Exception:
        return str(data)


def print_status(message: str, status: str = "info"):
    """Print a status message with appropriate emoji"""
    emojis = {
        "success": "✅",
        "error": "❌",
        "warning": "⚠️",
        "info": "ℹ️",
        "loading": "⏳"
    }
    
    emoji = emojis.get(status, "ℹ️")
    print(f"{emoji} {message}")


def create_deployment_manifest(name: str, image: str, replicas: int = 1, 
                             port: int = 80, env_vars: Optional[Dict[str, str]] = None,
                             labels: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """Create a deployment manifest dictionary"""
    if labels is None:
        labels = {"app": name}
    
    env_list = []
    if env_vars:
        env_list = [{"name": k, "value": v} for k, v in env_vars.items()]
    
    manifest = {
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {
            "name": name,
            "labels": labels
        },
        "spec": {
            "replicas": replicas,
            "selector": {
                "matchLabels": labels
            },
            "template": {
                "metadata": {
                    "labels": labels
                },
                "spec": {
                    "containers": [
                        {
                            "name": name,
                            "image": image,
                            "ports": [
                                {
                                    "containerPort": port
                                }
                            ]
                        }
                    ]
                }
            }
        }
    }
    
    if env_list:
        manifest["spec"]["template"]["spec"]["containers"][0]["env"] = env_list
    
    return manifest


def create_service_manifest(name: str, port: int, target_port: int, 
                          service_type: str = "ClusterIP",
                          selector: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """Create a service manifest dictionary"""
    if selector is None:
        selector = {"app": name}
    
    manifest = {
        "apiVersion": "v1",
        "kind": "Service",
        "metadata": {
            "name": name
        },
        "spec": {
            "selector": selector,
            "ports": [
                {
                    "port": port,
                    "targetPort": target_port
                }
            ],
            "type": service_type
        }
    }
    
    return manifest
