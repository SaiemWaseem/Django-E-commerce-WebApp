from django.shortcuts import render
from django.views import View
from django.db import connection
import pandas as pd
from prophet import Prophet

# Create your views here.

class Revenue_Products(View):
    def get(self, request, *args, **kwargs):
        # Create a cursor object to execute raw SQL queries
        cursor = connection.cursor()
        
        # Execute the SQL query to get revenue data for products
        cursor.execute("SELECT sum(a.quantity) as total_quantity, b.name, b.price FROM customer_orderitem a, customer_car b where a.product_id = b.id group by a.product_id")

        # Fetch the data from the cursor
        data = cursor.fetchall()
        
        # Convert the fetched data into a DataFrame
        df = pd.DataFrame(data)
        
        # Print the DataFrame without column names
        print("Does not show column names")
        print(df)

        # Get column names from cursor description and set them as DataFrame column names
        column_names = [desc[0] for desc in cursor.description]
        df.columns = column_names
        
        # Print the DataFrame with column names
        print("shows column names")
        print(df)
        
        # Calculate sales by product
        df['sales_by_product'] = df.total_quantity * df.price
        
        # Sort DataFrame by sales and get top 5 products
        df = df.sort_values('sales_by_product', ascending=False).iloc[:5]
        
        # Extract product names and sales values as lists
        products = df['name'].tolist()
        sales_by_product = df['sales_by_product'].tolist()
        
        # Render the template with product and sales data
        return render(request, 'car/revenue_by_products.html', {'products': products, 'sales_by_product': sales_by_product})

class Revenue_Categories(View):
    def get(self, request, *args, **kwargs):
        cursor = connection.cursor()
        users = cursor.execute("select cat_name, sum(price*total_quantity) as total_by_category from (SELECT a.product_id, b.name, b.price as price, c.name as cat_name, sum(a.quantity) as total_quantity  FROM customer_orderitem a, customer_Car b, customer_Category c, customer_Car_Category d where a.product_id = b.id and b.id = d.car_id and c.id = d.category_id group by a.product_id, b.name, b.price, c.name) as s group by cat_name;")
        data = cursor.fetchall()

        # Set column names directly
        df = pd.DataFrame(data, columns=['cat_name', 'total_by_category'])

        # Sort DataFrame by total_by_category and select top 5 categories
        df = df.sort_values('total_by_category', ascending=False).iloc[:5]

        # Extract categories and sales by category
        categories = df['cat_name'].tolist()
        sales_by_category = df['total_by_category'].tolist()

        print("Categories:", categories)
        print("Sales by Category:", sales_by_category)

        # Render the template with categories and sales_by_category
        return render(request, 'car/revenue_by_categories.html', {'categories': categories, 'sales_by_category': sales_by_category})

class Revenue_Forecast(View):
    def get(self, request, *args, **kwargs):
        pizza_df = pd.read_excel('Data.xlsx')   
        print(pizza_df.head(5))     
        #Calculate daily sales/revenue and make a new pandas df
        daily_revenue_analysis = pizza_df.groupby((pizza_df['order_date']))['total_price'].sum()
        df = daily_revenue_analysis.copy().to_frame()
        df = df.rename(columns={'total_price': 'daily_revenue'})
        df = df.reset_index()
        print(df.head())
        df = df.rename(columns={'order_date': 'ds', 'daily_revenue': 'y'})
        print(df.head())        
        # Make the prophet model and fit on the data
        df_prophet = Prophet(changepoint_prior_scale=0.15, weekly_seasonality=True)
        df_prophet.fit(df)
        df_forecast = df_prophet.make_future_dataframe(periods=180 * 1, freq='D')
        # Make predictions
        df_forecast = df_prophet.predict(df_forecast)
    
        df_prophet.plot(df_forecast, xlabel = 'Date', ylabel = 'Daily Revenue (USD)').savefig('media/1.png')

        
        return render(request, 'car/revenue_forecast.html')