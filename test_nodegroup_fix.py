#!/usr/bin/env python3
"""Test script to verify the node group creation fix"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from unittest.mock import Mock, patch
from k8s_helper.core import EKSClient

def test_nodegroup_without_ssh_key():
    """Test that nodegroup creation works without SSH key (no remoteAccess parameter)"""
    
    # Mock the EKS client
    mock_eks = Mock()
    mock_iam = Mock()
    mock_ec2 = Mock()
    
    # Mock the create_nodegroup response
    mock_eks.create_nodegroup.return_value = {
        'nodegroup': {
            'nodegroupName': 'test-nodegroup',
            'nodegroupArn': 'arn:aws:eks:us-west-2:123456789012:nodegroup/test-cluster/test-nodegroup/123',
            'createdAt': '2024-01-01T00:00:00Z',
            'status': 'CREATING',
            'instanceTypes': ['t3.medium'],
            'scalingConfig': {
                'minSize': 1,
                'maxSize': 3,
                'desiredSize': 2
            }
        }
    }
    
    # Mock the describe_cluster response
    mock_eks.describe_cluster.return_value = {
        'cluster': {
            'name': 'test-cluster',
            'arn': 'arn:aws:eks:us-west-2:123456789012:cluster/test-cluster',
            'version': '1.29',
            'status': 'ACTIVE',
            'endpoint': 'https://test.eks.amazonaws.com',
            'createdAt': '2024-01-01T00:00:00Z',
            'resourcesVpcConfig': {
                'subnetIds': ['subnet-12345', 'subnet-67890']
            }
        }
    }
    
    # Mock IAM role creation - simulate role doesn't exist first, then create it
    from botocore.exceptions import ClientError
    
    def mock_get_role(RoleName):
        if RoleName == 'eks-nodegroup-role':
            raise ClientError(
                error_response={'Error': {'Code': 'NoSuchEntity'}},
                operation_name='GetRole'
            )
    
    mock_iam.get_role.side_effect = mock_get_role
    mock_iam.create_role.return_value = {
        'Role': {
            'Arn': 'arn:aws:iam::123456789012:role/eks-nodegroup-role'
        }
    }
    mock_iam.attach_role_policy.return_value = {}
    
    # Create EKS client with mocked boto3 clients
    with patch('boto3.client') as mock_boto3:
        def mock_client(service, **kwargs):
            if service == 'eks':
                return mock_eks
            elif service == 'iam':
                return mock_iam
            elif service == 'ec2':
                return mock_ec2
            
        mock_boto3.side_effect = mock_client
        
        client = EKSClient(region='us-west-2')
        
        # Test nodegroup creation without SSH key
        result = client.create_nodegroup(
            cluster_name='test-cluster',
            nodegroup_name='test-nodegroup'
        )
        
        # Verify the call was made without remoteAccess parameter
        call_args = mock_eks.create_nodegroup.call_args
        
        # Check that remoteAccess is not in the call arguments
        assert 'remoteAccess' not in call_args[1], "remoteAccess should not be present when no SSH key is provided"
        
        # Verify other parameters are present
        assert call_args[1]['clusterName'] == 'test-cluster'
        assert call_args[1]['nodegroupName'] == 'test-nodegroup'
        assert call_args[1]['instanceTypes'] == ['t3.medium']
        assert call_args[1]['scalingConfig']['desiredSize'] == 2
        
        print("✅ Test passed: nodegroup creation without SSH key works correctly")
        print(f"📋 Call arguments: {list(call_args[1].keys())}")
        print(f"🔒 remoteAccess not included: {'remoteAccess' not in call_args[1]}")

def test_nodegroup_with_ssh_key():
    """Test that nodegroup creation works with SSH key (includes remoteAccess parameter)"""
    
    # Mock the EKS client
    mock_eks = Mock()
    mock_iam = Mock()
    mock_ec2 = Mock()
    
    # Mock the create_nodegroup response
    mock_eks.create_nodegroup.return_value = {
        'nodegroup': {
            'nodegroupName': 'test-nodegroup',
            'nodegroupArn': 'arn:aws:eks:us-west-2:123456789012:nodegroup/test-cluster/test-nodegroup/123',
            'createdAt': '2024-01-01T00:00:00Z',
            'status': 'CREATING',
            'instanceTypes': ['t3.medium'],
            'scalingConfig': {
                'minSize': 1,
                'maxSize': 3,
                'desiredSize': 2
            }
        }
    }
    
    # Mock the describe_cluster response
    mock_eks.describe_cluster.return_value = {
        'cluster': {
            'name': 'test-cluster',
            'arn': 'arn:aws:eks:us-west-2:123456789012:cluster/test-cluster',
            'version': '1.29',
            'status': 'ACTIVE',
            'endpoint': 'https://test.eks.amazonaws.com',
            'createdAt': '2024-01-01T00:00:00Z',
            'resourcesVpcConfig': {
                'subnetIds': ['subnet-12345', 'subnet-67890']
            }
        }
    }
    
    # Mock IAM role creation
    from botocore.exceptions import ClientError
    
    def mock_get_role(RoleName):
        if RoleName == 'eks-nodegroup-role':
            raise ClientError(
                error_response={'Error': {'Code': 'NoSuchEntity'}},
                operation_name='GetRole'
            )
    
    mock_iam.get_role.side_effect = mock_get_role
    mock_iam.create_role.return_value = {
        'Role': {
            'Arn': 'arn:aws:iam::123456789012:role/eks-nodegroup-role'
        }
    }
    mock_iam.attach_role_policy.return_value = {}
    
    # Create EKS client with mocked boto3 clients
    with patch('boto3.client') as mock_boto3:
        def mock_client(service, **kwargs):
            if service == 'eks':
                return mock_eks
            elif service == 'iam':
                return mock_iam
            elif service == 'ec2':
                return mock_ec2
            
        mock_boto3.side_effect = mock_client
        
        client = EKSClient(region='us-west-2')
        
        # Test nodegroup creation with SSH key
        result = client.create_nodegroup(
            cluster_name='test-cluster',
            nodegroup_name='test-nodegroup',
            ssh_key='my-ssh-key'
        )
        
        # Verify the call was made with remoteAccess parameter
        call_args = mock_eks.create_nodegroup.call_args
        
        # Check that remoteAccess is present with the correct SSH key
        assert 'remoteAccess' in call_args[1], "remoteAccess should be present when SSH key is provided"
        assert call_args[1]['remoteAccess']['ec2SshKey'] == 'my-ssh-key', "SSH key should be passed correctly"
        
        # Verify other parameters are present
        assert call_args[1]['clusterName'] == 'test-cluster'
        assert call_args[1]['nodegroupName'] == 'test-nodegroup'
        assert call_args[1]['instanceTypes'] == ['t3.medium']
        assert call_args[1]['scalingConfig']['desiredSize'] == 2
        
        print("✅ Test passed: nodegroup creation with SSH key works correctly")
        print(f"📋 Call arguments: {list(call_args[1].keys())}")
        print(f"🔑 remoteAccess included: {'remoteAccess' in call_args[1]}")
        print(f"🔐 SSH key: {call_args[1]['remoteAccess']['ec2SshKey']}")

if __name__ == "__main__":
    print("🧪 Testing node group creation fix...")
    print("=" * 60)
    
    try:
        test_nodegroup_without_ssh_key()
        print()
        test_nodegroup_with_ssh_key()
        print()
        print("🎉 All tests passed! The fix is working correctly.")
        print("✅ Node group creation no longer passes remoteAccess with null SSH key")
        print("✅ Node group creation includes remoteAccess when SSH key is provided")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
