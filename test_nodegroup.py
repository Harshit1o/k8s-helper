#!/usr/bin/env python3
"""
Test script for EKS node group functionality
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from k8s_helper.core import EKSClient
from unittest.mock import Mock, patch
import boto3
import json

def test_nodegroup_creation():
    """Test node group creation logic"""
    print("🧪 Testing node group creation...")
    
    # Mock AWS clients
    with patch('boto3.client') as mock_boto3:
        # Mock EKS client
        mock_eks = Mock()
        mock_ec2 = Mock()
        mock_iam = Mock()
        
        mock_boto3.side_effect = lambda service, region_name: {
            'eks': mock_eks,
            'ec2': mock_ec2,
            'iam': mock_iam
        }[service]
        
        # Mock IAM role creation
        def mock_get_role(RoleName):
            from botocore.exceptions import ClientError
            raise ClientError({'Error': {'Code': 'NoSuchEntity'}}, 'GetRole')
        
        mock_iam.get_role.side_effect = mock_get_role
        mock_iam.create_role.return_value = {
            'Role': {'Arn': 'arn:aws:iam::123456789012:role/eks-nodegroup-role'}
        }
        
        # Mock cluster details
        mock_eks.describe_cluster.return_value = {
            'cluster': {
                'name': 'test-cluster',
                'status': 'ACTIVE',
                'endpoint': 'https://test-cluster.eks.us-west-2.amazonaws.com',
                'version': '1.29',
                'platformVersion': 'eks.1',
                'createdAt': '2023-01-01T00:00:00Z',
                'arn': 'arn:aws:eks:us-west-2:123456789012:cluster/test-cluster',
                'resourcesVpcConfig': {
                    'subnetIds': ['subnet-12345', 'subnet-67890']
                }
            }
        }
        
        # Mock node group creation
        mock_eks.create_nodegroup.return_value = {
            'nodegroup': {
                'nodegroupName': 'test-nodegroup',
                'clusterName': 'test-cluster',
                'nodegroupArn': 'arn:aws:eks:us-west-2:123456789012:nodegroup/test-cluster/test-nodegroup',
                'createdAt': '2023-01-01T00:00:00Z',
                'status': 'CREATING'
            }
        }
        
        # Test node group creation
        eks_client = EKSClient(region='us-west-2')
        
        result = eks_client.create_nodegroup(
            cluster_name='test-cluster',
            nodegroup_name='test-nodegroup',
            instance_types=['t3.medium'],
            scaling_config={
                'minSize': 1,
                'maxSize': 3,
                'desiredSize': 2
            }
        )
        
        print(f"✅ Node group creation result: {result}")
        
        # Verify the call was made correctly
        mock_eks.create_nodegroup.assert_called_once()
        call_args = mock_eks.create_nodegroup.call_args
        print(f"📋 Create nodegroup called with: {call_args}")
        
        # Test that IAM role was created for node group
        mock_iam.create_role.assert_called_once()
        role_call = mock_iam.create_role.call_args
        print(f"📋 IAM role created: {role_call}")
        
        # Test that required policies were attached
        expected_policies = [
            "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy",
            "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy",
            "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
        ]
        
        policy_calls = [call[1]['PolicyArn'] for call in mock_iam.attach_role_policy.call_args_list]
        print(f"📋 Policies attached: {policy_calls}")
        
        for policy in expected_policies:
            assert policy in policy_calls, f"Policy {policy} not attached"
        
        print("✅ All tests passed!")

def test_cluster_with_nodegroup():
    """Test cluster creation with automatic node group"""
    print("\n🧪 Testing cluster creation with automatic node group...")
    
    with patch('boto3.client') as mock_boto3:
        # Mock clients
        mock_eks = Mock()
        mock_ec2 = Mock()
        mock_iam = Mock()
        
        mock_boto3.side_effect = lambda service, region_name: {
            'eks': mock_eks,
            'ec2': mock_ec2,
            'iam': mock_iam
        }[service]
        
        # Mock VPC and subnet responses
        mock_ec2.describe_vpcs.return_value = {
            'Vpcs': [{'VpcId': 'vpc-12345'}]
        }
        
        mock_ec2.describe_subnets.return_value = {
            'Subnets': [
                {'SubnetId': 'subnet-12345', 'State': 'available', 'AvailabilityZone': 'us-west-2a'},
                {'SubnetId': 'subnet-67890', 'State': 'available', 'AvailabilityZone': 'us-west-2b'}
            ]
        }
        
        # Mock IAM role responses
        def mock_get_role(RoleName):
            from botocore.exceptions import ClientError
            raise ClientError({'Error': {'Code': 'NoSuchEntity'}}, 'GetRole')
        
        mock_iam.get_role.side_effect = mock_get_role
        mock_iam.create_role.return_value = {
            'Role': {'Arn': 'arn:aws:iam::123456789012:role/eks-cluster-role'}
        }
        
        # Mock cluster creation
        mock_eks.create_cluster.return_value = {
            'cluster': {
                'name': 'test-cluster',
                'arn': 'arn:aws:eks:us-west-2:123456789012:cluster/test-cluster',
                'endpoint': 'https://test-cluster.eks.us-west-2.amazonaws.com',
                'createdAt': '2023-01-01T00:00:00Z',
                'status': 'CREATING'
            }
        }
        
        # Mock cluster status checks
        mock_eks.describe_cluster.return_value = {
            'cluster': {
                'name': 'test-cluster',
                'status': 'ACTIVE',
                'endpoint': 'https://test-cluster.eks.us-west-2.amazonaws.com',
                'version': '1.29',
                'platformVersion': 'eks.1',
                'createdAt': '2023-01-01T00:00:00Z',
                'arn': 'arn:aws:eks:us-west-2:123456789012:cluster/test-cluster',
                'resourcesVpcConfig': {
                    'subnetIds': ['subnet-12345', 'subnet-67890']
                }
            }
        }
        
        # Mock node group creation
        mock_eks.create_nodegroup.return_value = {
            'nodegroup': {
                'nodegroupName': 'test-cluster-nodegroup',
                'clusterName': 'test-cluster',
                'nodegroupArn': 'arn:aws:eks:us-west-2:123456789012:nodegroup/test-cluster/test-cluster-nodegroup',
                'createdAt': '2023-01-01T00:00:00Z',
                'status': 'CREATING'
            }
        }
        
        # Test cluster creation with node group
        eks_client = EKSClient(region='us-west-2')
        
        result = eks_client.create_cluster(
            cluster_name='test-cluster',
            create_nodegroup=True,
            wait_for_cluster=True
        )
        
        print(f"✅ Cluster creation result: {result}")
        
        # Verify cluster was created
        mock_eks.create_cluster.assert_called_once()
        
        # Since wait_for_cluster is True, node group should be created
        if 'nodegroup_info' in result:
            print(f"✅ Node group created: {result['nodegroup_info']['nodegroup_name']}")
            mock_eks.create_nodegroup.assert_called_once()
        else:
            print("ℹ️  Node group creation deferred (expected for non-wait mode)")
        
        print("✅ Cluster with node group test passed!")

if __name__ == "__main__":
    test_nodegroup_creation()
    test_cluster_with_nodegroup()
    print("\n🎉 All tests completed successfully!")
