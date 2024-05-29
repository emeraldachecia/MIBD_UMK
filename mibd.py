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
    cursor.execute("""
    IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'Users')
    BEGIN
        CREATE TABLE Users (
            User_ID INT PRIMARY KEY IDENTITY,
            PhoneNum VARCHAR(12) NOT NULL UNIQUE,
            OTP VARCHAR(6),
            OTP_Created_At DATETIME,
            Role VARCHAR(50) NOT NULL,
            first_login_done BIT DEFAULT 0, -- Added first_login_done column
            deleted_at DATETIME
        )
    END
    """)

    # Update Users table to add OTP_Created_At and first_login_done columns if they don't exist
    cursor.execute("""
    IF NOT EXISTS (
        SELECT * 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_NAME = 'Users' 
        AND COLUMN_NAME = 'OTP_Created_At'
    )
    BEGIN
        ALTER TABLE Users
        ADD OTP_Created_At DATETIME
    END
    """)

    cursor.execute("""
    IF NOT EXISTS (
        SELECT * 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_NAME = 'Users' 
        AND COLUMN_NAME = 'first_login_done'
    )
    BEGIN
        ALTER TABLE Users
        ADD first_login_done BIT DEFAULT 0
    END
    """)

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
            Balance DECIMAL(30,2),
            approved BIT DEFAULT 0,
            deleted_at DATETIME
        )
    END
    """)

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

    cursor.execute("""
    IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'Cities')
    BEGIN
        CREATE TABLE Cities (
            City_ID INT PRIMARY KEY IDENTITY,
            Name VARCHAR(100) NOT NULL
        )
    END
    """)

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

def validate_phone_number(phone_num):
    return phone_num.isdigit()

def register_admin():
    phone_num = input("Enter Phone Number for Admin: ")
    if not validate_phone_number(phone_num):
        print("Invalid phone number. Please enter digits only.")
        return

    otp = generate_otp()
    otp_created_at = datetime.datetime.now()

    try:
        cursor.execute("""
        INSERT INTO Users (PhoneNum, OTP, OTP_Created_At, Role)
        VALUES (?, ?, ?, 'Administrator')
        """, (phone_num, otp, otp_created_at))
        conn.commit()
        print("Administrator registered successfully.")
        print(f"Your OTP is: {otp}")
    except Exception as e:
        conn.rollback()
        print(f"Error occurred: {e}")

def register_umk():
    name = input("Enter UMK Name: ")
    description = input("Enter Description: ")
    logo = input("Enter Logo (as hex or binary): ").encode()
    address = input("Enter Address: ")
    phone_num = input("Enter Phone Number: ")
    if not validate_phone_number(phone_num):
        print("Invalid phone number. Please enter digits only.")
        return

    owner = input("Enter Owner Name: ")
    city = input("Enter City: ")
    province = input("Enter Province: ")

    otp = generate_otp()
    otp_created_at = datetime.datetime.now()

    try:
        cursor.execute("""
        INSERT INTO Users (PhoneNum, OTP, OTP_Created_At, Role)
        VALUES (?, ?, ?, 'UMK')
        """, (phone_num, otp, otp_created_at))
        conn.commit()

        cursor.execute("""
        INSERT INTO UMK_Profiles (Name, Description, Logo, Address, PhoneNum, Owner, City, Province)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, description, logo, address, phone_num, owner, city, province))
        conn.commit()

        print("UMK registered successfully.")
        print(f"Your OTP is: {otp}")
    except Exception as e:
        conn.rollback()
        print(f"Error occurred: {e}")

def login_as_admin(phone_num):
    cursor.execute("SELECT User_ID, Role FROM Users WHERE PhoneNum = ? AND Role = 'Administrator' AND deleted_at IS NULL", (phone_num,))
    user = cursor.fetchone()
    if user:
        return user
    else:
        print("Invalid phone number or user not found.")
        return None

