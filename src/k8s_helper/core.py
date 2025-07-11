from kubernetes import client, config
from kubernetes.client.rest import ApiException
from typing import Dict, List, Optional, Any
import yaml


class K8sClient:
    def __init__(self, namespace="default"):
        try:
            config.load_kube_config()  # Loads from ~/.kube/config
        except:
            config.load_incluster_config()  # For running inside a cluster

        self.namespace = namespace
        self.apps_v1 = client.AppsV1Api()
        self.core_v1 = client.CoreV1Api()

    # ======================
    # DEPLOYMENT OPERATIONS
    # ======================
    def create_deployment(self, name: str, image: str, replicas: int = 1, 
                         container_port: int = 80, env_vars: Optional[Dict[str, str]] = None,
                         labels: Optional[Dict[str, str]] = None) -> Optional[Any]:
        """Create a Kubernetes deployment"""
        if labels is None:
            labels = {"app": name}
        
        # Environment variables
        env = []
        if env_vars:
            env = [client.V1EnvVar(name=k, value=v) for k, v in env_vars.items()]
        
        container = client.V1Container(
            name=name,
            image=image,
            ports=[client.V1ContainerPort(container_port=container_port)],
            env=env if env else None
        )

        template = client.V1PodTemplateSpec(
            metadata=client.V1ObjectMeta(labels=labels),
            spec=client.V1PodSpec(containers=[container])
        )

        spec = client.V1DeploymentSpec(
            replicas=replicas,
            template=template,
            selector=client.V1LabelSelector(match_labels=labels)
        )

        deployment = client.V1Deployment(
            metadata=client.V1ObjectMeta(name=name, labels=labels),
            spec=spec
        )

        try:
            resp = self.apps_v1.create_namespaced_deployment(
                body=deployment,
                namespace=self.namespace
            )
            print(f"✅ Deployment '{name}' created successfully")
            return resp
        except ApiException as e:
            print(f"❌ Error creating deployment '{name}': {e}")
            return None

    def delete_deployment(self, name: str) -> bool:
        """Delete a Kubernetes deployment"""
        try:
            self.apps_v1.delete_namespaced_deployment(
                name=name,
                namespace=self.namespace
            )
            print(f"✅ Deployment '{name}' deleted successfully")
            return True
        except ApiException as e:
            print(f"❌ Error deleting deployment '{name}': {e}")
            return False

    def scale_deployment(self, name: str, replicas: int) -> bool:
        """Scale a deployment to the specified number of replicas"""
        try:
            # Get current deployment
            deployment = self.apps_v1.read_namespaced_deployment(
                name=name,
                namespace=self.namespace
            )
            
            # Update replicas
            deployment.spec.replicas = replicas
            
            # Apply the update
            self.apps_v1.patch_namespaced_deployment(
                name=name,
                namespace=self.namespace,
                body=deployment
            )
            print(f"✅ Deployment '{name}' scaled to {replicas} replicas")
            return True
        except ApiException as e:
            print(f"❌ Error scaling deployment '{name}': {e}")
            return False

    def list_deployments(self) -> List[Dict[str, Any]]:
        """List all deployments in the namespace"""
        try:
            deployments = self.apps_v1.list_namespaced_deployment(namespace=self.namespace)
            result = []
            for deployment in deployments.items:
                result.append({
                    'name': deployment.metadata.name,
                    'replicas': deployment.spec.replicas,
                    'ready_replicas': deployment.status.ready_replicas or 0,
                    'available_replicas': deployment.status.available_replicas or 0,
                    'created': deployment.metadata.creation_timestamp
                })
            return result
        except ApiException as e:
            print(f"❌ Error listing deployments: {e}")
            return []

    # ======================
    # POD OPERATIONS
    # ======================
    def create_pod(self, name: str, image: str, container_port: int = 80,
                   env_vars: Optional[Dict[str, str]] = None,
                   labels: Optional[Dict[str, str]] = None) -> Optional[Any]:
        """Create a simple pod"""
        if labels is None:
            labels = {"app": name}
        
        # Environment variables
        env = []
        if env_vars:
            env = [client.V1EnvVar(name=k, value=v) for k, v in env_vars.items()]
        
        container = client.V1Container(
            name=name,
            image=image,
            ports=[client.V1ContainerPort(container_port=container_port)],
            env=env if env else None
        )

        pod = client.V1Pod(
            metadata=client.V1ObjectMeta(name=name, labels=labels),
            spec=client.V1PodSpec(containers=[container])
        )

        try:
            resp = self.core_v1.create_namespaced_pod(
                body=pod,
                namespace=self.namespace
            )
            print(f"✅ Pod '{name}' created successfully")
            return resp
        except ApiException as e:
            print(f"❌ Error creating pod '{name}': {e}")
            return None

    def delete_pod(self, name: str) -> bool:
        """Delete a pod"""
        try:
            self.core_v1.delete_namespaced_pod(
                name=name,
                namespace=self.namespace
            )
            print(f"✅ Pod '{name}' deleted successfully")
            return True
        except ApiException as e:
            print(f"❌ Error deleting pod '{name}': {e}")
            return False

    def list_pods(self) -> List[Dict[str, Any]]:
        """List all pods in the namespace"""
        try:
            pods = self.core_v1.list_namespaced_pod(namespace=self.namespace)
            result = []
            for pod in pods.items:
                result.append({
                    'name': pod.metadata.name,
                    'phase': pod.status.phase,
                    'ready': self._is_pod_ready(pod),
                    'restarts': self._get_pod_restarts(pod),
                    'age': pod.metadata.creation_timestamp,
                    'node': pod.spec.node_name
                })
            return result
        except ApiException as e:
            print(f"❌ Error listing pods: {e}")
            return []

    def _is_pod_ready(self, pod) -> bool:
        """Check if a pod is ready"""
        if pod.status.conditions:
            for condition in pod.status.conditions:
                if condition.type == "Ready":
                    return condition.status == "True"
        return False

    def _get_pod_restarts(self, pod) -> int:
        """Get the number of restarts for a pod"""
        if pod.status.container_statuses:
            return sum(container.restart_count for container in pod.status.container_statuses)
        return 0

    def get_logs(self, pod_name: str, container_name: Optional[str] = None, 
                 tail_lines: Optional[int] = None) -> Optional[str]:
        """Get logs from a pod"""
        try:
            kwargs = {
                'name': pod_name,
                'namespace': self.namespace
            }
            if container_name:
                kwargs['container'] = container_name
            if tail_lines:
                kwargs['tail_lines'] = tail_lines
                
            logs = self.core_v1.read_namespaced_pod_log(**kwargs)
            print(f"📄 Logs from pod '{pod_name}':")
            print(logs)
            return logs
        except ApiException as e:
            print(f"❌ Error fetching logs from pod '{pod_name}': {e}")
            return None

    # ======================
    # SERVICE OPERATIONS
    # ======================
    def create_service(self, name: str, port: int, target_port: int, 
                      service_type: str = "ClusterIP", 
                      selector: Optional[Dict[str, str]] = None) -> Optional[Any]:
        """Create a Kubernetes service"""
        if selector is None:
            selector = {"app": name}
        
        service = client.V1Service(
            metadata=client.V1ObjectMeta(name=name),
            spec=client.V1ServiceSpec(
                selector=selector,
                ports=[client.V1ServicePort(
                    port=port,
                    target_port=target_port
                )],
                type=service_type
            )
        )

        try:
            resp = self.core_v1.create_namespaced_service(
                body=service,
                namespace=self.namespace
            )
            print(f"✅ Service '{name}' created successfully")
            return resp
        except ApiException as e:
            print(f"❌ Error creating service '{name}': {e}")
            return None

    def delete_service(self, name: str) -> bool:
        """Delete a service"""
        try:
            self.core_v1.delete_namespaced_service(
                name=name,
                namespace=self.namespace
            )
            print(f"✅ Service '{name}' deleted successfully")
            return True
        except ApiException as e:
            print(f"❌ Error deleting service '{name}': {e}")
            return False

    def list_services(self) -> List[Dict[str, Any]]:
        """List all services in the namespace"""
        try:
            services = self.core_v1.list_namespaced_service(namespace=self.namespace)
            result = []
            for service in services.items:
                result.append({
                    'name': service.metadata.name,
                    'type': service.spec.type,
                    'cluster_ip': service.spec.cluster_ip,
                    'external_ip': service.status.load_balancer.ingress[0].ip if (
                        service.status.load_balancer and 
                        service.status.load_balancer.ingress
                    ) else None,
                    'ports': [{'port': port.port, 'target_port': port.target_port} 
                             for port in service.spec.ports],
                    'created': service.metadata.creation_timestamp
                })
            return result
        except ApiException as e:
            print(f"❌ Error listing services: {e}")
            return []

    # ======================
    # EVENTS AND MONITORING
    # ======================
    def get_events(self, resource_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get events from the namespace, optionally filtered by resource name"""
        try:
            events = self.core_v1.list_namespaced_event(namespace=self.namespace)
            result = []
            
            for event in events.items:
                if resource_name and event.involved_object.name != resource_name:
                    continue
                    
                result.append({
                    'name': event.metadata.name,
                    'type': event.type,
                    'reason': event.reason,
                    'message': event.message,
                    'resource': f"{event.involved_object.kind}/{event.involved_object.name}",
                    'first_timestamp': event.first_timestamp,
                    'last_timestamp': event.last_timestamp,
                    'count': event.count
                })
            
            return sorted(result, key=lambda x: x['last_timestamp'] or x['first_timestamp'], reverse=True)
        except ApiException as e:
            print(f"❌ Error fetching events: {e}")
            return []

    # ======================
    # RESOURCE DESCRIPTION
    # ======================
    def describe_pod(self, name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a pod"""
        try:
            pod = self.core_v1.read_namespaced_pod(name=name, namespace=self.namespace)
            
            return {
                'metadata': {
                    'name': pod.metadata.name,
                    'namespace': pod.metadata.namespace,
                    'labels': pod.metadata.labels,
                    'annotations': pod.metadata.annotations,
                    'creation_timestamp': pod.metadata.creation_timestamp
                },
                'spec': {
                    'containers': [
                        {
                            'name': container.name,
                            'image': container.image,
                            'ports': [{'container_port': port.container_port} for port in container.ports] if container.ports else [],
                            'env': [{'name': env.name, 'value': env.value} for env in container.env] if container.env else []
                        }
                        for container in pod.spec.containers
                    ],
                    'restart_policy': pod.spec.restart_policy,
                    'node_name': pod.spec.node_name
                },
                'status': {
                    'phase': pod.status.phase,
                    'conditions': [
                        {
                            'type': condition.type,
                            'status': condition.status,
                            'reason': condition.reason,
                            'message': condition.message
                        }
                        for condition in pod.status.conditions
                    ] if pod.status.conditions else [],
                    'container_statuses': [
                        {
                            'name': status.name,
                            'ready': status.ready,
                            'restart_count': status.restart_count,
                            'state': str(status.state)
                        }
                        for status in pod.status.container_statuses
                    ] if pod.status.container_statuses else []
                }
            }
        except ApiException as e:
            print(f"❌ Error describing pod '{name}': {e}")
            return None

    def describe_deployment(self, name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a deployment"""
        try:
            deployment = self.apps_v1.read_namespaced_deployment(name=name, namespace=self.namespace)
            
            return {
                'metadata': {
                    'name': deployment.metadata.name,
                    'namespace': deployment.metadata.namespace,
                    'labels': deployment.metadata.labels,
                    'annotations': deployment.metadata.annotations,
                    'creation_timestamp': deployment.metadata.creation_timestamp
                },
                'spec': {
                    'replicas': deployment.spec.replicas,
                    'selector': deployment.spec.selector.match_labels,
                    'template': {
                        'metadata': {
                            'labels': deployment.spec.template.metadata.labels
                        },
                        'spec': {
                            'containers': [
                                {
                                    'name': container.name,
                                    'image': container.image,
                                    'ports': [{'container_port': port.container_port} for port in container.ports] if container.ports else []
                                }
                                for container in deployment.spec.template.spec.containers
                            ]
                        }
                    }
                },
                'status': {
                    'replicas': deployment.status.replicas,
                    'ready_replicas': deployment.status.ready_replicas,
                    'available_replicas': deployment.status.available_replicas,
                    'unavailable_replicas': deployment.status.unavailable_replicas,
                    'conditions': [
                        {
                            'type': condition.type,
                            'status': condition.status,
                            'reason': condition.reason,
                            'message': condition.message
                        }
                        for condition in deployment.status.conditions
                    ] if deployment.status.conditions else []
                }
            }
        except ApiException as e:
            print(f"❌ Error describing deployment '{name}': {e}")
            return None

    def describe_service(self, name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a service"""
        try:
            service = self.core_v1.read_namespaced_service(name=name, namespace=self.namespace)
            
            return {
                'metadata': {
                    'name': service.metadata.name,
                    'namespace': service.metadata.namespace,
                    'labels': service.metadata.labels,
                    'annotations': service.metadata.annotations,
                    'creation_timestamp': service.metadata.creation_timestamp
                },
                'spec': {
                    'type': service.spec.type,
                    'selector': service.spec.selector,
                    'ports': [
                        {
                            'port': port.port,
                            'target_port': port.target_port,
                            'protocol': port.protocol
                        }
                        for port in service.spec.ports
                    ],
                    'cluster_ip': service.spec.cluster_ip
                },
                'status': {
                    'load_balancer': {
                        'ingress': [
                            {'ip': ingress.ip, 'hostname': ingress.hostname}
                            for ingress in service.status.load_balancer.ingress
                        ] if service.status.load_balancer and service.status.load_balancer.ingress else []
                    }
                }
            }
        except ApiException as e:
            print(f"❌ Error describing service '{name}': {e}")
            return None

    # ======================
    # UTILITY METHODS
    # ======================
    def get_namespace_resources(self) -> Dict[str, int]:
        """Get a summary of resources in the namespace"""
        try:
            pods = len(self.core_v1.list_namespaced_pod(namespace=self.namespace).items)
            deployments = len(self.apps_v1.list_namespaced_deployment(namespace=self.namespace).items)
            services = len(self.core_v1.list_namespaced_service(namespace=self.namespace).items)
            
            return {
                'pods': pods,
                'deployments': deployments,
                'services': services
            }
        except ApiException as e:
            print(f"❌ Error getting namespace resources: {e}")
            return {}

    def wait_for_deployment_ready(self, name: str, timeout: int = 300) -> bool:
        """Wait for a deployment to be ready"""
        import time
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                deployment = self.apps_v1.read_namespaced_deployment(name=name, namespace=self.namespace)
                if (deployment.status.ready_replicas == deployment.spec.replicas and 
                    deployment.status.ready_replicas > 0):
                    print(f"✅ Deployment '{name}' is ready")
                    return True
                    
                print(f"⏳ Waiting for deployment '{name}' to be ready... ({deployment.status.ready_replicas or 0}/{deployment.spec.replicas})")
                time.sleep(5)
                
            except ApiException as e:
                print(f"❌ Error checking deployment status: {e}")
                return False
        
        print(f"❌ Timeout waiting for deployment '{name}' to be ready")
        return False
