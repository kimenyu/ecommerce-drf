from rest_framework import serializers
from .models import Product, Category, Cart, CartItem, ContactInfo, Profile, Order, OrderItem
from accounts.models import CustomUser
from accounts.serializers import CustomUserSerializer

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']
       
    def create(self, validated_data):
        return Category.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        return instance
    
class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer()  # Include CategorySerializer for nested serialization

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'image', 'price', 'category', 'stock']
        
    def create(self, validated_data):
        # Extract and create category separately to avoid errors
        category_data = validated_data.pop('category', None)
        category_instance = Category.objects.create(**category_data)
        
        # Now, create the product with the category instance
        validated_data['category'] = category_instance
        return Product.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.image = validated_data.get('image', instance.image)
        instance.price = validated_data.get('price', instance.price)
        
        # Update category if provided
        category_data = validated_data.get('category', {})
        instance.category.name = category_data.get('name', instance.category.name)
        instance.category.save()
        
        instance.stock = validated_data.get('stock', instance.stock)
        instance.save()
        return instance


class CartItemSerializer(serializers.ModelSerializer):
    cart = serializers.PrimaryKeyRelatedField(queryset=Cart.objects.all())
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    
    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'product', 'quantity']
        
    def create(self, validated_data):
        return CartItem.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        instance.cart = validated_data.get('cart', instance.cart)
        instance.product = validated_data.get('product', instance.product)
        instance.quantity = validated_data.get('quantity', instance.quantity)
        instance.save()
        return instance
    
class CartSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    items = CartItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Cart
        fields = ['id', 'user', 'created_at', 'items']
        
    def create(self, validated_data):
        return Cart.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        instance.user = validated_data.get('user', instance.user)
        instance.save()
        return instance
    
class ContactInfoSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    
    class Meta:
        model = ContactInfo
        fields = ['id', 'user', 'email']
        
    def create(self, validated_data):
        return ContactInfo.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        instance.user = validated_data.get('user', instance.user)
        instance.email = validated_data.get('email', instance.email)
        instance.save()
        return instance

class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    contact_info = ContactInfoSerializer()
    
    class Meta:
        model = Profile
        fields = ['id', 'user', 'first_name', 'last_name', 'contact_info', 'phone_number', 'address']
        
    def create(self, validated_data):
        # Extract and create contact info separately to avoid errors
        contact_info_data = validated_data.pop('contact_info', None)
        contact_info_instance = ContactInfo.objects.create(**contact_info_data)
        
        # Now, create the profile with the contact info instance
        validated_data['contact_info'] = contact_info_instance
        return Profile.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        instance.user = validated_data.get('user', instance.user)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        
        # Update contact info if provided
        contact_info_data = validated_data.get('contact_info', {})
        instance.contact_info.email = contact_info_data.get('email', instance.contact_info.email)
        instance.contact_info.save()
        
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.address = validated_data.get('address', instance.address)
        instance.save()
        return instance


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    contact_info = ContactInfoSerializer()

    class Meta:
        model = Order
        fields = ['id', 'user', 'items', 'total_amount', 'status', 'contact_info']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
        return order
    
    def update(self, instance, validated_data):
        instance.user = validated_data.get('user', instance.user)
        instance.cart = validated_data.get('cart', instance.cart)
        instance.total_amount = validated_data.get('total_amount', instance.total_amount)
        instance.status = validated_data.get('status', instance.status)

        # Update contact info if provided
        contact_info_data = validated_data.get('contact_info', {})
        instance.contact_info.email = contact_info_data.get('email', instance.contact_info.email)
        instance.contact_info.save()

        instance.save()
        return instance