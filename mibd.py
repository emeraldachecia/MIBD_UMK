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
            first_login_done BIT DEFAULT 0,
            deleted_at DATETIME
        )
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
            Product_ID INT,
            deleted_at DATETIME,
            FOREIGN KEY (UMK_ID) REFERENCES UMK_Profiles(UMK_ID),
            FOREIGN KEY (Product_ID) REFERENCES Products(Product_ID)
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
    print("Tabel berhasil dibuat.")

def generate_otp():
    return str(random.randint(100000, 999999))

def validate_phone_number(phone_num):
    return phone_num.isdigit()

def register_admin():
    phone_num = input("Masukkan Nomor Telepon untuk Admin: ")
    if not validate_phone_number(phone_num):
        print("Nomor telepon tidak valid. Harap masukkan angka saja.")
        return

    otp = generate_otp()
    otp_created_at = datetime.datetime.now()

    try:
        cursor.execute("""
        INSERT INTO Users (PhoneNum, OTP, OTP_Created_At, Role)
        VALUES (?, ?, ?, 'Administrator')
        """, (phone_num, otp, otp_created_at))
        conn.commit()
        print("Admin berhasil didaftarkan.")
        print(f"OTP Anda adalah: {otp}")
    except Exception as e:
        conn.rollback()
        print(f"Terjadi kesalahan: {e}")

def register_umk():
    name = input("Masukkan Nama UMK: ")
    description = input("Masukkan Deskripsi: ")
    logo = input("Masukkan Logo (sebagai hex atau biner): ").encode()
    address = input("Masukkan Alamat: ")
    phone_num = input("Masukkan Nomor Telepon: ")
    if not validate_phone_number(phone_num):
        print("Nomor telepon tidak valid. Harap masukkan angka saja.")
        return

    owner = input("Masukkan Nama Pemilik: ")
    city = input("Masukkan Kota: ")
    province = input("Masukkan Provinsi: ")

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

        print("UMK berhasil didaftarkan.")
        print(f"OTP Anda adalah: {otp}")
    except Exception as e:
        conn.rollback()
        print(f"Terjadi kesalahan: {e}")

def login_as_admin(phone_num):
    cursor.execute("SELECT User_ID, Role FROM Users WHERE PhoneNum = ? AND Role = 'Administrator' AND deleted_at IS NULL", (phone_num,))
    user = cursor.fetchone()
    if user:
        return user
    else:
        print("Nomor telepon tidak valid atau pengguna tidak ditemukan.")
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
            print("OTP telah kadaluarsa.")
            return None
    else:
        print("OTP tidak valid atau pengguna tidak ditemukan.")
        return None

def login_as_umk(phone_num):
    cursor.execute("SELECT User_ID, Role FROM Users WHERE PhoneNum = ? AND Role = 'UMK' AND first_login_done = 1 AND deleted_at IS NULL", (phone_num,))
    user = cursor.fetchone()
    if user:
        return user
    else:
        print("Nomor telepon tidak valid atau pengguna tidak ditemukan.")
        return None

def admin_menu():
    while True:
        print("\nMenu Administrator")
        print("1. Setujui Pendaftaran UMK")
        print("2. Lihat UMK Terdaftar")
        print("3. Lihat Produk Teratas")
        print("4. Lihat UMK Teratas Berdasarkan Penjualan")
        print("5. Keluar")

        choice = input("Masukkan pilihan Anda: ")

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
            print("Pilihan tidak valid. Silakan coba lagi.")

def umk_menu(umk_id):
    while True:
        print("\nMenu UMK")
        print("1. Kelola Produk")
        print("2. Catat Transaksi")
        print("3. Lihat Laporan Keuangan")
        print("4. Lihat Laporan Penjualan")
        print("5. Keluar")

        choice = input("Masukkan pilihan Anda: ")

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
            print("Pilihan tidak valid. Silakan coba lagi.")

