import React, { useState, useEffect } from 'react';
import './App.css';

const API_BASE = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

function App() {
  const [products, setProducts] = useState([]);
  const [cart, setCart] = useState({ items: [], total: 0 });
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [showCart, setShowCart] = useState(false);
  const [showCheckout, setShowCheckout] = useState(false);
  const [sessionId] = useState(() => Math.random().toString(36).substring(7));
  const [loading, setLoading] = useState(true);
  const [customerInfo, setCustomerInfo] = useState({
    name: '',
    email: '',
    phone: '',
    address: ''
  });

  useEffect(() => {
    fetchProducts();
    fetchCart();
  }, []);

  const fetchProducts = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/products`);
      const data = await response.json();
      setProducts(data.products);
    } catch (error) {
      console.error('Error fetching products:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchCart = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/cart/${sessionId}`);
      const data = await response.json();
      setCart(data);
    } catch (error) {
      console.error('Error fetching cart:', error);
    }
  };

  const addToCart = async (productId, quantity = 1) => {
    try {
      const response = await fetch(`${API_BASE}/api/cart/${sessionId}/add?product_id=${productId}&quantity=${quantity}`, {
        method: 'POST',
      });
      const data = await response.json();
      setCart(data.cart);
      alert('Item added to cart!');
    } catch (error) {
      console.error('Error adding to cart:', error);
    }
  };

  const updateCartItem = async (productId, quantity) => {
    try {
      const response = await fetch(`${API_BASE}/api/cart/${sessionId}/update?product_id=${productId}&quantity=${quantity}`, {
        method: 'PUT',
      });
      const data = await response.json();
      setCart(data.cart);
    } catch (error) {
      console.error('Error updating cart:', error);
    }
  };

  const removeFromCart = async (productId) => {
    try {
      await fetch(`${API_BASE}/api/cart/${sessionId}/remove/${productId}`, {
        method: 'DELETE',
      });
      fetchCart();
    } catch (error) {
      console.error('Error removing from cart:', error);
    }
  };

  const submitOrder = async (e) => {
    e.preventDefault();
    try {
      const orderData = {
        session_id: sessionId,
        items: cart.items,
        total: cart.total,
        customer_info: customerInfo
      };
      
      const response = await fetch(`${API_BASE}/api/orders`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(orderData),
      });
      
      const data = await response.json();
      alert(`Order submitted successfully! Order ID: ${data.order_id}`);
      setShowCheckout(false);
      setShowCart(false);
      setCart({ items: [], total: 0 });
      setCustomerInfo({ name: '', email: '', phone: '', address: '' });
    } catch (error) {
      console.error('Error submitting order:', error);
      alert('Error submitting order. Please try again.');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 to-pink-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-purple-500 mx-auto"></div>
          <p className="mt-4 text-gray-600 text-lg">Loading products...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-pink-50">
      {/* Header */}
      <header className="bg-white shadow-lg sticky top-0 z-40">
        <div className="container mx-auto px-4 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center">
                <span className="text-white font-bold text-xl">🐾</span>
              </div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
                PawStore
              </h1>
            </div>
            <button
              onClick={() => setShowCart(true)}
              className="relative bg-gradient-to-r from-purple-500 to-pink-500 text-white px-6 py-2 rounded-full hover:from-purple-600 hover:to-pink-600 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
            >
              🛒 Cart ({cart.items.length})
              {cart.items.length > 0 && (
                <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full h-6 w-6 flex items-center justify-center">
                  {cart.items.reduce((sum, item) => sum + item.quantity, 0)}
                </span>
              )}
            </button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="bg-gradient-to-r from-purple-600 to-pink-600 text-white py-20">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-5xl font-bold mb-6">Premium Pet Care Products</h2>
          <p className="text-xl mb-8 max-w-2xl mx-auto opacity-90">
            Discover innovative grooming tools and feeding solutions that make pet care easier and more enjoyable for both you and your furry friends.
          </p>
          <div className="flex justify-center space-x-6 text-sm">
            <div className="flex items-center">
              <span className="text-green-300 mr-2">✓</span>
              Free Worldwide Shipping
            </div>
            <div className="flex items-center">
              <span className="text-green-300 mr-2">✓</span>
              30-Day Money Back
            </div>
            <div className="flex items-center">
              <span className="text-green-300 mr-2">✓</span>
              24/7 Support
            </div>
          </div>
        </div>
      </section>

      {/* Products Section */}
      <section className="py-16">
        <div className="container mx-auto px-4">
          <h3 className="text-3xl font-bold text-center mb-12 text-gray-800">Featured Products</h3>
          <div className="grid md:grid-cols-2 gap-8 max-w-6xl mx-auto">
            {products.map((product) => (
              <div key={product.id} className="bg-white rounded-2xl shadow-xl overflow-hidden hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-2">
                <div className="relative">
                  <img 
                    src={product.image_url} 
                    alt={product.name}
                    className="w-full h-64 object-cover"
                  />
                  {product.discount_percentage && (
                    <div className="absolute top-4 left-4 bg-red-500 text-white px-3 py-1 rounded-full text-sm font-bold">
                      -{product.discount_percentage}%
                    </div>
                  )}
                  <div className="absolute top-4 right-4 bg-white/90 backdrop-blur-sm px-2 py-1 rounded-full text-sm">
                    ⭐ {product.rating} ({product.reviews_count})
                  </div>
                </div>
                
                <div className="p-6">
                  <h4 className="text-xl font-bold mb-2 text-gray-800">{product.name}</h4>
                  <p className="text-gray-600 mb-4 line-clamp-3">{product.description}</p>
                  
                  <div className="mb-4">
                    <h5 className="font-semibold text-gray-700 mb-2">Key Features:</h5>
                    <ul className="text-sm text-gray-600 space-y-1">
                      {product.features.slice(0, 3).map((feature, index) => (
                        <li key={index} className="flex items-center">
                          <span className="text-green-500 mr-2">•</span>
                          {feature}
                        </li>
                      ))}
                    </ul>
                  </div>
                  
                  <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center space-x-2">
                      <span className="text-2xl font-bold text-gray-800">${product.price}</span>
                      {product.original_price && (
                        <span className="text-lg text-gray-500 line-through">${product.original_price}</span>
                      )}
                    </div>
                    <span className="text-green-600 font-semibold">In Stock</span>
                  </div>
                  
                  <div className="flex space-x-3">
                    <button
                      onClick={() => setSelectedProduct(product)}
                      className="flex-1 bg-gray-100 text-gray-800 py-3 rounded-lg hover:bg-gray-200 transition-colors duration-300 font-medium"
                    >
                      View Details
                    </button>
                    <button
                      onClick={() => addToCart(product.id)}
                      className="flex-1 bg-gradient-to-r from-purple-500 to-pink-500 text-white py-3 rounded-lg hover:from-purple-600 hover:to-pink-600 transition-all duration-300 font-medium shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
                    >
                      Add to Cart
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-800 text-white py-12">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-3 gap-8">
            <div>
              <h4 className="text-xl font-bold mb-4 text-purple-300">PawStore</h4>
              <p className="text-gray-300">Your trusted partner for premium pet care products. We're dedicated to making pet care easier and more enjoyable.</p>
            </div>
            <div>
              <h4 className="text-lg font-semibold mb-4">Quick Links</h4>
              <ul className="space-y-2 text-gray-300">
                <li><a href="#" className="hover:text-purple-300">About Us</a></li>
                <li><a href="#" className="hover:text-purple-300">Shipping Info</a></li>
                <li><a href="#" className="hover:text-purple-300">Returns</a></li>
                <li><a href="#" className="hover:text-purple-300">Contact</a></li>
              </ul>
            </div>
            <div>
              <h4 className="text-lg font-semibold mb-4">Customer Service</h4>
              <ul className="space-y-2 text-gray-300">
                <li>📧 support@pawstore.com</li>
                <li>📞 1-800-PET-CARE</li>
                <li>🕒 24/7 Support</li>
                <li>🌍 Worldwide Shipping</li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-700 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2025 PawStore. All rights reserved.</p>
          </div>
        </div>
      </footer>

      {/* Product Detail Modal */}
      {selectedProduct && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-4xl max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-start mb-6">
                <h2 className="text-2xl font-bold text-gray-800">{selectedProduct.name}</h2>
                <button
                  onClick={() => setSelectedProduct(null)}
                  className="text-gray-500 hover:text-gray-700 text-2xl"
                >
                  ×
                </button>
              </div>
              
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <img 
                    src={selectedProduct.image_url} 
                    alt={selectedProduct.name}
                    className="w-full h-64 object-cover rounded-lg mb-4"
                  />
                  <div className="grid grid-cols-3 gap-2">
                    {selectedProduct.images.map((img, index) => (
                      <img 
                        key={index}
                        src={img} 
                        alt={`${selectedProduct.name} ${index + 1}`}
                        className="w-full h-20 object-cover rounded cursor-pointer border-2 border-transparent hover:border-purple-500"
                      />
                    ))}
                  </div>
                </div>
                
                <div>
                  <p className="text-gray-600 mb-4">{selectedProduct.description}</p>
                  
                  <div className="mb-4">
                    <h4 className="font-semibold text-gray-700 mb-2">All Features:</h4>
                    <ul className="text-sm text-gray-600 space-y-2">
                      {selectedProduct.features.map((feature, index) => (
                        <li key={index} className="flex items-center">
                          <span className="text-green-500 mr-2">✓</span>
                          {feature}
                        </li>
                      ))}
                    </ul>
                  </div>
                  
                  <div className="flex items-center space-x-4 mb-6">
                    <div className="flex items-center space-x-2">
                      <span className="text-3xl font-bold text-gray-800">${selectedProduct.price}</span>
                      {selectedProduct.original_price && (
                        <span className="text-xl text-gray-500 line-through">${selectedProduct.original_price}</span>
                      )}
                    </div>
                    <div className="bg-yellow-100 text-yellow-800 px-2 py-1 rounded text-sm">
                      ⭐ {selectedProduct.rating} ({selectedProduct.reviews_count} reviews)
                    </div>
                  </div>
                  
                  <button
                    onClick={() => {
                      addToCart(selectedProduct.id);
                      setSelectedProduct(null);
                    }}
                    className="w-full bg-gradient-to-r from-purple-500 to-pink-500 text-white py-3 rounded-lg hover:from-purple-600 hover:to-pink-600 transition-all duration-300 font-medium shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
                  >
                    Add to Cart - ${selectedProduct.price}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Cart Modal */}
      {showCart && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-gray-800">Shopping Cart</h2>
                <button
                  onClick={() => setShowCart(false)}
                  className="text-gray-500 hover:text-gray-700 text-2xl"
                >
                  ×
                </button>
              </div>
              
              {cart.items.length === 0 ? (
                <div className="text-center py-12">
                  <p className="text-gray-500 text-lg mb-4">Your cart is empty</p>
                  <button
                    onClick={() => setShowCart(false)}
                    className="bg-gradient-to-r from-purple-500 to-pink-500 text-white px-6 py-2 rounded-lg"
                  >
                    Continue Shopping
                  </button>
                </div>
              ) : (
                <>
                  <div className="space-y-4 mb-6">
                    {cart.items.map((item) => {
                      const product = products.find(p => p.id === item.product_id);
                      return (
                        <div key={item.product_id} className="flex items-center justify-between border-b pb-4">
                          <div className="flex items-center space-x-4">
                            <img 
                              src={product?.image_url} 
                              alt={product?.name}
                              className="w-16 h-16 object-cover rounded"
                            />
                            <div>
                              <h4 className="font-medium text-gray-800">{product?.name}</h4>
                              <p className="text-gray-600">${item.price}</p>
                            </div>
                          </div>
                          <div className="flex items-center space-x-2">
                            <button
                              onClick={() => updateCartItem(item.product_id, item.quantity - 1)}
                              className="bg-gray-200 text-gray-700 w-8 h-8 rounded-full hover:bg-gray-300"
                            >
                              -
                            </button>
                            <span className="w-8 text-center">{item.quantity}</span>
                            <button
                              onClick={() => updateCartItem(item.product_id, item.quantity + 1)}
                              className="bg-gray-200 text-gray-700 w-8 h-8 rounded-full hover:bg-gray-300"
                            >
                              +
                            </button>
                            <button
                              onClick={() => removeFromCart(item.product_id)}
                              className="text-red-500 ml-4 hover:text-red-700"
                            >
                              🗑️
                            </button>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                  
                  <div className="border-t pt-4">
                    <div className="flex justify-between items-center text-xl font-bold mb-4">
                      <span>Total: ${cart.total.toFixed(2)}</span>
                    </div>
                    <div className="flex space-x-4">
                      <button
                        onClick={() => setShowCart(false)}
                        className="flex-1 bg-gray-200 text-gray-800 py-3 rounded-lg hover:bg-gray-300"
                      >
                        Continue Shopping
                      </button>
                      <button
                        onClick={() => setShowCheckout(true)}
                        className="flex-1 bg-gradient-to-r from-purple-500 to-pink-500 text-white py-3 rounded-lg hover:from-purple-600 hover:to-pink-600"
                      >
                        Checkout
                      </button>
                    </div>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Checkout Modal */}
      {showCheckout && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-gray-800">Checkout</h2>
                <button
                  onClick={() => setShowCheckout(false)}
                  className="text-gray-500 hover:text-gray-700 text-2xl"
                >
                  ×
                </button>
              </div>
              
              <form onSubmit={submitOrder} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
                  <input
                    type="text"
                    required
                    value={customerInfo.name}
                    onChange={(e) => setCustomerInfo({...customerInfo, name: e.target.value})}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                  <input
                    type="email"
                    required
                    value={customerInfo.email}
                    onChange={(e) => setCustomerInfo({...customerInfo, email: e.target.value})}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
                  <input
                    type="tel"
                    required
                    value={customerInfo.phone}
                    onChange={(e) => setCustomerInfo({...customerInfo, phone: e.target.value})}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Address</label>
                  <textarea
                    required
                    value={customerInfo.address}
                    onChange={(e) => setCustomerInfo({...customerInfo, address: e.target.value})}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500"
                    rows="3"
                  />
                </div>
                
                <div className="border-t pt-4">
                  <div className="flex justify-between items-center text-lg font-bold mb-4">
                    <span>Total: ${cart.total.toFixed(2)}</span>
                  </div>
                  <button
                    type="submit"
                    className="w-full bg-gradient-to-r from-purple-500 to-pink-500 text-white py-3 rounded-lg hover:from-purple-600 hover:to-pink-600 font-medium"
                  >
                    Place Order
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;