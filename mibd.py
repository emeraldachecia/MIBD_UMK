import pyodbc as odbc
import datetime
import random

DRIVER_NAME = 'SQL SERVER'
SERVER_NAME = r'Rey-PC\SQLEXPRESS'
DATABASE_NAME = 'students'

connection_string = f"""
    DRIVER={{{DRIVER_NAME}}};
    SERVER={SERVER_NAME};
    DATABASE={DATABASE_NAME};
    Trusted_Connection=yes;
"""

conn = odbc.connect(connection_string)
cursor = conn.cursor()

def create_tables():
    # Users table
    cursor.execute("""
    IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'Users')
    BEGIN
        CREATE TABLE Users (
            User_ID INT PRIMARY KEY IDENTITY,
            PhoneNum VARCHAR(12) NOT NULL UNIQUE,
            OTP VARCHAR(6),
            Role VARCHAR(50) NOT NULL,
            deleted_at DATETIME
        )
    END
    """)

    # UMK profiles table
    cursor.execute("""
    IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'UMK_Profiles')
    BEGIN
        CREATE TABLE UMK_Profiles (
            UMK_ID INT PRIMARY KEY IDENTITY,
            Name VARCHAR(255) NOT NULL,
            Description VARCHAR(255),
            Logo VARBINARY(MAX),
            Address VARCHAR(255),
            PhoneNum VARCHAR(12) NOT NULL UNIQUE,
            Owner VARCHAR(255),
            City VARCHAR(100),
            Province VARCHAR(100),
            deleted_at DATETIME
        )
    END
    """)

    # Products table
    cursor.execute("""
    IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'Products')
    BEGIN
        CREATE TABLE Products (
            Product_ID INT PRIMARY KEY IDENTITY,
            UMK_ID INT,
            Code VARCHAR(50) NOT NULL,
            Name VARCHAR(255) NOT NULL,
            Image VARBINARY(MAX),
            Description VARCHAR(255),
            Unit VARCHAR(50),
            Price DECIMAL(10, 2) NOT NULL,
            deleted_at DATETIME,
            FOREIGN KEY (UMK_ID) REFERENCES UMK_Profiles(UMK_ID)
        )
    END
    """)

    # Transactions table
    cursor.execute("""
    IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'Transactions')
    BEGIN
        CREATE TABLE Transactions (
            Transaction_ID INT PRIMARY KEY IDENTITY,
            UMK_ID INT,
            Type VARCHAR(50),
            Amount DECIMAL(10, 2),
            Date DATETIME,
            Description VARCHAR(255),
            deleted_at DATETIME,
            FOREIGN KEY (UMK_ID) REFERENCES UMK_Profiles(UMK_ID)
        )
    END
    """)

    # Cities table
    cursor.execute("""
    IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'Cities')
    BEGIN
        CREATE TABLE Cities (
            City_ID INT PRIMARY KEY IDENTITY,
            Name VARCHAR(100) NOT NULL
        )
    END
    """)

    # Provinces table
    cursor.execute("""
    IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'Provinces')
    BEGIN
        CREATE TABLE Provinces (
            Province_ID INT PRIMARY KEY IDENTITY,
            Name VARCHAR(100) NOT NULL
        )
    END
    """)

    conn.commit()
    print("Tables created successfully.")

def generate_otp():
    return str(random.randint(100000, 999999))

def register_umk():
    name = input("Enter UMK Name: ")
    description = input("Enter Description: ")
    logo = input("Enter Logo (as hex or binary): ").encode()  # Assuming binary input as string
    address = input("Enter Address: ")
    phone_num = input("Enter Phone Number: ")
    owner = input("Enter Owner Name: ")
    city = input("Enter City: ")
    province = input("Enter Province: ")

    otp = generate_otp()

    # Insert into Users table
    cursor.execute("""
    INSERT INTO Users (PhoneNum, OTP, Role)
    VALUES (?, ?, 'UMK')
    """, phone_num, otp)
    conn.commit()

    # Insert into UMK_Profiles table
    cursor.execute("""
    INSERT INTO UMK_Profiles (Name, Description, Logo, Address, PhoneNum, Owner, City, Province)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, name, description, logo, address, phone_num, owner, city, province)
    conn.commit()

    print("UMK registered successfully.")
    print(f"Your OTP is: {otp}")

def insert_product(umk_id, code, name, image, description, unit, price):
    cursor.execute("""
    INSERT INTO Products (UMK_ID, Code, Name, Image, Description, Unit, Price)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, umk_id, code, name, image, description, unit, price)
    conn.commit()

def insert_transaction(umk_id, type, amount, date, description):
    cursor.execute("""
    INSERT INTO Transactions (UMK_ID, Type, Amount, Date, Description)
    VALUES (?, ?, ?, ?, ?)
    """, umk_id, type, amount, date, description)
    conn.commit()