def approve_umk_registration():
    print("\nMenu Persetujuan UMK")
    print("1. Lihat UMK yang Menunggu Persetujuan")
    print("2. Lihat UMK yang Disetujui")
    choice = input("Masukkan pilihan Anda: ")

    if choice == '1':
        cursor.execute("SELECT * FROM UMK_Profiles WHERE approved = 0 AND deleted_at IS NULL")
        umks = cursor.fetchall()
        if umks:
            print("UMK yang Menunggu Persetujuan:")
            for umk in umks:
                print(umk)
            umk_id = int(input("Masukkan UMK_ID untuk disetujui: "))
            cursor.execute("UPDATE UMK_Profiles SET approved = 1 WHERE UMK_ID = ?", (umk_id,))
            conn.commit()
            print(f"UMK_ID {umk_id} telah disetujui.")
        else:
            print("Tidak ada UMK yang menunggu persetujuan.")
    elif choice == '2':
        cursor.execute("SELECT * FROM UMK_Profiles WHERE approved = 1 AND deleted_at IS NULL")
        umks = cursor.fetchall()
        if umks:
            print("UMK yang Disetujui:")
            for umk in umks:
                print(umk)
        else:
            print("Tidak ada UMK yang disetujui.")
    else:
        print("Pilihan tidak valid. Silakan coba lagi.")

def view_registered_umks():
    cursor.execute("SELECT * FROM UMK_Profiles WHERE deleted_at IS NULL")
    umks = cursor.fetchall()
    for umk in umks:
        print(umk)

def view_top_n_products():
    n = int(input("Masukkan jumlah produk teratas yang ingin dilihat: "))
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
    n = int(input("Masukkan jumlah UMK teratas yang ingin dilihat: "))
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
        print("\nMenu Kelola Produk")
        print("1. Tambah Produk")
        print("2. Lihat Produk")
        print("3. Perbarui Produk")
        print("4. Hapus Produk")
        print("5. Kembali ke Menu UMK")

        choice = input("Masukkan pilihan Anda: ")

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
            print("Pilihan tidak valid. Silakan coba lagi.")

