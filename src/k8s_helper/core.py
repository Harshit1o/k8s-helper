from kubernetes import client, config
from kubernetes.client.rest import ApiException
from typing import Dict, List, Optional, Any
import yaml
import time
import base64
import boto3
import json
from botocore.exceptions import ClientError, NoCredentialsError


class EKSClient:
    """AWS EKS client for cluster management"""
    
    def __init__(self, region: str = "us-west-2"):
        """Initialize EKS client
        
        Args:
            region: AWS region for EKS operations
        """
        self.region = region
        try:
            self.eks_client = boto3.client('eks', region_name=region)
            self.ec2_client = boto3.client('ec2', region_name=region)
            self.iam_client = boto3.client('iam', region_name=region)
        except (NoCredentialsError, ClientError) as e:
            raise Exception(f"AWS credentials not found or invalid: {e}")
    
    def create_cluster(self, cluster_name: str, version: str = "1.29", 
                      subnets: List[str] = None, security_groups: List[str] = None,
                      role_arn: str = None, node_group_name: str = None,
                      instance_types: List[str] = None, ami_type: str = "AL2_x86_64",
                      capacity_type: str = "ON_DEMAND", scaling_config: Dict = None) -> Dict:
        """Create an EKS cluster
        
        Args:
            cluster_name: Name of the EKS cluster
            version: Kubernetes version
            subnets: List of subnet IDs
            security_groups: List of security group IDs
            role_arn: IAM role ARN for the cluster
            node_group_name: Name for the node group
            instance_types: List of EC2 instance types
            ami_type: AMI type for nodes
            capacity_type: Capacity type (ON_DEMAND or SPOT)
            scaling_config: Scaling configuration for node group
            
        Returns:
            Dict containing cluster information
        """
        try:
            # Use default values if not provided
            if subnets is None:
                subnets = self._get_default_subnets()
            
            if role_arn is None:
                role_arn = self._create_or_get_cluster_role()
            
            if instance_types is None:
                instance_types = ["t3.medium"]
            
            if scaling_config is None:
                scaling_config = {
                    "minSize": 1,
                    "maxSize": 3,
                    "desiredSize": 2
                }
            
            # Create cluster
            cluster_response = self.eks_client.create_cluster(
                name=cluster_name,
                version=version,
                roleArn=role_arn,
                resourcesVpcConfig={
                    'subnetIds': subnets,
                    'securityGroupIds': security_groups or [],
                    'endpointConfigPublic': True,
                    'endpointConfigPrivate': True
                },
                logging={
                    'enable': True,
                    'types': ['api', 'audit', 'authenticator', 'controllerManager', 'scheduler']
                }
            )
            
            cluster_info = {
                'cluster_name': cluster_name,
                'status': 'CREATING',
                'cluster_arn': cluster_response['cluster']['arn'],
                'endpoint': cluster_response['cluster'].get('endpoint', 'Not available yet'),
                'version': version,
                'role_arn': role_arn,
                'subnets': subnets,
                'created_at': cluster_response['cluster']['createdAt']
            }
            
            # If node group name is provided, we'll create it after cluster is active
            if node_group_name:
                cluster_info['node_group_name'] = node_group_name
                cluster_info['instance_types'] = instance_types
                cluster_info['scaling_config'] = scaling_config
            
            return cluster_info
            
        except ClientError as e:
            raise Exception(f"Failed to create EKS cluster: {e}")
    
    def _get_default_subnets(self) -> List[str]:
        """Get default subnets for EKS cluster"""
        try:
            response = self.ec2_client.describe_subnets()
            subnets = []
            for subnet in response['Subnets']:
                if subnet['State'] == 'available':
                    subnets.append(subnet['SubnetId'])
            
            if len(subnets) < 2:
                raise Exception("Need at least 2 subnets for EKS cluster")
            
            return subnets[:2]  # Return first 2 available subnets
            
        except ClientError as e:
            raise Exception(f"Failed to get default subnets: {e}")
    
    def _create_or_get_cluster_role(self) -> str:
        """Create or get IAM role for EKS cluster"""
        role_name = "eks-cluster-role"
        
        try:
            # Check if role exists
            response = self.iam_client.get_role(RoleName=role_name)
            return response['Role']['Arn']
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchEntity':
                # Create the role
                trust_policy = {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Principal": {
                                "Service": "eks.amazonaws.com"
                            },
                            "Action": "sts:AssumeRole"
                        }
                    ]
                }
                
                response = self.iam_client.create_role(
                    RoleName=role_name,
                    AssumeRolePolicyDocument=json.dumps(trust_policy),
                    Description="EKS cluster role created by k8s-helper"
                )
                
                # Attach required policies
                policies = [
                    "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
                ]
                
                for policy in policies:
                    self.iam_client.attach_role_policy(
                        RoleName=role_name,
                        PolicyArn=policy
                    )
                
                return response['Role']['Arn']
            else:
                raise Exception(f"Failed to create or get cluster role: {e}")
    
    def get_cluster_status(self, cluster_name: str) -> Dict:
        """Get EKS cluster status"""
        try:
            response = self.eks_client.describe_cluster(name=cluster_name)
            cluster = response['cluster']
            
            return {
                'name': cluster['name'],
                'status': cluster['status'],
                'endpoint': cluster.get('endpoint', 'Not available'),
                'version': cluster['version'],
                'platform_version': cluster['platformVersion'],
                'created_at': cluster['createdAt'],
                'arn': cluster['arn']
            }
            
        except ClientError as e:
            raise Exception(f"Failed to get cluster status: {e}")
    
    def wait_for_cluster_active(self, cluster_name: str, timeout: int = 1800) -> bool:
        """Wait for EKS cluster to become active"""
        import time
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                status = self.get_cluster_status(cluster_name)
                if status['status'] == 'ACTIVE':
                    return True
                elif status['status'] == 'FAILED':
                    raise Exception(f"Cluster creation failed")
                
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                raise Exception(f"Error waiting for cluster: {e}")
        
        return False

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
                         labels: Optional[Dict[str, str]] = None, 
                         init_containers: Optional[List[Dict]] = None,
                         volume_mounts: Optional[List[Dict]] = None,
                         volumes: Optional[List[Dict]] = None) -> Optional[Any]:
        """Create a Kubernetes deployment
        
        Args:
            name: Deployment name
            image: Container image
            replicas: Number of replicas
            container_port: Container port
            env_vars: Environment variables
            labels: Labels for the deployment
            init_containers: List of init container specifications
            volume_mounts: List of volume mounts for the main container
            volumes: List of volumes for the pod
            
        Returns:
            Deployment object if successful, None otherwise
        """
        if labels is None:
            labels = {"app": name}
        
        # Environment variables
        env = []
        if env_vars:
            env = [client.V1EnvVar(name=k, value=v) for k, v in env_vars.items()]
        
        # Volume mounts for main container
        volume_mounts_obj = []
        if volume_mounts:
            for vm in volume_mounts:
                volume_mounts_obj.append(client.V1VolumeMount(
                    name=vm.get('name'),
                    mount_path=vm.get('mount_path'),
                    read_only=vm.get('read_only', False)
                ))
        
        # Main container
        container = client.V1Container(
            name=name,
            image=image,
            ports=[client.V1ContainerPort(container_port=container_port)],
            env=env if env else None,
            volume_mounts=volume_mounts_obj if volume_mounts_obj else None
        )

        # Init containers
        init_containers_obj = []
        if init_containers:
            for init_container in init_containers:
                init_env = []
                if init_container.get('env_vars'):
                    init_env = [client.V1EnvVar(name=k, value=v) 
                              for k, v in init_container['env_vars'].items()]
                
                init_volume_mounts = []
                if init_container.get('volume_mounts'):
                    for vm in init_container['volume_mounts']:
                        init_volume_mounts.append(client.V1VolumeMount(
                            name=vm.get('name'),
                            mount_path=vm.get('mount_path'),
                            read_only=vm.get('read_only', False)
                        ))
                
                init_containers_obj.append(client.V1Container(
                    name=init_container['name'],
                    image=init_container['image'],
                    command=init_container.get('command'),
                    args=init_container.get('args'),
                    env=init_env if init_env else None,
                    volume_mounts=init_volume_mounts if init_volume_mounts else None
                ))
        
        # Volumes
        volumes_obj = []
        if volumes:
            for volume in volumes:
                if volume.get('type') == 'pvc':
                    volumes_obj.append(client.V1Volume(
                        name=volume['name'],
                        persistent_volume_claim=client.V1PersistentVolumeClaimVolumeSource(
                            claim_name=volume['claim_name']
                        )
                    ))
                elif volume.get('type') == 'secret':
                    volumes_obj.append(client.V1Volume(
                        name=volume['name'],
                        secret=client.V1SecretVolumeSource(
                            secret_name=volume['secret_name']
                        )
                    ))
                elif volume.get('type') == 'configmap':
                    volumes_obj.append(client.V1Volume(
                        name=volume['name'],
                        config_map=client.V1ConfigMapVolumeSource(
                            name=volume['config_map_name']
                        )
                    ))
                elif volume.get('type') == 'empty_dir':
                    volumes_obj.append(client.V1Volume(
                        name=volume['name'],
                        empty_dir=client.V1EmptyDirVolumeSource()
                    ))

        template = client.V1PodTemplateSpec(
            metadata=client.V1ObjectMeta(labels=labels),
            spec=client.V1PodSpec(
                containers=[container],
                init_containers=init_containers_obj if init_containers_obj else None,
                volumes=volumes_obj if volumes_obj else None
            )
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
    # SECRET OPERATIONS
    # ======================
    def create_secret(self, name: str, data: Dict[str, str], 
                     secret_type: str = "Opaque", namespace: str = None) -> Optional[Any]:
        """Create a Kubernetes secret
        
        Args:
            name: Name of the secret
            data: Dictionary of key-value pairs for the secret
            secret_type: Type of secret (Opaque, kubernetes.io/tls, etc.)
            namespace: Namespace (uses default if not provided)
            
        Returns:
            Secret object if successful, None otherwise
        """
        try:
            ns = namespace or self.namespace
            
            # Encode data as base64
            encoded_data = {}
            for key, value in data.items():
                encoded_data[key] = base64.b64encode(value.encode()).decode()
            
            secret = client.V1Secret(
                metadata=client.V1ObjectMeta(name=name, namespace=ns),
                type=secret_type,
                data=encoded_data
            )
            
            result = self.core_v1.create_namespaced_secret(
                namespace=ns,
                body=secret
            )
            
            return result
            
        except ApiException as e:
            print(f"❌ Error creating secret: {e}")
            return None
    
    def get_secret(self, name: str, namespace: str = None) -> Optional[Dict]:
        """Get a Kubernetes secret
        
        Args:
            name: Name of the secret
            namespace: Namespace (uses default if not provided)
            
        Returns:
            Dictionary containing secret data
        """
        try:
            ns = namespace or self.namespace
            result = self.core_v1.read_namespaced_secret(name=name, namespace=ns)
            
            # Decode base64 data
            decoded_data = {}
            if result.data:
                for key, value in result.data.items():
                    decoded_data[key] = base64.b64decode(value).decode()
            
            return {
                'name': result.metadata.name,
                'namespace': result.metadata.namespace,
                'type': result.type,
                'data': decoded_data,
                'created_at': result.metadata.creation_timestamp
            }
            
        except ApiException as e:
            print(f"❌ Error getting secret: {e}")
            return None
    
    def delete_secret(self, name: str, namespace: str = None) -> bool:
        """Delete a Kubernetes secret"""
        try:
            ns = namespace or self.namespace
            self.core_v1.delete_namespaced_secret(name=name, namespace=ns)
            return True
        except ApiException as e:
            print(f"❌ Error deleting secret: {e}")
            return False
    
    def list_secrets(self, namespace: str = None) -> List[Dict]:
        """List all secrets in a namespace"""
        try:
            ns = namespace or self.namespace
            result = self.core_v1.list_namespaced_secret(namespace=ns)
            
            secrets = []
            for secret in result.items:
                secrets.append({
                    'name': secret.metadata.name,
                    'namespace': secret.metadata.namespace,
                    'type': secret.type,
                    'data_keys': list(secret.data.keys()) if secret.data else [],
                    'created_at': secret.metadata.creation_timestamp
                })
            
            return secrets
            
        except ApiException as e:
            print(f"❌ Error listing secrets: {e}")
            return []

    # ======================
    # PVC OPERATIONS
    # ======================
    def create_pvc(self, name: str, size: str, access_modes: List[str] = None,
                   storage_class: str = None, namespace: str = None) -> Optional[Any]:
        """Create a Persistent Volume Claim
        
        Args:
            name: Name of the PVC
            size: Size of the volume (e.g., '10Gi', '100Mi')
            access_modes: List of access modes (default: ['ReadWriteOnce'])
            storage_class: Storage class name
            namespace: Namespace (uses default if not provided)
            
        Returns:
            PVC object if successful, None otherwise
        """
        try:
            ns = namespace or self.namespace
            
            if access_modes is None:
                access_modes = ['ReadWriteOnce']
            
            # Create PVC specification
            pvc_spec = client.V1PersistentVolumeClaimSpec(
                access_modes=access_modes,
                resources=client.V1ResourceRequirements(
                    requests={'storage': size}
                )
            )
            
            if storage_class:
                pvc_spec.storage_class_name = storage_class
            
            pvc = client.V1PersistentVolumeClaim(
                metadata=client.V1ObjectMeta(name=name, namespace=ns),
                spec=pvc_spec
            )
            
            result = self.core_v1.create_namespaced_persistent_volume_claim(
                namespace=ns,
                body=pvc
            )
            
            return result
            
        except ApiException as e:
            print(f"❌ Error creating PVC: {e}")
            return None
    
    def get_pvc(self, name: str, namespace: str = None) -> Optional[Dict]:
        """Get a Persistent Volume Claim"""
        try:
            ns = namespace or self.namespace
            result = self.core_v1.read_namespaced_persistent_volume_claim(name=name, namespace=ns)
            
            return {
                'name': result.metadata.name,
                'namespace': result.metadata.namespace,
                'status': result.status.phase,
                'volume_name': result.spec.volume_name,
                'access_modes': result.spec.access_modes,
                'storage_class': result.spec.storage_class_name,
                'size': result.spec.resources.requests.get('storage', 'Unknown'),
                'created_at': result.metadata.creation_timestamp
            }
            
        except ApiException as e:
            print(f"❌ Error getting PVC: {e}")
            return None
    
    def delete_pvc(self, name: str, namespace: str = None) -> bool:
        """Delete a Persistent Volume Claim"""
        try:
            ns = namespace or self.namespace
            self.core_v1.delete_namespaced_persistent_volume_claim(name=name, namespace=ns)
            return True
        except ApiException as e:
            print(f"❌ Error deleting PVC: {e}")
            return False
    
    def list_pvcs(self, namespace: str = None) -> List[Dict]:
        """List all PVCs in a namespace"""
        try:
            ns = namespace or self.namespace
            result = self.core_v1.list_namespaced_persistent_volume_claim(namespace=ns)
            
            pvcs = []
            for pvc in result.items:
                pvcs.append({
                    'name': pvc.metadata.name,
                    'namespace': pvc.metadata.namespace,
                    'status': pvc.status.phase,
                    'volume_name': pvc.spec.volume_name,
                    'access_modes': pvc.spec.access_modes,
                    'storage_class': pvc.spec.storage_class_name,
                    'size': pvc.spec.resources.requests.get('storage', 'Unknown'),
                    'created_at': pvc.metadata.creation_timestamp
                })
            
            return pvcs
            
        except ApiException as e:
            print(f"❌ Error listing PVCs: {e}")
            return []

    # ======================
    # SERVICE URL OPERATIONS
    # ======================
    def get_service_url(self, name: str, namespace: str = None) -> Optional[Dict]:
        """Get service URL, including AWS ELB URLs for LoadBalancer services
        
        Args:
            name: Name of the service
            namespace: Namespace (uses default if not provided)
            
        Returns:
            Dictionary containing service URL information
        """
        try:
            ns = namespace or self.namespace
            service = self.core_v1.read_namespaced_service(name=name, namespace=ns)
            
            service_type = service.spec.type
            ports = []
            for port in service.spec.ports:
                ports.append({
                    'port': port.port,
                    'target_port': port.target_port,
                    'protocol': port.protocol,
                    'name': port.name
                })
            
            result = {
                'name': name,
                'namespace': ns,
                'type': service_type,
                'ports': ports,
                'cluster_ip': service.spec.cluster_ip
            }
            
            if service_type == 'LoadBalancer':
                # Check for AWS ELB
                ingress = service.status.load_balancer.ingress
                if ingress:
                    for ing in ingress:
                        if ing.hostname:  # AWS ELB uses hostname
                            result['external_url'] = f"http://{ing.hostname}"
                            result['external_hostname'] = ing.hostname
                            
                            # Check if it's an AWS ELB
                            if 'elb.amazonaws.com' in ing.hostname:
                                result['aws_elb'] = True
                                result['elb_dns_name'] = ing.hostname
                        elif ing.ip:  # Some cloud providers use IP
                            result['external_url'] = f"http://{ing.ip}"
                            result['external_ip'] = ing.ip
                
                # If no ingress yet, service might still be provisioning
                if not ingress:
                    result['status'] = 'Provisioning LoadBalancer...'
            
            elif service_type == 'NodePort':
                # For NodePort, we need to get node IPs
                nodes = self.core_v1.list_node()
                if nodes.items:
                    node_ip = None
                    for node in nodes.items:
                        for address in node.status.addresses:
                            if address.type == 'ExternalIP':
                                node_ip = address.address
                                break
                        if node_ip:
                            break
                    
                    if node_ip:
                        for port in service.spec.ports:
                            if port.node_port:
                                result['external_url'] = f"http://{node_ip}:{port.node_port}"
                                result['node_ip'] = node_ip
                                result['node_port'] = port.node_port
            
            return result
            
        except ApiException as e:
            print(f"❌ Error getting service URL: {e}")
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