def login_with_otp(otp):
    cursor.execute("SELECT User_ID, Role, PhoneNum FROM Users WHERE OTP = ? AND deleted_at IS NULL", (otp,))
    user = cursor.fetchone()
    if user:
        otp_validity_period = datetime.timedelta(minutes=5)
        cursor.execute("SELECT OTP_Created_At FROM Users WHERE OTP = ? AND deleted_at IS NULL", (otp,))
        otp_created_at = cursor.fetchone()[0]
        if datetime.datetime.now() - otp_created_at <= otp_validity_period:
            cursor.execute("UPDATE Users SET OTP = NULL, OTP_Created_At = NULL, first_login_done = 1 WHERE OTP = ?", (otp,))
            conn.commit()
            return user
        else:
            print("OTP has expired.")
            return None
    else:
        print("Invalid OTP or user not found.")
        return None

def login_as_umk(phone_num):
    cursor.execute("SELECT User_ID, Role FROM Users WHERE PhoneNum = ? AND Role = 'UMK' AND first_login_done = 1 AND deleted_at IS NULL", (phone_num,))
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
        print("1. Manage Products")
        print("2. Record Transactions")
        print("3. View Financial Report")
        print("4. View Sales Report")
        print("5. Log Out")

        choice = input("Enter your choice: ")

        if choice == '1':
            manage_products(umk_id)
        elif choice == '2':
            record_transactions(umk_id)
        elif choice == '3':
            view_financial_report(umk_id)
        elif choice == '4':
            view_sales_report(umk_id)
        elif choice == '5':
            break
        else:
            print("Invalid choice. Please try again.")

def approve_umk_registration():
    print("\nUMK Approval Menu")
    print("1. View UMKs Pending Approval")
    print("2. View Approved UMKs")
    choice = input("Enter your choice: ")

    if choice == '1':
        cursor.execute("SELECT * FROM UMK_Profiles WHERE approved = 0 AND deleted_at IS NULL")
        umks = cursor.fetchall()
        if umks:
            print("UMKs Pending Approval:")
            for umk in umks:
                print(umk)
            umk_id = int(input("Enter UMK_ID to approve: "))
            cursor.execute("UPDATE UMK_Profiles SET approved = 1 WHERE UMK_ID = ?", (umk_id,))
            conn.commit()
            print(f"UMK_ID {umk_id} has been approved.")
        else:
            print("No UMKs pending approval.")
    elif choice == '2':
        cursor.execute("SELECT * FROM UMK_Profiles WHERE approved = 1 AND deleted_at IS NULL")
        umks = cursor.fetchall()
        if umks:
            print("Approved UMKs:")
            for umk in umks:
                print(umk)
        else:
            print("No UMKs have been approved yet.")
    else:
        print("Invalid choice. Please try again.")

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
    """, (n,))
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
    """, (n,))
    umks = cursor.fetchall()
    for umk in umks:
        print(umk)

def manage_products(umk_id):
    while True:
        print("\nManage Products Menu")
        print("1. Add Product")
        print("2. View Products")
        print("3. Update Product")
        print("4. Delete Product")
        print("5. Back to UMK Menu")

        choice = input("Enter your choice: ")

        if choice == '1':
            add_product(umk_id)
        elif choice == '2':
            view_products(umk_id)
        elif choice == '3':
            update_product(umk_id)
        elif choice == '4':
            delete_product(umk_id)
        elif choice == '5':
            break
        else:
            print("Invalid choice. Please try again.")