def add_product(umk_id):
    code = input("Masukkan Kode Produk: ")
    name = input("Masukkan Nama Produk: ")
    image = input("Masukkan Gambar (sebagai hex atau biner): ").encode()
    description = input("Masukkan Deskripsi: ")
    unit = input("Masukkan Satuan: ")
    price = float(input("Masukkan Harga: "))

    try:
        cursor.execute("""
        INSERT INTO Products (UMK_ID, Code, Name, Image, Description, Unit, Price)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (umk_id, code, name, image, description, unit, price))
        conn.commit()
        print("Produk berhasil ditambahkan.")
    except Exception as e:
        conn.rollback()
        print(f"Terjadi kesalahan: {e}")

def view_products(umk_id):
    cursor.execute("SELECT * FROM Products WHERE UMK_ID = ? AND deleted_at IS NULL", (umk_id,))
    products = cursor.fetchall()
    for product in products:
        print(product)

def update_product(umk_id):
    product_id = int(input("Masukkan ID Produk yang ingin diperbarui: "))

    cursor.execute("SELECT * FROM Products WHERE Product_ID = ? AND UMK_ID = ? AND deleted_at IS NULL", (product_id, umk_id))
    product = cursor.fetchone()
    if not product:
        print("Produk tidak ditemukan.")
        return

    print("Detail produk saat ini:")
    print(f"Kode: {product.Code}")
    print(f"Nama: {product.Name}")
    print(f"Deskripsi: {product.Description}")
    print(f"Satuan: {product.Unit}")
    print(f"Harga: {product.Price}")

    code = input("Masukkan Kode Produk baru (Kosongkan kalau tidak ingin mengubah apapun): ") or product.Code
    name = input("Masukkan Nama Produk baru (Kosongkan kalau tidak ingin mengubah apapun): ") or product.Name
    image = input("Masukkan Gambar baru (sebagai hex atau biner, Kosongkan kalau tidak ingin mengubah apapun): ").encode() or product.Image
    description = input("Masukkan Deskripsi baru (Kosongkan kalau tidak ingin mengubah apapun): ") or product.Description
    unit = input("Masukkan Satuan baru (Kosongkan kalau tidak ingin mengubah apapun): ") or product.Unit
    price = input("Masukkan Harga baru (Kosongkan kalau tidak ingin mengubah apapun): ")
    price = float(price) if price else product.Price

    confirm = input(f"Apakah Anda yakin ingin memperbarui produk dengan ID {product_id}? (ya/tidak): ").strip().lower()
    if confirm != 'ya':
        print("Pembaruan dibatalkan.")
        return

    try:
        cursor.execute("""
        UPDATE Products
        SET Code = ?, Name = ?, Image = ?, Description = ?, Unit = ?, Price = ?
        WHERE Product_ID = ? AND UMK_ID = ?
        """, (code, name, image, description, unit, price, product_id, umk_id))
        conn.commit()
        print("Produk berhasil diperbarui.")
    except Exception as e:
        conn.rollback()
        print(f"Terjadi kesalahan: {e}")

def delete_product(umk_id):
    product_id = int(input("Masukkan ID Produk yang ingin dihapus: "))

    cursor.execute("SELECT * FROM Products WHERE Product_ID = ? AND UMK_ID = ? AND deleted_at IS NULL", (product_id, umk_id))
    product = cursor.fetchone()
    if not product:
        print("Produk tidak ditemukan.")
        return

    confirm = input(f"Apakah Anda yakin ingin menghapus produk dengan ID {product_id}? (ya/tidak): ").strip().lower()
    if confirm != 'ya':
        print("Penghapusan dibatalkan.")
        return

    try:
        cursor.execute("UPDATE Products SET deleted_at = ? WHERE Product_ID = ? AND UMK_ID = ?", (datetime.datetime.now(), product_id, umk_id))
        conn.commit()
        print("Produk berhasil dihapus.")
    except Exception as e:
        conn.rollback()
        print(f"Terjadi kesalahan: {e}")

def record_transactions(umk_id):
    while True:
        print("\nMenu Catat Transaksi")
        print("1. Catat Pemasukan")
        print("2. Catat Pengeluaran")
        print("3. Kembali ke Menu UMK")

        choice = input("Masukkan pilihan Anda: ")

        if choice == '1':
            record_income(umk_id)
        elif choice == '2':
            record_expense(umk_id)
        elif choice == '3':
            break
        else:
            print("Pilihan tidak valid. Silakan coba lagi.")

def record_income(umk_id):
    print("\nCatat Pemasukan")
    print("1. Setor Modal")
    print("2. Penjualan Produk")
    choice = input("Masukkan jenis pemasukan: ")

    if choice == '1':
        income_type = 'Setor Modal'
        product_id = None
    elif choice == '2':
        income_type = 'Penjualan Produk'
        product_id = select_product(umk_id)
        if not product_id:
            print("Tidak ada produk yang tersedia atau pilihan tidak valid. Kembali ke Menu Catat Transaksi.")
            return
    else:
        print("Pilihan tidak valid. Kembali ke Menu Catat Transaksi.")
        return

    amount = float(input("Masukkan jumlah: "))
    description = input("Masukkan deskripsi: ")

    try:
        cursor.execute("""
        INSERT INTO Transactions (UMK_ID, Type, Amount, Date, Description, Product_ID)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (umk_id, income_type, amount, datetime.datetime.now(), description, product_id))
        conn.commit()
        print("Pemasukan berhasil dicatat.")
    except Exception as e:
        conn.rollback()
        print(f"Terjadi kesalahan: {e}")

def record_expense(umk_id):
    print("\nCatat Pengeluaran")
    print("1. Pengeluaran Operasional")
    print("2. Penarikan Modal/Keuntungan")
    choice = input("Masukkan jenis pengeluaran: ")

    if choice == '1':
        expense_type = 'Pengeluaran Operasional'
    elif choice == '2':
        expense_type = 'Penarikan Modal/Keuntungan'
    else:
        print("Pilihan tidak valid. Kembali ke Menu Catat Transaksi.")
        return

    amount = float(input("Masukkan jumlah: "))
    description = input("Masukkan deskripsi: ")

    try:
        cursor.execute("""
        INSERT INTO Transactions (UMK_ID, Type, Amount, Date, Description)
        VALUES (?, ?, ?, ?, ?)
        """, (umk_id, expense_type, amount, datetime.datetime.now(), description))
        conn.commit()
        print("Pengeluaran berhasil dicatat.")
    except Exception as e:
        conn.rollback()
        print(f"Terjadi kesalahan: {e}")

def select_product(umk_id):
    cursor.execute("SELECT Product_ID, Name FROM Products WHERE UMK_ID = ? AND deleted_at IS NULL", (umk_id,))
    products = cursor.fetchall()
    if not products:
        return None

    print("Pilih produk:")
    for product in products:
        print(f"{product.Product_ID}: {product.Name}")
    
    product_id = int(input("Masukkan ID Produk: "))
    if any(product.Product_ID == product_id for product in products):
        return product_id
    else:
        return None