def soft_delete(table_name, id_column, id_value):
    soft_delete_sql = f"UPDATE {table_name} SET deleted_at = GETDATE() WHERE {id_column} = ?"
    cursor.execute(soft_delete_sql, id_value)
    conn.commit()
    print(f"Record soft deleted from table '{table_name}'.")

def login(phone_num):
    cursor.execute("SELECT User_ID, Role FROM Users WHERE PhoneNum = ? AND deleted_at IS NULL", phone_num)
    user = cursor.fetchone()
    if user:
        return user
    else:
        print("Invalid phone number or user not found.")
        return None

def admin_menu():
    while True:
        print("\nAdministrator Menu")
        print("1. Approve UMK Registration")
        print("2. View Registered UMKs")
        print("3. View Top-N Products")
        print("4. View Top-N UMKs by Sales")
        print("5. Log Out")

        choice = input("Enter your choice: ")

        if choice == '1':
            approve_umk_registration()
        elif choice == '2':
            view_registered_umks()
        elif choice == '3':
            view_top_n_products()
        elif choice == '4':
            view_top_n_umks()
        elif choice == '5':
            break
        else:
            print("Invalid choice. Please try again.")

def umk_menu(umk_id):
    while True:
        print("\nUMK Menu")
        print("1. Manage Profile")
        print("2. Manage Products")
        print("3. Record Transactions")
        print("4. View Financial Report")
        print("5. View Sales Report")
        print("6. Log Out")

        choice = input("Enter your choice: ")

        if choice == '1':
            manage_profile(umk_id)
        elif choice == '2':
            manage_products(umk_id)
        elif choice == '3':
            record_transactions(umk_id)
        elif choice == '4':
            view_financial_report(umk_id)
        elif choice == '5':
            view_sales_report(umk_id)
        elif choice == '6':
            break
        else:
            print("Invalid choice. Please try again.")

def approve_umk_registration():
    cursor.execute("SELECT * FROM UMK_Profiles WHERE deleted_at IS NULL")
    umks = cursor.fetchall()
    for umk in umks:
        print(umk)
    umk_id = int(input("Enter UMK_ID to approve: "))
    print(f"UMK_ID {umk_id} approved.")

def view_registered_umks():
    cursor.execute("SELECT * FROM UMK_Profiles WHERE deleted_at IS NULL")
    umks = cursor.fetchall()
    for umk in umks:
        print(umk)

def view_top_n_products():
    n = int(input("Enter the number of top products to view: "))
    cursor.execute("""
    SELECT TOP (?) p.Name, SUM(t.Amount) as TotalSales
    FROM Products p
    JOIN Transactions t ON p.UMK_ID = t.UMK_ID
    WHERE t.Type = 'income' AND t.deleted_at IS NULL
    GROUP BY p.Name
    ORDER BY TotalSales DESC
    """, n)
    products = cursor.fetchall()
    for product in products:
        print(product)

def view_top_n_umks():
    n = int(input("Enter the number of top UMKs to view: "))
    cursor.execute("""
    SELECT TOP (?) u.Name, SUM(t.Amount) as TotalSales
    FROM UMK_Profiles u
    JOIN Transactions t ON u.UMK_ID = t.UMK_ID
    WHERE t.Type = 'income' AND t.deleted_at IS NULL
    GROUP BY u.Name
    ORDER BY TotalSales DESC
    """, n)
    umks = cursor.fetchall()
    for umk in umks:
        print(umk)

def manage_profile(umk_id):
    print(f"Managing profile for UMK_ID {umk_id}")

def manage_products(umk_id):
    print(f"Managing products for UMK_ID {umk_id}")

def record_transactions(umk_id):
    print(f"Recording transactions for UMK_ID {umk_id}")

def view_financial_report(umk_id):
    print(f"Viewing financial report for UMK_ID {umk_id}")

def view_sales_report(umk_id):
    print(f"Viewing sales report for UMK_ID {umk_id}")

def display_main_menu():
    print("1. Log In")
    print("2. Register UMK")
    print("3. Exit")

def main():
    create_tables()

    while True:
        display_main_menu()
        choice = input("Enter your choice: ")
        
        if choice == '1':
            phone_num = input("Enter Phone Number: ")
            user = login(phone_num)
            if user:
                user_id, role = user
                if role == 'Administrator':
                    admin_menu()
                elif role == 'UMK':
                    cursor.execute("SELECT UMK_ID FROM UMK_Profiles WHERE PhoneNum = ? AND deleted_at IS NULL", phone_num)
                    umk = cursor.fetchone()
                    if umk:
                        umk_id = umk.UMK_ID
                        umk_menu(umk_id)
                    else:
                        print("UMK profile not found.")
        
        elif choice == '2':
            register_umk()
        
        elif choice == '3':
            print("Exiting...")
            break
        
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()

cursor.close()
conn.close()
