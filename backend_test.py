#!/usr/bin/env python3
"""
Backend API Testing for Dropshipping Store
Tests all core APIs: products, cart, and orders
"""

import requests
import json
import uuid
from datetime import datetime

# Use the production URL from frontend/.env
BASE_URL = "https://02567917-cf96-4cc5-98d7-5bf12a74cc47.preview.emergentagent.com/api"

class BackendTester:
    def __init__(self):
        self.session_id = str(uuid.uuid4())
        self.product_ids = []
        self.test_results = []
        
    def log_test(self, test_name, success, message, response_data=None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        if response_data:
            result["response"] = response_data
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        
    def test_get_products(self):
        """Test GET /api/products - should return 2 products"""
        try:
            response = requests.get(f"{BASE_URL}/products", timeout=10)
            
            if response.status_code != 200:
                self.log_test("GET /api/products", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
            data = response.json()
            
            if "products" not in data:
                self.log_test("GET /api/products", False, "Response missing 'products' key")
                return False
                
            products = data["products"]
            
            if len(products) != 2:
                self.log_test("GET /api/products", False, f"Expected 2 products, got {len(products)}")
                return False
                
            # Store product IDs for later tests
            self.product_ids = [p["id"] for p in products]
            
            # Verify expected products
            product_names = [p["name"] for p in products]
            expected_names = ["Steam Cat Brush - Professional Grooming Tool", "3-in-1 Pet Bowl with Automatic Water Feeder"]
            
            steam_brush_found = any("Steam Cat Brush" in name for name in product_names)
            pet_bowl_found = any("3-in-1 Pet Bowl" in name for name in product_names)
            
            if not steam_brush_found or not pet_bowl_found:
                self.log_test("GET /api/products", False, f"Missing expected products. Found: {product_names}")
                return False
                
            # Verify product structure
            for product in products:
                required_fields = ["id", "name", "price", "description", "features", "rating", "in_stock"]
                missing_fields = [field for field in required_fields if field not in product]
                if missing_fields:
                    self.log_test("GET /api/products", False, f"Product missing fields: {missing_fields}")
                    return False
                    
            self.log_test("GET /api/products", True, f"Successfully retrieved {len(products)} products with correct structure")
            return True
            
        except requests.exceptions.RequestException as e:
            self.log_test("GET /api/products", False, f"Request failed: {str(e)}")
            return False
            
    def test_get_product_by_id(self):
        """Test GET /api/products/{product_id}"""
        if not self.product_ids:
            self.log_test("GET /api/products/{id}", False, "No product IDs available from previous test")
            return False
            
        try:
            product_id = self.product_ids[0]  # Test with first product
            response = requests.get(f"{BASE_URL}/products/{product_id}", timeout=10)
            
            if response.status_code != 200:
                self.log_test("GET /api/products/{id}", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
            product = response.json()
            
            if product["id"] != product_id:
                self.log_test("GET /api/products/{id}", False, f"Product ID mismatch: expected {product_id}, got {product['id']}")
                return False
                
            # Test invalid product ID
            response = requests.get(f"{BASE_URL}/products/invalid-id", timeout=10)
            if response.status_code != 404:
                self.log_test("GET /api/products/{id}", False, f"Expected 404 for invalid ID, got {response.status_code}")
                return False
                
            self.log_test("GET /api/products/{id}", True, "Successfully retrieved product by ID and handled invalid ID")
            return True
            
        except requests.exceptions.RequestException as e:
            self.log_test("GET /api/products/{id}", False, f"Request failed: {str(e)}")
            return False
            
    def test_cart_workflow(self):
        """Test complete cart workflow: get empty cart, add items, update, remove"""
        try:
            # Test 1: Get empty cart
            response = requests.get(f"{BASE_URL}/cart/{self.session_id}", timeout=10)
            if response.status_code != 200:
                self.log_test("Cart Workflow - Get Empty Cart", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
            cart = response.json()
            if cart["items"] != [] or cart["total"] != 0:
                self.log_test("Cart Workflow - Get Empty Cart", False, f"Expected empty cart, got: {cart}")
                return False
                
            # Test 2: Add item to cart
            if not self.product_ids:
                self.log_test("Cart Workflow - Add Item", False, "No product IDs available")
                return False
                
            product_id = self.product_ids[0]
            add_data = {"product_id": product_id, "quantity": 2}
            response = requests.post(f"{BASE_URL}/cart/{self.session_id}/add", 
                                   params=add_data, timeout=10)
            
            if response.status_code != 200:
                self.log_test("Cart Workflow - Add Item", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
            result = response.json()
            if "cart" not in result or len(result["cart"]["items"]) != 1:
                self.log_test("Cart Workflow - Add Item", False, f"Expected 1 item in cart, got: {result}")
                return False
                
            # Test 3: Add second product
            if len(self.product_ids) > 1:
                product_id_2 = self.product_ids[1]
                add_data_2 = {"product_id": product_id_2, "quantity": 1}
                response = requests.post(f"{BASE_URL}/cart/{self.session_id}/add", 
                                       params=add_data_2, timeout=10)
                
                if response.status_code != 200:
                    self.log_test("Cart Workflow - Add Second Item", False, f"HTTP {response.status_code}: {response.text}")
                    return False
                    
            # Test 4: Update cart item quantity
            update_data = {"product_id": product_id, "quantity": 3}
            response = requests.put(f"{BASE_URL}/cart/{self.session_id}/update", 
                                  params=update_data, timeout=10)
            
            if response.status_code != 200:
                self.log_test("Cart Workflow - Update Quantity", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
            # Test 5: Get updated cart
            response = requests.get(f"{BASE_URL}/cart/{self.session_id}", timeout=10)
            if response.status_code != 200:
                self.log_test("Cart Workflow - Get Updated Cart", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
            cart = response.json()
            if len(cart["items"]) == 0:
                self.log_test("Cart Workflow - Get Updated Cart", False, "Cart is empty after adding items")
                return False
                
            # Verify quantity was updated
            item_found = False
            for item in cart["items"]:
                if item["product_id"] == product_id and item["quantity"] == 3:
                    item_found = True
                    break
                    
            if not item_found:
                self.log_test("Cart Workflow - Update Quantity", False, f"Quantity not updated correctly. Cart: {cart}")
                return False
                
            # Test 6: Remove item from cart
            response = requests.delete(f"{BASE_URL}/cart/{self.session_id}/remove/{product_id}", timeout=10)
            if response.status_code != 200:
                self.log_test("Cart Workflow - Remove Item", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
            self.log_test("Cart Workflow", True, "Successfully completed full cart workflow: add, update, remove items")
            return True
            
        except requests.exceptions.RequestException as e:
            self.log_test("Cart Workflow", False, f"Request failed: {str(e)}")
            return False
            
    def test_order_creation(self):
        """Test order creation with sample customer data"""
        try:
            # First, add items to cart for order
            if not self.product_ids:
                self.log_test("Order Creation", False, "No product IDs available")
                return False
                
            # Add item to cart
            product_id = self.product_ids[0]
            add_data = {"product_id": product_id, "quantity": 1}
            response = requests.post(f"{BASE_URL}/cart/{self.session_id}/add", 
                                   params=add_data, timeout=10)
            
            if response.status_code != 200:
                self.log_test("Order Creation - Setup Cart", False, f"Failed to add item to cart: {response.text}")
                return False
                
            # Get cart for order data
            response = requests.get(f"{BASE_URL}/cart/{self.session_id}", timeout=10)
            if response.status_code != 200:
                self.log_test("Order Creation - Get Cart", False, f"Failed to get cart: {response.text}")
                return False
                
            cart = response.json()
            
            # Create order with realistic customer data
            order_data = {
                "session_id": self.session_id,
                "items": cart["items"],
                "total": cart["total"],
                "customer_info": {
                    "name": "Sarah Johnson",
                    "email": "sarah.johnson@email.com",
                    "phone": "+1-555-0123",
                    "address": {
                        "street": "123 Pet Lover Lane",
                        "city": "Austin",
                        "state": "TX",
                        "zip": "78701",
                        "country": "USA"
                    }
                }
            }
            
            response = requests.post(f"{BASE_URL}/orders", 
                                   json=order_data, 
                                   headers={"Content-Type": "application/json"},
                                   timeout=10)
            
            if response.status_code != 200:
                self.log_test("Order Creation", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
            result = response.json()
            
            if "order_id" not in result:
                self.log_test("Order Creation", False, f"Missing order_id in response: {result}")
                return False
                
            # Verify cart was cleared after order
            response = requests.get(f"{BASE_URL}/cart/{self.session_id}", timeout=10)
            if response.status_code == 200:
                cart_after_order = response.json()
                if len(cart_after_order["items"]) > 0:
                    self.log_test("Order Creation - Cart Clear", False, "Cart was not cleared after order creation")
                    return False
                    
            self.log_test("Order Creation", True, f"Successfully created order {result['order_id']} and cleared cart")
            return True
            
        except requests.exceptions.RequestException as e:
            self.log_test("Order Creation", False, f"Request failed: {str(e)}")
            return False
            
    def test_error_handling(self):
        """Test error handling for invalid requests"""
        try:
            # Test invalid product ID in cart operations
            invalid_id = "invalid-product-id"
            add_data = {"product_id": invalid_id, "quantity": 1}
            response = requests.post(f"{BASE_URL}/cart/{self.session_id}/add", 
                                   params=add_data, timeout=10)
            
            if response.status_code != 404:
                self.log_test("Error Handling - Invalid Product", False, f"Expected 404 for invalid product, got {response.status_code}")
                return False
                
            # Test cart operations on non-existent cart
            fake_session = "non-existent-session"
            update_data = {"product_id": "any-id", "quantity": 1}
            response = requests.put(f"{BASE_URL}/cart/{fake_session}/update", 
                                  params=update_data, timeout=10)
            
            if response.status_code != 404:
                self.log_test("Error Handling - Non-existent Cart", False, f"Expected 404 for non-existent cart, got {response.status_code}")
                return False
                
            self.log_test("Error Handling", True, "Successfully handled invalid product IDs and non-existent carts")
            return True
            
        except requests.exceptions.RequestException as e:
            self.log_test("Error Handling", False, f"Request failed: {str(e)}")
            return False
            
    def run_all_tests(self):
        """Run all backend API tests"""
        print(f"🚀 Starting Backend API Tests")
        print(f"📍 Base URL: {BASE_URL}")
        print(f"🔑 Session ID: {self.session_id}")
        print("=" * 60)
        
        # Test sequence
        tests = [
            ("Products API", self.test_get_products),
            ("Product by ID API", self.test_get_product_by_id),
            ("Cart Workflow", self.test_cart_workflow),
            ("Order Creation", self.test_order_creation),
            ("Error Handling", self.test_error_handling)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n🧪 Running {test_name}...")
            if test_func():
                passed += 1
            else:
                print(f"   ⚠️  {test_name} failed - check logs above")
                
        print("\n" + "=" * 60)
        print(f"📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All backend API tests passed!")
            return True
        else:
            print(f"❌ {total - passed} tests failed")
            return False
            
    def print_detailed_results(self):
        """Print detailed test results"""
        print("\n📋 Detailed Test Results:")
        print("-" * 60)
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}")
            print(f"   Message: {result['message']}")
            print(f"   Time: {result['timestamp']}")
            if not result["success"] and "response" in result:
                print(f"   Response: {result['response']}")
            print()

if __name__ == "__main__":
    tester = BackendTester()
    success = tester.run_all_tests()
    tester.print_detailed_results()
    
    if success:
        print("\n✅ Backend API testing completed successfully!")
    else:
        print("\n❌ Backend API testing completed with failures!")