def view_financial_report(umk_id):
    print(f"Melihat laporan keuangan untuk UMK_ID {umk_id}")
    # Tambahkan kode untuk menghasilkan dan menampilkan laporan keuangan

def view_sales_report(umk_id):
    print(f"Melihat laporan penjualan untuk UMK_ID {umk_id}")
    # Tambahkan kode untuk menghasilkan dan menampilkan laporan penjualan

def display_main_menu():
    print("1. Masuk sebagai Admin")
    print("2. Masuk sebagai UMK dengan OTP")
    print("3. Masuk sebagai UMK dengan Nomor Telepon")
    print("4. Daftarkan UMK")
    print("5. Daftarkan Admin")
    print("6. Keluar")

def main():
    create_tables()

    while True:
        display_main_menu()
        choice = input("Masukkan pilihan Anda: ")
        
        if choice == '1':
            phone_num = input("Masukkan Nomor Telepon Admin: ")
            user = login_as_admin(phone_num)
            if user:
                admin_menu()
        
        elif choice == '2':
            otp = input("Masukkan OTP: ")
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
                        print("Profil UMK tidak ditemukan.")
        
        elif choice == '3':
            phone_num = input("Masukkan Nomor Telepon UMK: ")
            user = login_as_umk(phone_num)
            if user:
                cursor.execute("SELECT UMK_ID FROM UMK_Profiles WHERE PhoneNum = ? AND deleted_at IS NULL", (phone_num,))
                umk = cursor.fetchone()
                if umk:
                    umk_id = umk.UMK_ID
                    umk_menu(umk_id)
                else:
                    print("Profil UMK tidak ditemukan.")
        
        elif choice == '4':
            register_umk()
        
        elif choice == '5':
            register_admin()

        elif choice == '6':
            print("Keluar...")
            break
        
        else:
            print("Pilihan tidak valid. Silakan coba lagi.")

if __name__ == "__main__":
    main()

cursor.close()
conn.close()
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
            first_login_done BIT DEFAULT 0,
            deleted_at DATETIME
        )
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
            Product_ID INT,
            deleted_at DATETIME,
            FOREIGN KEY (UMK_ID) REFERENCES UMK_Profiles(UMK_ID),
            FOREIGN KEY (Product_ID) REFERENCES Products(Product_ID)
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
    print("Tabel berhasil dibuat.")

def generate_otp():
    return str(random.randint(100000, 999999))

def validate_phone_number(phone_num):
    return phone_num.isdigit()

def register_admin():
    phone_num = input("Masukkan Nomor Telepon untuk Admin: ")
    if not validate_phone_number(phone_num):
        print("Nomor telepon tidak valid. Harap masukkan angka saja.")
        return

    otp = generate_otp()
    otp_created_at = datetime.datetime.now()

    try:
        cursor.execute("""
        INSERT INTO Users (PhoneNum, OTP, OTP_Created_At, Role)
        VALUES (?, ?, ?, 'Administrator')
        """, (phone_num, otp, otp_created_at))
        conn.commit()
        print("Admin berhasil didaftarkan.")
        print(f"OTP Anda adalah: {otp}")
    except Exception as e:
        conn.rollback()
        print(f"Terjadi kesalahan: {e}")

def register_umk():
    name = input("Masukkan Nama UMK: ")
    description = input("Masukkan Deskripsi: ")
    logo = input("Masukkan Logo (sebagai hex atau biner): ").encode()
    address = input("Masukkan Alamat: ")
    phone_num = input("Masukkan Nomor Telepon: ")
    if not validate_phone_number(phone_num):
        print("Nomor telepon tidak valid. Harap masukkan angka saja.")
        return

    owner = input("Masukkan Nama Pemilik: ")
    city = input("Masukkan Kota: ")
    province = input("Masukkan Provinsi: ")

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

        print("UMK berhasil didaftarkan.")
        print(f"OTP Anda adalah: {otp}")
    except Exception as e:
        conn.rollback()
        print(f"Terjadi kesalahan: {e}")