def add_product(umk_id):
    code = input("Enter Product Code: ")
    name = input("Enter Product Name: ")
    image = input("Enter Image (as hex or binary): ").encode()
    description = input("Enter Description: ")
    unit = input("Enter Unit: ")
    price = float(input("Enter Price: "))

    try:
        cursor.execute("""
        INSERT INTO Products (UMK_ID, Code, Name, Image, Description, Unit, Price)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (umk_id, code, name, image, description, unit, price))
        conn.commit()
        print("Product added successfully.")
    except Exception as e:
        conn.rollback()
        print(f"Error occurred: {e}")

def view_products(umk_id):
    cursor.execute("SELECT * FROM Products WHERE UMK_ID = ? AND deleted_at IS NULL", (umk_id,))
    products = cursor.fetchall()
    for product in products:
        print(product)

def update_product(umk_id):
    product_id = int(input("Enter Product ID to update: "))

    cursor.execute("SELECT * FROM Products WHERE Product_ID = ? AND UMK_ID = ? AND deleted_at IS NULL", (product_id, umk_id))
    product = cursor.fetchone()
    if not product:
        print("Product not found.")
        return

    print("Current product details:")
    print(f"Code: {product.Code}")
    print(f"Name: {product.Name}")
    print(f"Description: {product.Description}")
    print(f"Unit: {product.Unit}")
    print(f"Price: {product.Price}")

    code = input("Enter new Product Code (leave blank to keep current): ") or product.Code
    name = input("Enter new Product Name (leave blank to keep current): ") or product.Name
    image = input("Enter new Image (as hex or binary, leave blank to keep current): ").encode() or product.Image
    description = input("Enter new Description (leave blank to keep current): ") or product.Description
    unit = input("Enter new Unit (leave blank to keep current): ") or product.Unit
    price = input("Enter new Price (leave blank to keep current): ")
    price = float(price) if price else product.Price

    confirm = input(f"Are you sure you want to update product ID {product_id}? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("Update cancelled.")
        return

    try:
        cursor.execute("""
        UPDATE Products
        SET Code = ?, Name = ?, Image = ?, Description = ?, Unit = ?, Price = ?
        WHERE Product_ID = ? AND UMK_ID = ?
        """, (code, name, image, description, unit, price, product_id, umk_id))
        conn.commit()
        print("Product updated successfully.")
    except Exception as e:
        conn.rollback()
        print(f"Error occurred: {e}")

def delete_product(umk_id):
    product_id = int(input("Enter Product ID to delete: "))

    cursor.execute("SELECT * FROM Products WHERE Product_ID = ? AND UMK_ID = ? AND deleted_at IS NULL", (product_id, umk_id))
    product = cursor.fetchone()
    if not product:
        print("Product not found.")
        return

    confirm = input(f"Are you sure you want to delete product ID {product_id}? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("Delete cancelled.")
        return

    try:
        cursor.execute("UPDATE Products SET deleted_at = ? WHERE Product_ID = ? AND UMK_ID = ?", (datetime.datetime.now(), product_id, umk_id))
        conn.commit()
        print("Product deleted successfully.")
    except Exception as e:
        conn.rollback()
        print(f"Error occurred: {e}")

def record_transactions(umk_id):
    print(f"Recording transactions for UMK_ID {umk_id}")

def view_financial_report(umk_id):
    print(f"Viewing financial report for UMK_ID {umk_id}")

def view_sales_report(umk_id):
    print(f"Viewing sales report for UMK_ID {umk_id}")

def display_main_menu():
    print("1. Log In as Admin")
    print("2. Log In as UMK with OTP")
    print("3. Log In as UMK with Phone Number")
    print("4. Register UMK")
    print("5. Register Admin")
    print("6. Exit")

def main():
    create_tables()

    while True:
        display_main_menu()
        choice = input("Enter your choice: ")
        
        if choice == '1':
            phone_num = input("Enter Admin Phone Number: ")
            user = login_as_admin(phone_num)
            if user:
                admin_menu()
        
        elif choice == '2':
            otp = input("Enter OTP: ")
            user = login_with_otp(otp)
            if user:
                user_id, role, phone_num = user
                if role == 'UMK':
                    cursor.execute("SELECT UMK_ID FROM UMK_Profiles WHERE PhoneNum = ? AND deleted_at IS NULL", (phone_num,))
                    umk = cursor.fetchone()
                    if umk:
                        umk_id = umk.UMK_ID
                        umk_menu(umk_id)
                    else:
                        print("UMK profile not found.")
        
        elif choice == '3':
            phone_num = input("Enter UMK Phone Number: ")
            user = login_as_umk(phone_num)
            if user:
                cursor.execute("SELECT UMK_ID FROM UMK_Profiles WHERE PhoneNum = ? AND deleted_at IS NULL", (phone_num,))
                umk = cursor.fetchone()
                if umk:
                    umk_id = umk.UMK_ID
                    umk_menu(umk_id)
                else:
                    print("UMK profile not found.")
        
        elif choice == '4':
            register_umk()
        
        elif choice == '5':
            register_admin()

        elif choice == '6':
            print("Exiting...")
            break
        
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()

cursor.close()
conn.close()
