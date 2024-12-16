import pandas as pd
import streamlit as st
from metadata.data_toko import baju_anak, accounts, vouchers
from functions.function import auth_user

# Simpan Pesanan di Keranjang
keranjang = []

# Fitur Registrasi Pembeli
def register_pembeli(df_accounts):
    st.subheader("Registrasi Pembeli")
    username = st.text_input("Masukkan username:")
    password = st.text_input("Masukkan password:", type="password")

    if st.button("Daftar"):
        if username in df_accounts['username'].values:
            st.error("Username sudah terdaftar. Gunakan username lain.")
        else:
            new_account = {"username": username, "password": password, "role": "pembeli"}
            df_accounts = df_accounts._append(new_account, ignore_index=True)
            st.success("Registrasi berhasil! Silakan login untuk melanjutkan.")
    return df_accounts

# Fitur Tambah Stok Baju (Admin)
def tambah_stok(df_baju_anak):
    st.subheader("Tambah Stok Baju")
    nama_baju = st.text_input("Masukkan nama baju:")
    harga_baju = st.number_input("Masukkan harga baju:", min_value=0, step=1000)

    if st.button("Tambah Stok"):
        df_baju_anak = df_baju_anak._append({"Nama": nama_baju, "Harga": harga_baju}, ignore_index=True)
        st.success(f"Berhasil menambahkan baju: {nama_baju} dengan harga Rp{harga_baju}.")
    return df_baju_anak

# Fitur Lihat Data Baju
def lihat_data_baju(df_baju_anak):
    st.subheader("Data Baju Anak")
    st.dataframe(df_baju_anak)

# Fitur Tambah ke Keranjang dengan Pilihan Ukuran
def tambah_ke_keranjang(df_baju_anak, keranjang):
    st.subheader("Tambah ke Keranjang")
    st.dataframe(df_baju_anak)

    index_baju = st.number_input("Pilih nomor baju (0 untuk batal):", min_value=0, max_value=len(df_baju_anak), step=1)
    ukuran = st.selectbox("Pilih ukuran:", ["", "S", "M", "L", "XL"])

    if st.button("Tambahkan ke Keranjang"):
        if index_baju == 0:
            st.info("Batal menambahkan baju ke keranjang.")
        elif ukuran == "":
            st.error("Harap pilih ukuran baju.")
        else:
            baju = df_baju_anak.iloc[index_baju - 1]
            item = baju.to_dict()
            item['Ukuran'] = ukuran
            keranjang.append(item)
            st.success(f"Berhasil menambahkan {baju['Nama']} ukuran {ukuran} ke keranjang.")
    return keranjang

# Fitur Lihat Keranjang
def lihat_keranjang(keranjang):
    st.subheader("Keranjang Belanja")
    if not keranjang:
        st.info("Keranjang Anda kosong.")
    else:
        df_keranjang = pd.DataFrame(keranjang)
        st.dataframe(df_keranjang)
        total = sum(item['Harga'] for item in keranjang)
        st.write(f"**Total: Rp{total}**")

# Fitur Pembayaran
def bayar_keranjang(keranjang, df_vouchers):
    st.subheader("Pembayaran Keranjang")
    if not keranjang:
        st.warning("Keranjang Anda kosong. Pergi ke katalog untuk memilih barang yang Anda suka.")
        return keranjang

    lihat_keranjang(keranjang)
    total = sum(item['Harga'] for item in keranjang)

    kode_voucher = st.text_input("Masukkan kode voucher (lewati jika tidak ada):")
    if st.button("Gunakan Voucher"):
        if kode_voucher:
            voucher = df_vouchers[df_vouchers['kode'] == kode_voucher]
            if not voucher.empty:
                diskon = voucher.iloc[0]['diskon']
                total *= (1 - diskon)
                st.success(voucher.iloc[0]['Annouce'])
            else:
                st.error("Kode voucher tidak valid!")

    st.write(f"**Total yang harus dibayar: Rp{total:.0f}**")

    metode_pembayaran = st.radio("Metode Pembayaran:", ["Cash on Delivery (COD)", "Transfer Bank (Virtual Account)"])

    if st.button("Konfirmasi Pembayaran"):
        if metode_pembayaran == "Cash on Delivery (COD)":
            st.success("Pesanan Anda akan dikirimkan dan dibayar saat barang diterima. Terima kasih!")
            keranjang.clear()
        elif metode_pembayaran == "Transfer Bank (Virtual Account)":
            virtual_account = "1234567890"  # Contoh nomor VA
            st.info(f"Lakukan transfer ke nomor Virtual Account berikut: {virtual_account}")
            st.info(f"Total transfer: Rp{total:.0f}")
            if st.button("Saya sudah transfer"):
                st.success("Pembayaran berhasil. Terima kasih telah berbelanja!")
                keranjang.clear()
    return keranjang

# Main Program
def main():
    st.title("Toko Baju Anak Andalan")

    # Load data
    df_baju_anak = pd.DataFrame(baju_anak)
    df_vouchers = pd.DataFrame(vouchers)
    df_accounts = pd.DataFrame(accounts)

    menu = st.sidebar.selectbox("Menu", ["Home", "Register", "Login"])

    if menu == "Home":
        st.write("Selamat datang di Toko Baju Anak Andalan!")

    elif menu == "Register":
        df_accounts = register_pembeli(df_accounts)

    elif menu == "Login":
        username = st.text_input("Username:")
        password = st.text_input("Password:", type="password")

        if st.button("Login"):
            login_result = auth_user(df_accounts, username, password)
            if login_result:
                username, role = login_result
                st.success(f"Login berhasil! Selamat datang, {username} ({role}).")

                if role == "admin":
                    st.sidebar.subheader("Menu Admin")
                    admin_menu = st.sidebar.selectbox("Pilih Menu", ["Lihat Data Baju", "Tambah Stok Baju"])

                    if admin_menu == "Lihat Data Baju":
                        lihat_data_baju(df_baju_anak)
                    elif admin_menu == "Tambah Stok Baju":
                        df_baju_anak = tambah_stok(df_baju_anak)

                elif role == "pembeli":
                    st.sidebar.subheader("Menu Pembeli")
                    pembeli_menu = st.sidebar.selectbox("Pilih Menu", ["Lihat Data Baju", "Tambah ke Keranjang", "Lihat Keranjang", "Bayar Keranjang"])

                    if pembeli_menu == "Lihat Data Baju":
                        lihat_data_baju(df_baju_anak)
                    elif pembeli_menu == "Tambah ke Keranjang":
                        keranjang = tambah_ke_keranjang(df_baju_anak, keranjang)
                    elif pembeli_menu == "Lihat Keranjang":
                        lihat_keranjang(keranjang)
                    elif pembeli_menu == "Bayar Keranjang":
                        keranjang = bayar_keranjang(keranjang, df_vouchers)

if __name__ == "__main__":
    main()