def login_as_admin(phone_num):
    cursor.execute("SELECT User_ID, Role FROM Users WHERE PhoneNum = ? AND Role = 'Administrator' AND deleted_at IS NULL", (phone_num,))
    user = cursor.fetchone()
    if user:
        return user
    else:
        print("Nomor telepon tidak valid atau pengguna tidak ditemukan.")
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
            print("OTP telah kadaluarsa.")
            return None
    else:
        print("OTP tidak valid atau pengguna tidak ditemukan.")
        return None

def login_as_umk(phone_num):
    cursor.execute("SELECT User_ID, Role FROM Users WHERE PhoneNum = ? AND Role = 'UMK' AND first_login_done = 1 AND deleted_at IS NULL", (phone_num,))
    user = cursor.fetchone()
    if user:
        return user
    else:
        print("Nomor telepon tidak valid atau pengguna tidak ditemukan.")
        return None

def admin_menu():
    while True:
        print("\nMenu Administrator")
        print("1. Approve Pendaftaran UMK")
        print("2. Lihat UMK Terdaftar")
        print("3. Lihat Produk Teratas")
        print("4. Lihat UMK Teratas Berdasarkan Penjualan")
        print("5. Keluar")

        choice = input("Masukkan pilihan Anda: ")

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
            print("Pilihan tidak valid. Silakan coba lagi.")

def umk_menu(umk_id):
    while True:
        print("\nMenu UMK")
        print("1. Kelola Produk")
        print("2. Catat Transaksi")
        print("3. Lihat Laporan Keuangan")
        print("4. Lihat Laporan Penjualan")
        print("5. Keluar")

        choice = input("Masukkan pilihan Anda: ")

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
            print("Pilihan tidak valid. Silakan coba lagi.")

def approve_umk_registration():
    print("\nMenu Persetujuan UMK")
    print("1. Lihat UMK yang Menunggu Persetujuan")
    print("2. Lihat UMK yang telah disetujui")
    choice = input("Masukkan pilihan Anda: ")

    if choice == '1':
        cursor.execute("SELECT * FROM UMK_Profiles WHERE approved = 0 AND deleted_at IS NULL")
        umks = cursor.fetchall()
        if umks:
            print("UMK yang Menunggu Persetujuan:")
            for umk in umks:
                print(umk)
            umk_id = int(input("Masukkan UMK_ID untuk disetujui: "))
            cursor.execute("UPDATE UMK_Profiles SET approved = 1 WHERE UMK_ID = ?", (umk_id,))
            conn.commit()
            print(f"UMK_ID {umk_id} telah disetujui.")
        else:
            print("Tidak ada UMK yang menunggu persetujuan.")
    elif choice == '2':
        cursor.execute("SELECT * FROM UMK_Profiles WHERE approved = 1 AND deleted_at IS NULL")
        umks = cursor.fetchall()
        if umks:
            print("UMK yang Disetujui:")
            for umk in umks:
                print(umk)
        else:
            print("Tidak ada UMK yang disetujui.")
    else:
        print("Pilihan tidak valid. Silakan coba lagi.")

def view_registered_umks():
    cursor.execute("SELECT * FROM UMK_Profiles WHERE deleted_at IS NULL")
    umks = cursor.fetchall()
    for umk in umks:
        print(umk)

def view_top_n_products():
    n = int(input("Masukkan jumlah produk teratas yang ingin dilihat: "))
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
    n = int(input("Masukkan jumlah UMK teratas yang ingin dilihat: "))
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
        print("\nMenu Kelola Produk")
        print("1. Tambah Produk")
        print("2. Lihat Produk")
        print("3. Perbarui Produk")
        print("4. Hapus Produk")
        print("5. Kembali ke Menu UMK")

        choice = input("Masukkan pilihan Anda: ")

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
            print("Pilihan tidak valid. Silakan coba lagi.")

