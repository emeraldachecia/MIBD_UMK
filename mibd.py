import pyodbc as odbc
import datetime
import random

# Informasi koneksi ke database SQL Server
DRIVER_NAME = 'SQL SERVER'
SERVER_NAME = r'Rey-PC\SQLEXPRESS'
DATABASE_NAME = 'students'

# Membuat string koneksi
connection_string = f"""
    DRIVER={{{DRIVER_NAME}}};
    SERVER={SERVER_NAME};
    DATABASE={DATABASE_NAME};
    Trusted_Connection=yes;
"""

# Membuka koneksi ke database
conn = odbc.connect(connection_string)
cursor = conn.cursor()

# Fungsi untuk membuat tabel-tabel yang dibutuhkan
def create_tables():
    # Membuat tabel Users
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

    # Membuat tabel UMK_Profiles
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

    # Membuat tabel Products
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

    # Membuat tabel Transactions
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

    # Membuat tabel Kota
    cursor.execute("""
    IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'Cities')
    BEGIN
        CREATE TABLE Cities (
            City_ID INT PRIMARY KEY IDENTITY,
            Name VARCHAR(100) NOT NULL
        )
    END
    """)

    # Membuat tabel Provinsi
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
    

# Fungsi untuk memasukkan data dummy ke tabel Products dan Transactions
def insert_dummy_data():
    # Data dummy untuk tabel Products
    products = [
        (1, 'P001', 'Electric Kettle', None, '1.7L capacity electric kettle', 'Unit 1', 100.00, None),
        (1, 'P002', 'Wireless Mouse', None, 'Ergonomic wireless mouse', 'Unit 2', 200.00, None),
        (2, 'P003', 'Bluetooth Speaker', None, 'Portable Bluetooth speaker', 'Unit 3', 300.00, None),
        (2, 'P004', 'Smartphone Holder', None, 'Adjustable smartphone holder', 'Unit 4', 400.00, None),
        (3, 'P005', 'LED Desk Lamp', None, 'Dimmable LED desk lamp', 'Unit 5', 500.00, None),
        (3, 'P006', 'USB Hub', None, '4-port USB 3.0 hub', 'Unit 6', 600.00, None),
        (4, 'P007', 'Wireless Charger', None, 'Fast wireless charger pad', 'Unit 7', 700.00, None),
        (4, 'P008', 'Fitness Tracker', None, 'Waterproof fitness tracker', 'Unit 8', 800.00, None),
        (5, 'P009', 'Portable Power Bank', None, '10000mAh power bank', 'Unit 9', 900.00, None),
        (5, 'P010', 'Electric Toothbrush', None, 'Rechargeable electric toothbrush', 'Unit 10', 1000.00, None),
        (6, 'P011', 'Smart Home Camera', None, '1080p smart home security camera', 'Unit 11', 1100.00, None),
        (6, 'P012', 'Laptop Cooling Pad', None, 'Adjustable laptop cooling pad', 'Unit 12', 1200.00, None),
        (7, 'P013', 'Noise Cancelling Headphones', None, 'Over-ear noise cancelling headphones', 'Unit 13', 1300.00, None),
        (7, 'P014', 'Portable Hard Drive', None, '1TB portable external hard drive', 'Unit 14', 1400.00, None),
        (8, 'P015', 'Smart Light Bulb', None, 'Color-changing smart light bulb', 'Unit 15', 1500.00, None),
        (8, 'P016', 'Air Fryer', None, 'Digital air fryer with touchscreen', 'Unit 16', 1600.00, None),
        (9, 'P017', 'Electric Shaver', None, 'Cordless electric shaver', 'Unit 17', 1700.00, None),
        (9, 'P018', 'Bluetooth Headset', None, 'In-ear Bluetooth headset', 'Unit 18', 1800.00, None),
        (10, 'P019', 'Smart Thermostat', None, 'Wi-Fi smart thermostat', 'Unit 19', 1900.00, None),
        (10, 'P020', 'Robot Vacuum', None, 'Smart robot vacuum cleaner', 'Unit 20', 2000.00, None),
        (11, 'P021', 'Smartwatch', None, 'Fitness tracking smartwatch', 'Unit 21', 2100.00, None),
        (11, 'P022', 'Wireless Earbuds', None, 'True wireless earbuds', 'Unit 22', 2200.00, None),
        (12, 'P023', 'Portable Projector', None, 'Mini portable projector', 'Unit 23', 2300.00, None),
        (12, 'P024', 'Electric Scooter', None, 'Foldable electric scooter', 'Unit 24', 2400.00, None),
        (13, 'P025', 'VR Headset', None, 'Virtual reality headset', 'Unit 25', 2500.00, None),
        (13, 'P026', 'Digital Camera', None, 'Compact digital camera', 'Unit 26', 2600.00, None),
        (14, 'P027', 'Smart Doorbell', None, 'Wi-Fi enabled smart doorbell', 'Unit 27', 2700.00, None),
        (14, 'P028', 'Electric Bike', None, 'Foldable electric bike', 'Unit 28', 2800.00, None)
    ]

    # Data dummy untuk tabel Transactions
    transactions = []
    for umk_id in range(1, 15):
        for i in range(1, 3):  # Tambahkan dua transaksi per UMK_ID
            transactions.append((umk_id, 'income', 150.00 + umk_id * 10, datetime.datetime(2023, 1, i), 'Setor Modal', umk_id * 2 - 1, None))
            transactions.append((umk_id, 'income', 200.00 + umk_id * 10, datetime.datetime(2023, 1, i + 1), 'Penjualan Produk', umk_id * 2, None))
            transactions.append((umk_id, 'expense', 50.00 + umk_id * 10, datetime.datetime(2023, 1, i + 2), 'Pengeluaran Operasional', umk_id * 2 + 1, None))

    try:
        cursor.executemany("""
        INSERT INTO Products (UMK_ID, Code, Name, Image, Description, Unit, Price, deleted_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, products)
        
        cursor.executemany("""
        INSERT INTO Transactions (UMK_ID, Type, Amount, Date, Description, Product_ID, deleted_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, transactions)

        conn.commit()
        print("Data dummy untuk tabel Products dan Transactions berhasil dimasukkan.")
    except Exception as e:
        conn.rollback()
        print(f"Terjadi kesalahan: {e}")

# Fungsi untuk menghasilkan OTP
def generate_otp():
    return str(random.randint(100000, 999999))

# Fungsi untuk validasi nomor telepon
def validate_phone_number(phone_num):
    return phone_num.isdigit()

# Fungsi untuk mendaftarkan admin
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

# Fungsi untuk mendaftarkan UMK
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

# Fungsi untuk login sebagai admin menggunakan nomor telepon
def login_as_admin(phone_num):
    cursor.execute("SELECT User_ID, Role FROM Users WHERE PhoneNum = ? AND Role = 'Administrator' AND deleted_at IS NULL", (phone_num,))
    user = cursor.fetchone()
    if user:
        return user
    else:
        print("Nomor telepon tidak valid atau pengguna tidak ditemukan.")
        return None

# Fungsi untuk login menggunakan OTP
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

# Fungsi untuk login sebagai UMK menggunakan nomor telepon
def login_as_umk(phone_num):
    cursor.execute("SELECT User_ID, Role FROM Users WHERE PhoneNum = ? AND Role = 'UMK' AND first_login_done = 1 AND deleted_at IS NULL", (phone_num,))
    user = cursor.fetchone()
    if user:
        return user
    else:
        print("Nomor telepon tidak valid atau pengguna tidak ditemukan.")
        return None

# Menu utama untuk admin
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
            n = int(input("Masukkan jumlah produk teratas yang ingin dilihat: "))
            view_top_n_products(n)
        elif choice == '4':
            n = int(input("Masukkan jumlah UMK teratas yang ingin dilihat: "))
            view_top_n_umk(n)
        elif choice == '5':
            break
        else:
            print("Pilihan tidak valid. Silakan coba lagi.")


# Fungsi untuk menyetujui pendaftaran UMK
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

# Fungsi untuk melihat UMK yang terdaftar
def view_registered_umks():
    cursor.execute("SELECT * FROM UMK_Profiles WHERE deleted_at IS NULL")
    umks = cursor.fetchall()
    for umk in umks:
        print(umk)

# Fungsi untuk melihat produk teratas berdasarkan jumlah transaksi
def view_top_n_products(n):
    cursor.execute("""
    SELECT p.Name, COUNT(t.Transaction_ID) as Frequency
    FROM Products p
    JOIN Transactions t ON p.Product_ID = t.Product_ID
    WHERE t.Type = 'income' AND t.deleted_at IS NULL
    GROUP BY p.Name
    ORDER BY Frequency DESC
    """)
    top_products = cursor.fetchmany(n)
    
    if top_products:
        print(f"\nTop {n} Produk Paling Laku:")
        for rank, product in enumerate(top_products, 1):
            print(f"{rank}. {product[0]} - {product[1]} kali terjual")
    else:
        print("Tidak ada data produk.")

# Fungsi untuk melihat UMK teratas berdasarkan jumlah transaksi
def view_top_n_umk(n):
    cursor.execute("""
    SELECT u.Name, COUNT(t.Transaction_ID) as Frequency
    FROM UMK_Profiles u
    JOIN Transactions t ON u.UMK_ID = t.UMK_ID
    WHERE t.Type = 'income' AND t.deleted_at IS NULL
    GROUP BY u.Name
    ORDER BY Frequency DESC
    """)
    top_umk = cursor.fetchmany(n)
    
    if top_umk:
        print(f"\nTop {n} UMK Terlaris:")
        for rank, umk in enumerate(top_umk, 1):
            print(f"{rank}. {umk[0]} - {umk[1]} transaksi penjualan")
    else:
        print("Tidak ada data UMK.")

# Fungsi untuk mengelola produk UMK
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

# Fungsi untuk menambah produk UMK
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

# Fungsi untuk melihat produk UMK
def view_products(umk_id):
    cursor.execute("SELECT * FROM Products WHERE UMK_ID = ? AND deleted_at IS NULL", (umk_id,))
    products = cursor.fetchall()
    for product in products:
        print(product)

# Fungsi untuk memperbarui produk UMK
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

# Fungsi untuk menghapus produk UMK
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

# Fungsi untuk melihat pembukuan
def view_bookkeeping():
    cursor.execute("""
    SELECT UMK_ID, Type, Amount, Date, Description, Product_ID
    FROM Transactions
    WHERE deleted_at IS NULL
    ORDER BY Date
    """)
    transactions = cursor.fetchall()
    
    if transactions:
        print("\nPembukuan:")
        for transaction in transactions:
            print(f"""
            UMK_ID: {transaction.UMK_ID}
            Tanggal: {transaction.Date}
            Jenis Transaksi: {transaction.Type}
            Jumlah: {transaction.Amount}
            Deskripsi: {transaction.Description}
            Product_ID: {transaction.Product_ID}
            """)
    else:
        print("Tidak ada data transaksi.")

# Fungsi untuk melihat laporan keuangan UMK
def view_financial_report(umk_id):
    end_date = input("Masukkan tanggal akhir (YYYY-MM-DD): ")
    
    try:
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        print("Format tanggal tidak valid.")
        return

    cursor.execute("""
    SELECT Type, SUM(Amount) as Total
    FROM Transactions
    WHERE UMK_ID = ? AND Date <= ? AND deleted_at IS NULL
    GROUP BY Type
    """, (umk_id, end_date))
    
    transactions = cursor.fetchall()
    
    total_income = 0
    total_expense = 0
    
    for transaction in transactions:
        if transaction.Type == 'income':
            total_income += transaction.Total
        elif transaction.Type == 'expense':
            total_expense += transaction.Total

    balance = total_income - total_expense

    print(f"\nLaporan Keuangan sampai tanggal {end_date.date()}")
    print(f"Total Penerimaan: {total_income}")
    print(f"Total Pengeluaran: {total_expense}")
    print(f"Saldo: {balance}")

# Contoh penggunaan dalam menu UMK
def umk_menu(umk_id):
    while True:
        print("\nMenu UMK")
        print("1. Kelola Produk")
        print("2. Melihat Pembukuan")
        print("3. Lihat Laporan Keuangan")
        print("4. Lihat Laporan Penjualan")
        print("5. Keluar")

        choice = input("Masukkan pilihan Anda: ")

        if choice == '1':
            manage_products(umk_id)
        elif choice == '2':
            view_bookkeeping()
        elif choice == '3':
            view_financial_report(umk_id)
        elif choice == '4':
            view_sales_report(umk_id)
        elif choice == '5':
            break
        else:
            print("Pilihan tidak valid. Silakan coba lagi.")

# Fungsi untuk melihat laporan penjualan UMK
def view_sales_report(umk_id):
    print(f"Melihat laporan penjualan untuk UMK_ID {umk_id}")
    start_date = input("Masukkan tanggal mulai (YYYY-MM-DD): ")
    end_date = input("Masukkan tanggal akhir (YYYY-MM-DD): ")

    try:
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        print("Format tanggal tidak valid.")
        return

    cursor.execute("""
    SELECT 
        p.Name as Product_Name, 
        COUNT(t.Transaction_ID) as Frequency, 
        SUM(t.Amount) as Total_Income,
        u.Name as Receiver
    FROM Transactions t
    JOIN Products p ON t.Product_ID = p.Product_ID
    JOIN UMK_Profiles u ON t.UMK_ID = u.UMK_ID
    WHERE t.Type = 'income' AND t.Date BETWEEN ? AND ? AND t.deleted_at IS NULL
    GROUP BY p.Name, u.Name
    """, (start_date, end_date))
    
    sales_report = cursor.fetchall()
    
    if sales_report:
        print(f"\nLaporan Penjualan Produk dari {start_date.date()} sampai {end_date.date()}")
        for row in sales_report:
            print(f"Produk: {row.Product_Name}, Kuantitas: {row.Frequency}, Pemasukan: {row.Total_Income}, Penerima: {row.Receiver}")
    else:
        print("Tidak ada data penjualan dalam rentang tanggal yang diberikan.")

# Fungsi untuk menampilkan menu utama
def display_main_menu():
    print("1. Masuk sebagai Admin")
    print("2. Masuk sebagai UMK dengan OTP")
    print("3. Masuk sebagai UMK dengan Nomor Telepon")
    print("4. Daftarkan UMK")
    print("5. Daftarkan Admin")
    print("6. Keluar")

# Fungsi utama yang menjalankan aplikasi
def main():
    create_tables()
    insert_dummy_data()
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
