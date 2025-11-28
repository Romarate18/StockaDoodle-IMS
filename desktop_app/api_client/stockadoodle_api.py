import requests
import base64
import os
from typing import Dict, Any, Optional
from datetime import date, datetime


class StockaDoodleAPIError(Exception):
    """Custom exception for API errors"""
    pass

class APIResponse:
    
    def __init__(self, success: bool, data=None, error: str = None, status_code: int = None):
        self.success = success
        self.data = data
        self.error = error
        self.status_code = status_code


class StockaDoodleAPI:
    """
    Complete API client for StockaDoodle Inventory Management System
    Handles all communication with the Flask REST API    
    """
    def __init__(self, base_url: str = "http://127.0.0.1:5000/api/v1"):
        self.base_url = base_url.rstrip("/")
        self.timeout = 10
        
        # Initialize sub-clients
        self.products = ProductClient(self)

    # ==================================================================
    # HELPER METHODS
    # ==================================================================
    
    def _url(self, endpoint: str) -> str:
        """Construct full URL for endpoint"""
        return f"{self.base_url}/{endpoint.lstrip('/')}"
    
    def _request(self, method: str, endpoint: str, **kwargs) -> tuple:
        """
        Make HTTP request to API
        
        Args:
            method: HTTP method (GET, POST, PUT, PATCH, DELETE)
            endpoint: API endpoint path
            **kwargs: Additional arguments for requests (json, params, files, etc.)
        
        Returns:
            tuple: (response_data, status_code)
        
        Raises:
            StockaDoodleAPIError: If request fails
        """
        url = self._url(endpoint)
        kwargs.setdefault('timeout', self.timeout)
        
        try:
            response = requests.request(method, url, **kwargs)
            
            # Try to parse JSON response
            try:
                data = response.json()
            except ValueError:
                data = response.text
            
            # Check for errors
            if response.status_code >= 400:
                error_msg = data.get('errors', [str(data)]) if isinstance(data, dict) else [str(data)]
                raise StockaDoodleAPIError(f"API Error: {', '.join(error_msg)}")
            
            return data, response.status_code
            
        except requests.RequestException as e:
            raise StockaDoodleAPIError(f"Connection failed: {str(e)}")
    
    def _encode_image(self, image_path: str) -> str:
        """Encode image file to base64 string"""
        try:
            with open(image_path, 'rb') as f:
                return base64.b64encode(f.read()).decode('utf-8')
        except Exception as e:
            raise StockaDoodleAPIError(f"Failed to encode image: {str(e)}")
    
    # ==================================================================
    # PRODUCT ENDPOINTS
    # ==================================================================
    
    def get_products(self, **filters) -> tuple:
        """
        Get all products with optional filters
        
        Args:
            name: Filter by name (contains)
            brand: Filter by brand (contains)
            category_id: Filter by category ID
            price_gt: Price greater than
            price_gte: Price greater than or equal
            price_lt: Price less than
            price_lte: Price less than or equal
            sort_by: Sort field (name, price, created_at)
            sort_dir: Sort direction (asc, desc)
            page: Page number
            per_page: Items per page
            include_image: Include base64 image (true/false)
        
        Returns:
            tuple: (products_data, status_code)
        """
        return self._request('GET', 'products', params=filters)
    
    def get_product(self, product_id: int, include_image: bool = False, 
                    include_batches: bool = False) -> tuple:
        """Get single product by ID"""
        params = {
            'include_image': 'true' if include_image else 'false',
            'include_batches': 'true' if include_batches else 'false'
        }
        return self._request('GET', f'products/{product_id}', params=params)
    
    def create_product(self, name: str, price: float, brand: str = None,
                      category_id: int = None, min_stock_level: int = 10,
                      details: str = None, stock_level: int = 0,
                      expiration_date: str = None, image_path: str = None,
                      added_by: int = None) -> tuple:
        """
        Create new product
        
        Args:
            name: Product name (required)
            price: Product price (required)
            brand: Brand name
            category_id: Category ID
            min_stock_level: Minimum stock level for alerts
            details: Product description
            stock_level: Initial stock quantity
            expiration_date: Expiration date (YYYY-MM-DD)
            image_path: Path to product image file
            added_by: User ID who added the product
        
        Returns:
            tuple: (product_data, status_code)
        """
        data = {
            'name': name,
            'price': price,
            'brand': brand,
            'category_id': category_id,
            'min_stock_level': min_stock_level,
            'details': details,
            'stock_level': stock_level,
            'expiration_date': expiration_date,
            'added_by': added_by
        }
        
        # Add image if provided
        if image_path:
            data['image_base64'] = self._encode_image(image_path)
        
        return self._request('POST', 'products', json=data)
    
    def update_product(self, product_id: int, **updates) -> tuple:
        """
        Update product (PATCH - partial update)
        
        Args:
            product_id: Product ID
            **updates: Fields to update (name, price, brand, category_id, etc.)
        
        Returns:
            tuple: (product_data, status_code)
        """
        # Handle image path
        if 'image_path' in updates:
            updates['image_base64'] = self._encode_image(updates.pop('image_path'))
        
        return self._request('PATCH', f'products/{product_id}', json=updates)
    
    def replace_product(self, product_id: int, **data) -> tuple:
        """Replace product (PUT - full replacement)"""
        if 'image_path' in data:
            data['image_base64'] = self._encode_image(data.pop('image_path'))
        
        return self._request('PUT', f'products/{product_id}', json=data)
    
    def delete_product(self, product_id: int, user_id: int = None) -> tuple:
        """Delete product"""
        return self._request('DELETE', f'products/{product_id}', 
                           json={'user_id': user_id})
    
    # Stock Batch Operations
    def get_stock_batches(self, product_id: int) -> tuple:
        """Get all stock batches for a product"""
        return self._request('GET', f'products/{product_id}/stock_batches')
    
    def add_stock_batch(self, product_id: int, quantity: int, 
                       expiration_date: str, added_by: int = None,
                       reason: str = "Stock added") -> tuple:
        """Add new stock batch to product"""
        data = {
            'quantity': quantity,
            'expiration_date': expiration_date,
            'added_by': added_by,
            'reason': reason
        }
        return self._request('POST', f'products/{product_id}/stock_batches', json=data)
    
    def update_stock_batch_metadata(self, product_id: int, batch_id: int, 
                                 expiration_date: str = None, 
                                 added_by: int = None, reason: str = None) -> tuple:
        """Update stock batch metadata"""
        data = {}
        if expiration_date:
            data['expiration_date'] = expiration_date
        if added_by:
            data['added_by'] = added_by
        if reason:
            data['reason'] = reason

        # Only send data if it's non-empty
        if not data:
            raise ValueError("At least one metadata field (expiration_date, added_by, reason) must be provided")

        return self._request('PATCH', f'products/{product_id}/stock_batches/{batch_id}/metadata', json=data)

    def remove_stock_batch(self, product_id: int, batch_id: int, 
                          quantity: int, reason: str = None) -> tuple:
        """Remove quantity from stock batch"""
        data = {'quantity': quantity, 'reason': reason}
        return self._request('PATCH', f'products/{product_id}/stock_batches/{batch_id}', 
                           json=data)
    
    def delete_stock_batch(self, product_id: int, batch_id: int, 
                          user_id: int = None) -> tuple:
        """Delete entire stock batch"""
        return self._request('DELETE', f'products/{product_id}/stock_batches/{batch_id}',
                           json={'user_id': user_id})
    
    # ==================================================================
    # CATEGORY ENDPOINTS
    # ==================================================================
    
    def get_categories(self, include_image: bool = False) -> tuple:
        """Get all categories"""
        params = {'include_image': 'true' if include_image else 'false'}
        return self._request('GET', 'categories', params=params)
    
    def get_category(self, category_id: int, include_image: bool = False) -> tuple:
        """Get single category by ID"""
        params = {'include_image': 'true' if include_image else 'false'}
        return self._request('GET', f'categories/{category_id}', params=params)
    
    def create_category(self, name: str, description: str = None,
                       image_path: str = None, user_id: int = None) -> tuple:
        """Create new category"""
        data = {
            'name': name,
            'description': description,
            'user_id': user_id
        }
        
        if image_path:
            data['image_base64'] = self._encode_image(image_path)
        
        return self._request('POST', 'categories', json=data)
    
    def update_category(self, category_id: int, **updates) -> tuple:
        """Update category (PATCH)"""
        if 'image_path' in updates:
            updates['image_base64'] = self._encode_image(updates.pop('image_path'))
        
        return self._request('PATCH', f'categories/{category_id}', json=updates)
    
    def replace_category(self, category_id: int, **data) -> tuple:
        """Replace category (PUT)"""
        if 'image_path' in data:
            data['image_base64'] = self._encode_image(data.pop('image_path'))
        
        return self._request('PUT', f'categories/{category_id}', json=data)
    
    def delete_category(self, category_id: int, user_id: int = None) -> tuple:
        """Delete category"""
        return self._request('DELETE', f'categories/{category_id}',
                           json={'user_id': user_id})
    
    # ==================================================================
    # USER ENDPOINTS
    # ==================================================================
    
    def get_users(self, role: str = None, include_image: bool = False) -> tuple:
        """Get all users with optional role filter"""
        params = {
            'role': role,
            'include_image': 'true' if include_image else 'false'
        }
        return self._request('GET', 'users', params=params)
    
    def get_user(self, user_id: int, include_image: bool = False) -> tuple:
        """Get single user by ID"""
        params = {'include_image': 'true' if include_image else 'false'}
        return self._request('GET', f'users/{user_id}', params=params)
    
    def create_user(self, username: str, password: str, full_name: str,
                   email: str, role: str = "staff", image_path: str = None) -> tuple:
        """Create new user account"""
        data = {
            'username': username,
            'password': password,
            'full_name': full_name,
            'email': email,
            'role': role
        }
        
        if image_path:
            data['image_base64'] = self._encode_image(image_path)
        
        return self._request('POST', 'users', json=data)
    
    def update_user(self, user_id: int, **updates) -> tuple:
        """Update user (PATCH)"""
        if 'image_path' in updates:
            updates['image_base64'] = self._encode_image(updates.pop('image_path'))
        
        return self._request('PATCH', f'users/{user_id}', json=updates)
    
    def replace_user(self, user_id: int, **data) -> tuple:
        """Replace user (PUT)"""
        if 'image_path' in data:
            data['image_base64'] = self._encode_image(data.pop('image_path'))
        
        return self._request('PUT', f'users/{user_id}', json=data)
    
    def delete_user(self, user_id: int) -> tuple:
        """Delete user account"""
        return self._request('DELETE', f'users/{user_id}')
    
    # Authentication
    def login(self, username: str, password: str) -> tuple:
        """Authenticate user and check MFA requirement"""
        data = {'username': username, 'password': password}
        return self._request('POST', 'users/auth/login', json=data)
    
    def send_mfa_code(self, username: str, email: str) -> tuple:
        """Send MFA code to user email"""
        data = {'username': username, 'email': email}
        return self._request('POST', 'users/auth/mfa/send', json=data)
    
    def verify_mfa_code(self, username: str, code: str) -> tuple:
        """Verify MFA code"""
        data = {'username': username, 'code': code}
        return self._request('POST', 'users/auth/mfa/verify', json=data)
    
    def change_password(self, user_id: int, old_password: str, 
                       new_password: str) -> tuple:
        """Change user password with verification"""
        data = {'old_password': old_password, 'new_password': new_password}
        return self._request('POST', f'users/{user_id}/change-password', json=data)
    
    # ==================================================================
    # SALES ENDPOINTS
    # ==================================================================
    
    def record_sale(self, retailer_id: int, items: List[Dict], 
                   total_amount: float) -> tuple:
        """
        Record atomic sale transaction
        
        Args:
            retailer_id: ID of retailer making sale
            items: List of {'product_id': int, 'quantity': int, 'line_total': float}
            total_amount: Total sale amount
        
        Returns:
            tuple: (sale_data, status_code)
        """
        data = {
            'retailer_id': retailer_id,
            'items': items,
            'total_amount': total_amount
        }
        return self._request('POST', 'sales', json=data)
    
    def get_sale(self, sale_id: int, include_items: bool = True) -> tuple:
        """Get single sale by ID"""
        params = {'include_items': 'true' if include_items else 'false'}
        return self._request('GET', f'sales/{sale_id}', params=params)
    
    def undo_sale(self, sale_id: int, user_id: int) -> tuple:
        """Undo sale and restore stock"""
        return self._request('DELETE', f'sales/{sale_id}', json={'user_id': user_id})
    
    def get_sales_report(self, start_date: str = None, end_date: str = None,
                        retailer_id: int = None) -> tuple:
        """
        Get sales report for date range
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            retailer_id: Filter by specific retailer
        
        Returns:
            tuple: (report_data, status_code)
        """
        params = {
            'start': start_date,
            'end': end_date,
            'retailer_id': retailer_id
        }
        return self._request('GET', 'sales/reports', params=params)
    
    # ==================================================================
    # LOGS ENDPOINTS
    # ==================================================================
    
    def get_product_logs(self, product_id: int, limit: int = 50) -> tuple:
        """Get logs for specific product"""
        return self._request('GET', f'logs/product/{product_id}', 
                           params={'limit': limit})
    
    def get_user_logs(self, user_id: int, limit: int = 50) -> tuple:
        """Get logs for specific user"""
        return self._request('GET', f'logs/user/{user_id}', 
                           params={'limit': limit})
    
    def get_all_logs(self, action_type: str = None, limit: int = 100) -> tuple:
        """Get all product logs with optional filtering"""
        params = {'action_type': action_type, 'limit': limit}
        return self._request('GET', 'logs', params=params)
    
    def dispose_product(self, product_id: int, user_id: int, quantity: int,
                       notes: str = None) -> tuple:
        """Dispose product with atomic stock deduction"""
        data = {
            'product_id': product_id,
            'user_id': user_id,
            'quantity': quantity,
            'notes': notes
        }
        return self._request('POST', 'logs/dispose', json=data)
    
    def log_desktop_action(self, action_type: str, user_id: int = None,
                          target_entity: str = None, details: str = None) -> tuple:
        """Log desktop application activity"""
        data = {
            'action_type': action_type,
            'user_id': user_id,
            'target_entity': target_entity,
            'details': details
        }
        return self._request('POST', 'logs/desktop', json=data)
    
    # ==================================================================
    # DASHBOARD ENDPOINTS
    # ==================================================================
    
    def get_admin_dashboard(self) -> tuple:
        """Get admin dashboard metrics"""
        return self._request('GET', 'dashboard/admin')
    
    def get_manager_dashboard(self) -> tuple:
        """Get manager dashboard metrics"""
        return self._request('GET', 'dashboard/manager')
    
    def get_retailer_dashboard(self, user_id: int) -> tuple:
        """Get retailer dashboard metrics"""
        return self._request('GET', f'dashboard/retailer/{user_id}')
    
    # ==================================================================
    # METRICS ENDPOINTS
    # ==================================================================
    
    def get_retailer_metrics(self, user_id: int) -> tuple:
        """Get retailer performance metrics"""
        return self._request('GET', f'retailer/{user_id}')
    
    def get_leaderboard(self, sort_by: str = 'current_streak', 
                       limit: int = 10) -> tuple:
        """Get top performing retailers"""
        params = {'sort_by': sort_by, 'limit': limit}
        return self._request('GET', 'retailer/leaderboard', params=params)
    
    def update_retailer_quota(self, user_id: int, daily_quota: float,
                             updated_by: int = None) -> tuple:
        """Update retailer's daily quota"""
        data = {'daily_quota': daily_quota, 'updated_by': updated_by}
        return self._request('PATCH', f'retailer/{user_id}/quota', json=data)
    
    def reset_retailer_streak(self, user_id: int, admin_id: int = None) -> tuple:
        """Reset retailer's streak"""
        return self._request('POST', f'retailer/{user_id}/reset-streak',
                           json={'admin_id': admin_id})
    
    # ==================================================================
    # REPORTS ENDPOINTS
    # ==================================================================
    
    def get_sales_performance_report(self, start_date: str = None, 
                                    end_date: str = None) -> tuple:
        """Report 1: Sales Performance Report"""
        params = {'start_date': start_date, 'end_date': end_date}
        return self._request('GET', 'reports/sales-performance', params=params)
    
    def get_category_distribution_report(self) -> tuple:
        """Report 2: Category Distribution Report"""
        return self._request('GET', 'reports/category-distribution')
    
    def get_retailer_performance_report(self) -> tuple:
        """Report 3: Retailer Performance Report"""
        return self._request('GET', 'reports/retailer-performance')
    
    def get_alerts_report(self, days_ahead: int = 7) -> tuple:
        """Report 4: Low-Stock and Expiration Alert Report"""
        return self._request('GET', 'reports/alerts', params={'days_ahead': days_ahead})
    
    def get_managerial_activity_report(self, start_date: str = None,
                                      end_date: str = None) -> tuple:
        """Report 5: Managerial Activity Log Report"""
        params = {'start_date': start_date, 'end_date': end_date}
        return self._request('GET', 'reports/managerial-activity', params=params)
    
    def get_transactions_report(self, start_date: str = None,
                               end_date: str = None) -> tuple:
        """Report 6: Detailed Sales Transaction Report"""
        params = {'start_date': start_date, 'end_date': end_date}
        return self._request('GET', 'reports/transactions', params=params)
    
    def get_user_accounts_report(self) -> tuple:
        """Report 7: User Accounts Report"""
        return self._request('GET', 'reports/user-accounts')
    
    # PDF Downloads
    def download_pdf_report(self, report_type: str, **params) -> bytes:
        """
        Download PDF report
        
        Args:
            report_type: One of 'sales-performance', 'category-distribution',
                        'retailer-performance', 'alerts', 'managerial-activity',
                        'transactions', 'user-accounts'
            **params: Query parameters for the report (dates, filters, etc.)
        
        Returns:
            bytes: PDF file content
        """
        url = self._url(f'reports/{report_type}/pdf')
        response = requests.get(url, params=params, timeout=self.timeout)
        
        if response.status_code != 200:
            raise StockaDoodleAPIError(f"Failed to download PDF: {response.status_code}")
        
        return response.content
    
    # ==================================================================
    # NOTIFICATIONS ENDPOINTS
    # ==================================================================
    
    def send_low_stock_alerts(self, triggered_by: int = None) -> tuple:
        """Send low stock alerts to managers"""
        return self._request('POST', 'notifications/low-stock',
                           json={'triggered_by': triggered_by})
    
    def send_expiration_alerts(self, days_ahead: int = 7, 
                              triggered_by: int = None) -> tuple:
        """Send expiration alerts to managers"""
        data = {'days_ahead': days_ahead, 'triggered_by': triggered_by}
        return self._request('POST', 'notifications/expiring', json=data)
    
    def send_daily_summary(self, triggered_by: int = None) -> tuple:
        """Send daily inventory summary to managers"""
        return self._request('POST', 'notifications/daily-summary',
                           json={'triggered_by': triggered_by})
    
    def get_notification_history(self, limit: int = 50, 
                                 notification_type: str = None) -> tuple:
        """Get notification history"""
        params = {'limit': limit, 'notification_type': notification_type}
        return self._request('GET', 'notifications/history', params=params)
    
    # ==================================================================
    # HEALTH CHECK
    # ==================================================================
    
    def health_check(self) -> tuple:
        """Check API server health"""
        return self._request('GET', 'health')