def add_product(umk_id):
    code = input("Masukkan Kode Produk: ")
    name = input("Masukkan Nama Produk: ")
    image = input("Masukkan Gambar (sebagai hex atau biner): ").encode()
    description = input("Masukkan Deskripsi: ")
    unit = input("Masukkan Satuan: ")
    price = float(input("Masukkan Harga: "))

    try:
        cursor.execute("""
        INSERT INTO Products (UMK_ID, Code, Name, Image, Description, Unit, Price)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (umk_id, code, name, image, description, unit, price))
        conn.commit()
        print("Produk berhasil ditambahkan.")
    except Exception as e:
        conn.rollback()
        print(f"Terjadi kesalahan: {e}")

def view_products(umk_id):
    cursor.execute("SELECT * FROM Products WHERE UMK_ID = ? AND deleted_at IS NULL", (umk_id,))
    products = cursor.fetchall()
    for product in products:
        print(product)

def update_product(umk_id):
    product_id = int(input("Masukkan ID Produk yang ingin diperbarui: "))

    cursor.execute("SELECT * FROM Products WHERE Product_ID = ? AND UMK_ID = ? AND deleted_at IS NULL", (product_id, umk_id))
    product = cursor.fetchone()
    if not product:
        print("Produk tidak ditemukan.")
        return

    print("Detail produk saat ini:")
    print(f"Kode: {product.Code}")
    print(f"Nama: {product.Name}")
    print(f"Deskripsi: {product.Description}")
    print(f"Satuan: {product.Unit}")
    print(f"Harga: {product.Price}")

    code = input("Masukkan Kode Produk baru (Kosongkan kalau tidak ingin mengubah apapun): ") or product.Code
    name = input("Masukkan Nama Produk baru (Kosongkan kalau tidak ingin mengubah apapun): ") or product.Name
    image = input("Masukkan Gambar baru (sebagai hex atau biner, Kosongkan kalau tidak ingin mengubah apapun): ").encode() or product.Image
    description = input("Masukkan Deskripsi baru (Kosongkan kalau tidak ingin mengubah apapun): ") or product.Description
    unit = input("Masukkan Satuan baru (Kosongkan kalau tidak ingin mengubah apapun): ") or product.Unit
    price = input("Masukkan Harga baru (Kosongkan kalau tidak ingin mengubah apapun): ")
    price = float(price) if price else product.Price

    confirm = input(f"Apakah Anda yakin ingin memperbarui produk dengan ID {product_id}? (yes/no): ").strip().lower()
    if confirm not in ['yes', 'y']:
        print("Pembaruan dibatalkan.")
        return

    try:
        cursor.execute("""
        UPDATE Products
        SET Code = ?, Name = ?, Image = ?, Description = ?, Unit = ?, Price = ?
        WHERE Product_ID = ? AND UMK_ID = ?
        """, (code, name, image, description, unit, price, product_id, umk_id))
        conn.commit()
        print("Produk berhasil diperbarui.")
    except Exception as e:
        conn.rollback()
        print(f"Terjadi kesalahan: {e}")

def delete_product(umk_id):
    product_id = int(input("Masukkan ID Produk yang ingin dihapus: "))

    cursor.execute("SELECT * FROM Products WHERE Product_ID = ? AND UMK_ID = ? AND deleted_at IS NULL", (product_id, umk_id))
    product = cursor.fetchone()
    if not product:
        print("Produk tidak ditemukan.")
        return

    confirm = input(f"Apakah Anda yakin ingin menghapus produk dengan ID {product_id}? (yes/no): ").strip().lower()
    if confirm not in ['yes', 'y']:
        print("Penghapusan dibatalkan.")
        return

    try:
        cursor.execute("UPDATE Products SET deleted_at = ? WHERE Product_ID = ? AND UMK_ID = ?", (datetime.datetime.now(), product_id, umk_id))
        conn.commit()
        print("Produk berhasil dihapus.")
    except Exception as e:
        conn.rollback()
        print(f"Terjadi kesalahan: {e}")

def record_transactions(umk_id):
    while True:
        print("\nMenu Catat Transaksi")
        print("1. Catat Pemasukan")
        print("2. Catat Pengeluaran")
        print("3. Kembali ke Menu UMK")

        choice = input("Masukkan pilihan Anda: ")

        if choice == '1':
            record_income(umk_id)
        elif choice == '2':
            record_expense(umk_id)
        elif choice == '3':
            break
        else:
            print("Pilihan tidak valid. Silakan coba lagi.")

def record_income(umk_id):
    print("\nCatat Pemasukan")
    print("1. Setor Modal")
    print("2. Penjualan Produk")
    choice = input("Masukkan jenis pemasukan: ")

    if choice == '1':
        income_type = 'Setor Modal'
        product_id = None
    elif choice == '2':
        income_type = 'Penjualan Produk'
        product_id = select_product(umk_id)
        if not product_id:
            print("Tidak ada produk yang tersedia atau pilihan tidak valid. Kembali ke Menu Catat Transaksi.")
            return
    else:
        print("Pilihan tidak valid. Kembali ke Menu Catat Transaksi.")
        return

    amount = float(input("Masukkan jumlah: "))
    description = input("Masukkan deskripsi: ")

    try:
        cursor.execute("""
        INSERT INTO Transactions (UMK_ID, Type, Amount, Date, Description, Product_ID)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (umk_id, income_type, amount, datetime.datetime.now(), description, product_id))
        conn.commit()
        print("Pemasukan berhasil dicatat.")
    except Exception as e:
        conn.rollback()
        print(f"Terjadi kesalahan: {e}")

