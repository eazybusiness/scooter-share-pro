#!/usr/bin/env python3
"""
Scooter Share Pro Diagram Generator
Creates professional diagrams for documentation
"""

import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime
import os

# Configure matplotlib for professional look
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10

class ScooterShareProDiagramGenerator:
    def __init__(self, output_dir="../diagrams"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Scooter Share Pro Colors
        self.colors = {
            'primary': '#2c3e50',
            'secondary': '#3498db',
            'accent': '#34495e',
            'success': '#27ae60',
            'warning': '#f39c12',
            'error': '#e74c3c',
            'light': '#ecf0f1',
            'dark': '#2c3e50'
        }
    
    def create_architecture_diagram(self):
        """Create enterprise system architecture diagram"""
        fig, ax = plt.subplots(1, 1, figsize=(14, 10))
        ax.set_title('Scooter Share Pro - Enterprise Architecture', fontsize=16, fontweight='bold', color=self.colors['primary'])
        
        # Define enterprise components
        components = {
            'Mobile App': {'pos': (1, 9), 'size': (2, 1), 'color': self.colors['primary']},
            'Web Frontend': {'pos': (4, 9), 'size': (2, 1), 'color': self.colors['secondary']},
            'Admin Dashboard': {'pos': (7, 9), 'size': (2, 1), 'color': self.colors['accent']},
            'API Gateway': {'pos': (4, 7), 'size': (2, 1), 'color': self.colors['warning']},
            'Auth Service': {'pos': (1, 5), 'size': (2, 1), 'color': self.colors['success']},
            'User Service': {'pos': (4, 5), 'size': (2, 1), 'color': self.colors['dark']},
            'Scooter Service': {'pos': (7, 5), 'size': (2, 1), 'color': self.colors['error']},
            'Rental Service': {'pos': (1, 3), 'size': (2, 1), 'color': self.colors['secondary']},
            'Payment Service': {'pos': (4, 3), 'size': (2, 1), 'color': self.colors['warning']},
            'Notification Service': {'pos': (7, 3), 'size': (2, 1), 'color': self.colors['accent']},
            'PostgreSQL': {'pos': (2, 1), 'size': (2, 1), 'color': self.colors['success']},
            'Redis Cache': {'pos': (6, 1), 'size': (2, 1), 'color': self.colors['dark']},
        }
        
        # Draw components
        for name, comp in components.items():
            rect = plt.Rectangle(comp['pos'], comp['size'][0], comp['size'][1], 
                                facecolor=comp['color'], edgecolor='black', linewidth=2, alpha=0.8)
            ax.add_patch(rect)
            ax.text(comp['pos'][0] + comp['size'][0]/2, comp['pos'][1] + comp['size'][1]/2, 
                    name, ha='center', va='center', fontweight='bold', color='white', fontsize=9)
        
        # Draw arrows
        arrows = [
            ((2, 8.5), (4, 8)),    # Mobile to API
            ((5, 8.5), (5, 8)),    # Web to API
            ((8, 8.5), (5, 8)),    # Admin to API
            ((4, 6), (2, 6)),      # API to Auth
            ((5, 6), (5, 6)),      # API to User
            ((6, 6), (8, 6)),      # API to Scooter
            ((3, 4), (2, 4)),      # Auth to Rental
            ((5, 4), (5, 4)),      # User to Payment
            ((7, 4), (7, 4)),      # Scooter to Notification
            ((2, 2), (3, 2)),      # Services to PostgreSQL
            ((6, 2), (7, 2)),      # Services to Redis
        ]
        
        for start, end in arrows:
            ax.annotate('', xy=end, xytext=start,
                       arrowprops=dict(arrowstyle='->', lw=2, color=self.colors['dark']))
        
        # Add layers
        layer_labels = [
            ('Presentation Layer', 0.5, 9.5, self.colors['primary']),
            ('API Gateway Layer', 0.5, 7.5, self.colors['warning']),
            ('Service Layer', 0.5, 5.5, self.colors['dark']),
            ('Business Layer', 0.5, 3.5, self.colors['secondary']),
            ('Data Layer', 0.5, 1.5, self.colors['success']),
        ]
        
        for label, x, y, color in layer_labels:
            ax.text(x, y, label, rotation=90, va='center', fontweight='bold', 
                   color=color, fontsize=11)
        
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 11)
        ax.axis('off')
        
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/scooter_share_pro_architecture.png", dpi=300, bbox_inches='tight')
        plt.close()
        print("✅ Enterprise architecture diagram created")
    
    def create_database_schema(self):
        """Create enterprise database ER diagram"""
        fig, ax = plt.subplots(1, 1, figsize=(16, 12))
        ax.set_title('Scooter Share Pro - Database Schema', fontsize=16, fontweight='bold', color=self.colors['primary'])
        
        # Define enterprise tables
        tables = {
            'users': {
                'pos': (2, 10), 'size': (3, 2.5),
                'fields': ['id (PK)', 'email (UNIQUE)', 'password_hash', 'first_name', 'last_name', 'role', 'phone', 'is_active', 'created_at', 'updated_at']
            },
            'scooters': {
                'pos': (7, 10), 'size': (3, 3),
                'fields': ['id (PK)', 'identifier (UNIQUE)', 'model', 'brand', 'status', 'battery_level', 'max_speed', 'range_km', 'qr_code', 'latitude', 'longitude', 'provider_id (FK)', 'created_at']
            },
            'rentals': {
                'pos': (12, 10), 'size': (3, 2.5),
                'fields': ['id (PK)', 'rental_code (UNIQUE)', 'user_id (FK)', 'scooter_id (FK)', 'start_time', 'end_time', 'duration_minutes', 'start_lat', 'start_lng', 'end_lat', 'end_lng', 'total_cost', 'status']
            },
            'payments': {
                'pos': (2, 6), 'size': (3, 2),
                'fields': ['id (PK)', 'transaction_id (UNIQUE)', 'rental_id (FK)', 'user_id (FK)', 'amount', 'currency', 'payment_method', 'status', 'created_at']
            },
            'maintenance': {
                'pos': (7, 6), 'size': (3, 2),
                'fields': ['id (PK)', 'scooter_id (FK)', 'type', 'description', 'cost', 'status', 'scheduled_date', 'completed_date']
            },
            'notifications': {
                'pos': (12, 6), 'size': (3, 2),
                'fields': ['id (PK)', 'user_id (FK)', 'type', 'message', 'status', 'sent_at', 'read_at']
            }
        }
        
        # Draw tables
        for name, table in tables.items():
            # Table box
            rect = plt.Rectangle(table['pos'], table['size'][0], table['size'][1], 
                                facecolor=self.colors['light'], edgecolor=self.colors['primary'], linewidth=2)
            ax.add_patch(rect)
            
            # Table name
            ax.text(table['pos'][0] + table['size'][0]/2, table['pos'][1] + table['size'][1] - 0.2, 
                   name.upper(), ha='center', va='top', fontweight='bold', color=self.colors['primary'])
            
            # Fields
            for i, field in enumerate(table['fields']):
                y_pos = table['pos'][1] + table['size'][1] - 0.5 - (i * 0.2)
                ax.text(table['pos'][0] + 0.1, y_pos, field, ha='left', va='center', fontsize=7)
        
        # Draw relationships
        relationships = [
            ((3.5, 10), (3.5, 8)),    # users to payments
            ((8.5, 10), (13.5, 12.5)), # scooters to rentals
            ((3.5, 10), (13.5, 12.5)), # users to rentals
            ((3.5, 6), (13.5, 8)),    # payments to rentals
            ((8.5, 6), (8.5, 10)),    # maintenance to scooters
            ((3.5, 6), (13.5, 8)),    # notifications to users
        ]
        
        for start, end in relationships:
            ax.annotate('', xy=end, xytext=start,
                       arrowprops=dict(arrowstyle='->', lw=2, color=self.colors['dark']))
        
        ax.set_xlim(0, 16)
        ax.set_ylim(0, 13)
        ax.axis('off')
        
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/scooter_share_pro_database_schema.png", dpi=300, bbox_inches='tight')
        plt.close()
        print("✅ Enterprise database schema diagram created")
    
    def create_scalability_diagram(self):
        """Create scalability and performance diagram"""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Concurrent Users vs Response Time', 'Database Performance', 'API Load Distribution', 'System Scalability'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Generate realistic data
        users = [100, 250, 500, 750, 1000, 1500, 2000]
        response_time = [45, 52, 68, 89, 120, 195, 280]
        throughput = [1200, 2800, 5200, 7100, 8900, 10500, 11200]
        
        # Response Time Chart
        fig.add_trace(
            go.Scatter(x=users, y=response_time, name='Response Time (ms)', 
                      line=dict(color=self.colors['primary'], width=3),
                      mode='lines+markers'),
            row=1, col=1
        )
        
        # Database Performance
        queries = [1000, 2500, 5000, 7500, 10000, 15000, 20000]
        query_time = [12, 18, 35, 58, 95, 165, 240]
        
        fig.add_trace(
            go.Scatter(x=queries, y=query_time, name='Query Time (ms)', 
                      line=dict(color=self.colors['warning'], width=3),
                      mode='lines+markers'),
            row=1, col=2
        )
        
        # API Load Distribution
        endpoints = ['Auth', 'Users', 'Scooters', 'Rentals', 'Payments']
        requests = [15, 25, 35, 20, 5]
        
        fig.add_trace(
            go.Bar(x=endpoints, y=requests, name='Request %', 
                  marker_color=self.colors['success']),
            row=2, col=1
        )
        
        # System Scalability
        servers = [1, 2, 4, 8, 16]
        capacity = [1000, 1950, 3800, 7200, 13500]
        cost = [100, 180, 340, 620, 1100]
        
        fig.add_trace(
            go.Scatter(x=servers, y=capacity, name='User Capacity', 
                      line=dict(color=self.colors['primary'], width=3)),
            row=2, col=2
        )
        fig.add_trace(
            go.Scatter(x=servers, y=cost, name='Cost ($)', 
                      line=dict(color=self.colors['error'], width=3, dash='dash')),
            row=2, col=2
        )
        
        fig.update_layout(
            title_text="Scooter Share Pro - Scalability Analysis",
            showlegend=True,
            height=800
        )
        
        fig.write_image(f"{self.output_dir}/scooter_share_pro_scalability.png", width=1400, height=800, scale=2)
        print("✅ Scalability analysis diagram created")
    
    def create_security_diagram(self):
        """Create security architecture diagram"""
        fig, ax = plt.subplots(1, 1, figsize=(14, 10))
        ax.set_title('Scooter Share Pro - Security Architecture', fontsize=16, fontweight='bold', color=self.colors['primary'])
        
        # Security layers
        security_layers = {
            'WAF & DDoS Protection': {'pos': (2, 9), 'size': (3, 1), 'color': self.colors['error']},
            'SSL/TLS Encryption': {'pos': (7, 9), 'size': (3, 1), 'color': self.colors['warning']},
            'JWT Authentication': {'pos': (2, 7), 'size': (3, 1), 'color': self.colors['success']},
            'OAuth 2.0 & RBAC': {'pos': (7, 7), 'size': (3, 1), 'color': self.colors['primary']},
            'API Rate Limiting': {'pos': (2, 5), 'size': (3, 1), 'color': self.colors['secondary']},
            'Input Validation': {'pos': (7, 5), 'size': (3, 1), 'color': self.colors['accent']},
            'Database Encryption': {'pos': (2, 3), 'size': (3, 1), 'color': self.colors['dark']},
            'Audit Logging': {'pos': (7, 3), 'size': (3, 1), 'color': self.colors['warning']},
            'Security Monitoring': {'pos': (4.5, 1), 'size': (3, 1), 'color': self.colors['error']},
        }
        
        for name, layer in security_layers.items():
            rect = plt.Rectangle(layer['pos'], layer['size'][0], layer['size'][1], 
                                facecolor=layer['color'], edgecolor='black', linewidth=2, alpha=0.8)
            ax.add_patch(rect)
            ax.text(layer['pos'][0] + layer['size'][0]/2, layer['pos'][1] + layer['size'][1]/2, 
                    name, ha='center', va='center', fontweight='bold', color='white', fontsize=9)
        
        # Add security zones
        zones = [
            ('External Threat Protection', 0.5, 10, self.colors['error']),
            ('Authentication & Authorization', 0.5, 8, self.colors['success']),
            ('API Security', 0.5, 6, self.colors['primary']),
            ('Data Protection', 0.5, 4, self.colors['dark']),
            ('Monitoring & Compliance', 0.5, 2, self.colors['warning']),
        ]
        
        for label, x, y, color in zones:
            ax.text(x, y, label, rotation=90, va='center', fontweight='bold', 
                   color=color, fontsize=11)
        
        ax.set_xlim(0, 11)
        ax.set_ylim(0, 11)
        ax.axis('off')
        
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/scooter_share_pro_security.png", dpi=300, bbox_inches='tight')
        plt.close()
        print("✅ Security architecture diagram created")
    
    def create_deployment_diagram(self):
        """Create enterprise deployment diagram"""
        fig, ax = plt.subplots(1, 1, figsize=(16, 10))
        ax.set_title('Scooter Share Pro - Enterprise Deployment', fontsize=16, fontweight='bold', color=self.colors['primary'])
        
        # Render Cloud Platform
        render_rect = plt.Rectangle((1, 1), 14, 9, facecolor='#f8f9fa', edgecolor=self.colors['primary'], linewidth=3)
        ax.add_patch(render_rect)
        ax.text(8, 9.5, 'Render Cloud Platform - Enterprise', ha='center', fontsize=14, fontweight='bold', color=self.colors['primary'])
        
        # Enterprise components
        components = {
            'CDN (Cloudflare)': {'pos': (2, 8), 'size': (2.5, 0.8), 'color': self.colors['secondary']},
            'Load Balancer': {'pos': (5.5, 8), 'size': (2, 0.8), 'color': self.colors['primary']},
            'API Gateway': {'pos': (8.5, 8), 'size': (2, 0.8), 'color': self.colors['warning']},
            'Web Services': {'pos': (12, 8), 'size': (2, 0.8), 'color': self.colors['accent']},
            'PostgreSQL Cluster': {'pos': (2, 6), 'size': (3, 0.8), 'color': self.colors['success']},
            'Redis Cluster': {'pos': (6, 6), 'size': (2.5, 0.8), 'color': self.colors['dark']},
            'File Storage': {'pos': (9.5, 6), 'size': (2, 0.8), 'color': self.colors['error']},
            'Monitoring Stack': {'pos': (12.5, 6), 'size': (2, 0.8), 'color': self.colors['secondary']},
            'Background Workers': {'pos': (3, 4), 'size': (2.5, 0.8), 'color': self.colors['warning']},
            'Queue System': {'pos': (6.5, 4), 'size': (2, 0.8), 'color': self.colors['primary']},
            'Log Aggregation': {'pos': (9.5, 4), 'size': (2, 0.8), 'color': self.colors['accent']},
            'Backup Systems': {'pos': (12.5, 4), 'size': (2, 0.8), 'color': self.colors['success']},
            'SSL Certificates': {'pos': (4, 2), 'size': (2, 0.8), 'color': self.colors['dark']},
            'Security Tools': {'pos': (7, 2), 'size': (2, 0.8), 'color': self.colors['error']},
            'Analytics Engine': {'pos': (10, 2), 'size': (2.5, 0.8), 'color': self.colors['secondary']},
        }
        
        for name, comp in components.items():
            rect = plt.Rectangle(comp['pos'], comp['size'][0], comp['size'][1], 
                                facecolor=comp['color'], edgecolor='black', linewidth=1, alpha=0.8)
            ax.add_patch(rect)
            ax.text(comp['pos'][0] + comp['size'][0]/2, comp['pos'][1] + comp['size'][1]/2, 
                    name, ha='center', va='center', fontweight='bold', color='white', fontsize=8)
        
        ax.set_xlim(0, 16)
        ax.set_ylim(0, 11)
        ax.axis('off')
        
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/scooter_share_pro_deployment.png", dpi=300, bbox_inches='tight')
        plt.close()
        print("✅ Enterprise deployment diagram created")
    
    def generate_all_diagrams(self):
        """Generate all diagrams"""
        print("🎨 Generating Scooter Share Pro diagrams...")
        self.create_architecture_diagram()
        self.create_database_schema()
        self.create_scalability_diagram()
        self.create_security_diagram()
        self.create_deployment_diagram()
        print(f"✅ All diagrams saved to {self.output_dir}/")

if __name__ == "__main__":
    generator = ScooterShareProDiagramGenerator()
    generator.generate_all_diagrams()
