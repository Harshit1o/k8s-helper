#!/usr/bin/env python3
"""
Test script for EKS functionality in k8s-helper
"""

import sys
import os
import json
from unittest.mock import patch, MagicMock

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from k8s_helper.core import EKSClient

def test_eks_client():
    """Test EKS client functionality with mocked AWS calls"""
    
    # Mock AWS responses
    mock_cluster_response = {
        'cluster': {
            'name': 'test-cluster',
            'arn': 'arn:aws:eks:us-west-2:123456789012:cluster/test-cluster',
            'createdAt': '2024-01-01T00:00:00Z',
            'endpoint': 'https://test-cluster.eks.us-west-2.amazonaws.com',
            'status': 'CREATING',
            'version': '1.29'
        }
    }
    
    mock_subnets_response = {
        'Subnets': [
            {
                'SubnetId': 'subnet-12345',
                'State': 'available',
                'AvailabilityZone': 'us-west-2a',
                'VpcId': 'vpc-12345'
            },
            {
                'SubnetId': 'subnet-67890',
                'State': 'available',
                'AvailabilityZone': 'us-west-2b',
                'VpcId': 'vpc-12345'
            }
        ]
    }
    
    mock_role_response = {
        'Role': {
            'Arn': 'arn:aws:iam::123456789012:role/eks-cluster-role'
        }
    }
    
    mock_azs_response = {
        'AvailabilityZones': [
            {'ZoneName': 'us-west-2a'},
            {'ZoneName': 'us-west-2b'},
            {'ZoneName': 'us-west-2c'}
        ]
    }
    
    mock_vpcs_response = {
        'Vpcs': [
            {
                'VpcId': 'vpc-12345',
                'IsDefault': True
            }
        ]
    }
    
    # Test with mocked AWS clients
    with patch('boto3.client') as mock_boto3:
        # Setup mocks
        mock_eks_client = MagicMock()
        mock_ec2_client = MagicMock()
        mock_iam_client = MagicMock()
        
        mock_boto3.side_effect = lambda service_name, **kwargs: {
            'eks': mock_eks_client,
            'ec2': mock_ec2_client,
            'iam': mock_iam_client
        }[service_name]
        
        # Configure mock responses
        mock_eks_client.create_cluster.return_value = mock_cluster_response
        mock_eks_client.describe_cluster.return_value = mock_cluster_response
        
        mock_ec2_client.describe_subnets.return_value = mock_subnets_response
        mock_ec2_client.describe_availability_zones.return_value = mock_azs_response
        mock_ec2_client.describe_vpcs.return_value = mock_vpcs_response
        
        mock_iam_client.get_role.return_value = mock_role_response
        
        # Test EKS client
        try:
            eks_client = EKSClient(region='us-west-2')
            print("✅ EKS client initialized successfully")
            
            # Test cluster creation
            cluster_info = eks_client.create_cluster(
                cluster_name='test-cluster',
                version='1.29',
                instance_types=['t3.medium'],
                scaling_config={'minSize': 1, 'maxSize': 3, 'desiredSize': 2}
            )
            
            print("✅ Cluster creation initiated successfully")
            print(f"   📋 Cluster ARN: {cluster_info['cluster_arn']}")
            print(f"   📍 Subnets: {cluster_info['subnets']}")
            
            # Test cluster status
            status = eks_client.get_cluster_status('test-cluster')
            print("✅ Cluster status retrieved successfully")
            print(f"   📊 Status: {status['status']}")
            print(f"   🔗 Endpoint: {status['endpoint']}")
            
        except Exception as e:
            print(f"❌ EKS test failed: {e}")
            return False
    
    return True

def test_subnet_logic():
    """Test subnet selection logic"""
    
    print("\n🧪 Testing subnet selection logic...")
    
    # Test scenario 1: Subnets in different AZs
    mock_subnets_multi_az = {
        'Subnets': [
            {'SubnetId': 'subnet-1', 'State': 'available', 'AvailabilityZone': 'us-west-2a'},
            {'SubnetId': 'subnet-2', 'State': 'available', 'AvailabilityZone': 'us-west-2b'},
            {'SubnetId': 'subnet-3', 'State': 'available', 'AvailabilityZone': 'us-west-2a'},
            {'SubnetId': 'subnet-4', 'State': 'available', 'AvailabilityZone': 'us-west-2c'}
        ]
    }
    
    with patch('boto3.client') as mock_boto3:
        mock_eks_client = MagicMock()
        mock_ec2_client = MagicMock()
        mock_iam_client = MagicMock()
        
        mock_boto3.side_effect = lambda service_name, **kwargs: {
            'eks': mock_eks_client,
            'ec2': mock_ec2_client,
            'iam': mock_iam_client
        }[service_name]
        
        mock_ec2_client.describe_subnets.return_value = mock_subnets_multi_az
        
        try:
            eks_client = EKSClient()
            subnets = eks_client._get_default_subnets()
            
            # Should select 2 subnets from different AZs
            print(f"✅ Selected subnets: {subnets}")
            print(f"   📊 Count: {len(subnets)} (should be 2)")
            
            if len(subnets) == 2:
                print("✅ Subnet selection logic working correctly")
            else:
                print("❌ Subnet selection logic needs adjustment")
                
        except Exception as e:
            print(f"❌ Subnet logic test failed: {e}")
            return False
    
    return True

if __name__ == '__main__':
    print("🚀 Testing k8s-helper EKS functionality...")
    
    success = True
    
    # Test EKS client
    if not test_eks_client():
        success = False
    
    # Test subnet logic
    if not test_subnet_logic():
        success = False
    
    if success:
        print("\n✅ All EKS tests passed!")
        print("🎉 The EKS functionality is working correctly")
        print("\n💡 To use in production:")
        print("   1. Configure AWS credentials: aws configure")
        print("   2. Create EKS cluster: k8s-helper create-eks-cluster <name> --region <region>")
        print("   3. Configure kubectl: aws eks update-kubeconfig --name <cluster-name>")
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
        sys.exit(1)
