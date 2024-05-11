import mysql from 'mysql2';

export const UsahaMikroKecilDB = await mysql.createConnection({
    host: 'localhost',
    user: 'root',
    password: '',
    database: 'em_umk'
});

UsahaMikroKecilDB.connect((err) => {
    if (err) {
      console.error('Kesalahan koneksi database:', err);
    } else {
      console.log('Koneksi database berhasil');
    }
});