def record_expense(umk_id):
    print("\nCatat Pengeluaran")
    print("1. Pengeluaran Operasional")
    print("2. Penarikan Modal/Keuntungan")
    choice = input("Masukkan jenis pengeluaran: ")

    if choice == '1':
        expense_type = 'Pengeluaran Operasional'
    elif choice == '2':
        expense_type = 'Penarikan Modal/Keuntungan'
    else:
        print("Pilihan tidak valid. Kembali ke Menu Catat Transaksi.")
        return

    amount = float(input("Masukkan jumlah: "))
    description = input("Masukkan deskripsi: ")

    try:
        cursor.execute("""
        INSERT INTO Transactions (UMK_ID, Type, Amount, Date, Description)
        VALUES (?, ?, ?, ?, ?)
        """, (umk_id, expense_type, amount, datetime.datetime.now(), description))
        conn.commit()
        print("Pengeluaran berhasil dicatat.")
    except Exception as e:
        conn.rollback()
        print(f"Terjadi kesalahan: {e}")

def select_product(umk_id):
    cursor.execute("SELECT Product_ID, Name FROM Products WHERE UMK_ID = ? AND deleted_at IS NULL", (umk_id,))
    products = cursor.fetchall()
    if not products:
        return None

    print("Pilih produk:")
    for product in products:
        print(f"{product.Product_ID}: {product.Name}")
    
    product_id = int(input("Masukkan ID Produk: "))
    if any(product.Product_ID == product_id for product in products):
        return product_id
    else:
        return None

def view_financial_report(umk_id):
    print(f"Melihat laporan keuangan untuk UMK_ID {umk_id}")
    # kode untuk menghasilkan dan menampilkan laporan keuangan

def view_sales_report(umk_id):
    print(f"Melihat laporan penjualan untuk UMK_ID {umk_id}")
    # kode untuk menghasilkan dan menampilkan laporan penjualan

def display_main_menu():
    print("1. Masuk sebagai Admin")
    print("2. Masuk sebagai UMK dengan OTP")
    print("3. Masuk sebagai UMK dengan Nomor Telepon")
    print("4. Daftarkan UMK")
    print("5. Daftarkan Admin")
    print("6. Keluar")

def main():
    create_tables()

    while True:
        display_main_menu()
        choice = input("Masukkan pilihan Anda: ")
        
        if choice == '1':
            phone_num = input("Masukkan Nomor Telepon Admin: ")
            user = login_as_admin(phone_num)
            if user:
                admin_menu()
        
        elif choice == '2':
            otp = input("Masukkan OTP: ")
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
                        print("Profil UMK tidak ditemukan.")
        
        elif choice == '3':
            phone_num = input("Masukkan Nomor Telepon UMK: ")
            user = login_as_umk(phone_num)
            if user:
                cursor.execute("SELECT UMK_ID FROM UMK_Profiles WHERE PhoneNum = ? AND deleted_at IS NULL", (phone_num,))
                umk = cursor.fetchone()
                if umk:
                    umk_id = umk.UMK_ID
                    umk_menu(umk_id)
                else:
                    print("Profil UMK tidak ditemukan.")
        
        elif choice == '4':
            register_umk()
        
        elif choice == '5':
            register_admin()

        elif choice == '6':
            print("Keluar...")
            break
        
        else:
            print("Pilihan tidak valid. Silakan coba lagi.")

if __name__ == "__main__":
    main()

cursor.close()
conn.close()
