#!/usr/bin/env python3
"""
Test script to verify the overlapping rich status display fix.
This simulates the CLI commands that were causing the issue.
"""

import sys
import os
import time
import unittest
from unittest.mock import patch, MagicMock

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from k8s_helper.cli import app
from typer.testing import CliRunner

class TestDisplayFix(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()
        
    @patch('k8s_helper.core.EKSClient')
    def test_create_nodegroup_no_overlap(self, mock_eks_client):
        """Test that create-nodegroup doesn't have overlapping status displays"""
        # Mock the EKS client
        mock_client = MagicMock()
        mock_eks_client.return_value = mock_client
        
        # Mock cluster status check
        mock_client.get_cluster_status.return_value = {'status': 'ACTIVE'}
        
        # Mock nodegroup creation
        mock_client.create_nodegroup.return_value = {
            'nodegroup_arn': 'arn:aws:eks:us-west-2:123456789012:nodegroup/test-cluster/test-nodegroup',
            'created_at': '2024-01-01T00:00:00Z',
            'instance_types': ['t3.medium'],
            'scaling_config': {'minSize': 1, 'maxSize': 3, 'desiredSize': 2}
        }
        
        # Mock wait function
        mock_client.wait_for_nodegroup_active.return_value = True
        
        # Run the command
        result = self.runner.invoke(app, [
            'create-nodegroup', 
            'test-cluster', 
            'test-nodegroup',
            '--region', 'us-west-2',
            '--wait'
        ])
        
        # Check that command completed successfully
        self.assertEqual(result.exit_code, 0)
        
        # Check that expected messages are in output
        self.assertIn('Creating node group: test-nodegroup', result.stdout)
        self.assertIn('Node group creation initiated', result.stdout)
        
        # Verify that the EKS client methods were called
        mock_client.get_cluster_status.assert_called_once_with('test-cluster')
        mock_client.create_nodegroup.assert_called_once()
        mock_client.wait_for_nodegroup_active.assert_called_once_with('test-cluster', 'test-nodegroup')

    @patch('k8s_helper.core.EKSClient')
    def test_create_nodegroup_with_ssh_key(self, mock_eks_client):
        """Test create-nodegroup with SSH key parameter"""
        # Mock the EKS client
        mock_client = MagicMock()
        mock_eks_client.return_value = mock_client
        
        # Mock cluster status check
        mock_client.get_cluster_status.return_value = {'status': 'ACTIVE'}
        
        # Mock nodegroup creation
        mock_client.create_nodegroup.return_value = {
            'nodegroup_arn': 'arn:aws:eks:us-west-2:123456789012:nodegroup/test-cluster/test-nodegroup',
            'created_at': '2024-01-01T00:00:00Z',
            'instance_types': ['t3.medium'],
            'scaling_config': {'minSize': 1, 'maxSize': 3, 'desiredSize': 2}
        }
        
        # Mock wait function
        mock_client.wait_for_nodegroup_active.return_value = True
        
        # Run the command with SSH key
        result = self.runner.invoke(app, [
            'create-nodegroup', 
            'test-cluster', 
            'test-nodegroup',
            '--region', 'us-west-2',
            '--ssh-key', 'my-ssh-key',
            '--no-wait'
        ])
        
        # Check that command completed successfully
        self.assertEqual(result.exit_code, 0)
        
        # Check that expected messages are in output
        self.assertIn('Creating node group: test-nodegroup', result.stdout)
        self.assertIn('Node group creation initiated', result.stdout)
        
        # Verify that create_nodegroup was called with ssh_key
        mock_client.create_nodegroup.assert_called_once()
        call_args = mock_client.create_nodegroup.call_args
        self.assertEqual(call_args[1]['ssh_key'], 'my-ssh-key')

if __name__ == '__main__':
    print("Testing the overlapping status display fix...")
    unittest.main(verbosity=2)
