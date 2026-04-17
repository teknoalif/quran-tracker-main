import json
import os
import gspread
from django.shortcuts import render, redirect
from datetime import date, datetime
from oauth2client.service_account import ServiceAccountCredentials
from django.contrib import messages

try:
    from .data_santri import DATA_SANTRI
except ImportError:
    DATA_SANTRI = {}

# --- KONFIGURASI ---
SPREADSHEET_ID = "18knwd2i4FR0XOX0Bb22No66venosWUsma5DbTZ6u9_s"
KELAS_CHOICES = [(k, f"Kelas {k}") for k in DATA_SANTRI.keys()] if DATA_SANTRI else []

def get_gspread_client():
    """Fungsi pembantu untuk autentikasi Google Sheets"""
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds_json = os.getenv("GOOGLE_CREDENTIALS")
    
    if not creds_json:
        print("DEBUG: GOOGLE_CREDENTIALS tidak ditemukan di Env Vercel")
        return None
    
    try:
        # Bersihkan string dari karakter aneh dan pastikan JSON valid
        creds_json = creds_json.strip()
        creds_dict = json.loads(creds_json)
        
        if 'private_key' in creds_dict:
            # Handle karakter pindah baris yang sering rusak saat copy-paste ke Vercel
            creds_dict['private_key'] = creds_dict['private_key'].replace('\\n', '\n')
        
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        return gspread.authorize(creds)
    except Exception as e:
        print(f"DEBUG Error Auth: {str(e)}")
        return None

def kirim_ke_spreadsheet(data_list):
    try:
        client = get_gspread_client()
        if not client: 
            return False, "Gagal Autentikasi. Cek GOOGLE_CREDENTIALS di Vercel."
        
        sheet = client.open_by_key(SPREADSHEET_ID)
        # Mencoba buka Sheet1, jika gagal ambil tab pertama
        try:
            worksheet = sheet.worksheet("Sheet1")
        except:
            worksheet = sheet.get_worksheet(0)
            
        # USER_ENTERED membuat angka dan tanggal otomatis diformat benar oleh Google
        worksheet.append_rows(data_list, value_input_option='USER_ENTERED')
        return True, "Berhasil"
    except Exception as e:
        return False, f"Google API Error: {str(e)}"

def riwayat_laporan(request):
    tanggal_str = request.GET.get("tanggal", str(date.today()))
    kelas_selected = request.GET.get("kelas", "XA")
    
    nama_list = DATA_SANTRI.get(kelas_selected, [])
    
    # --- LOGIKA AMBIL DATA DARI SHEETS (RIWAYAT) ---
    data_terinput = {}
    try:
        client = get_gspread_client()
        if client:
            sheet = client.open_by_key(SPREADSHEET_ID)
            worksheet = sheet.get_worksheet(0)
            # Ambil semua data sekaligus untuk efisiensi
            records = worksheet.get_all_records()
            
            for row in records:
                # Normalisasi data untuk pencocokan (case-insensitive & trim spasi)
                s_tanggal = str(row.get('Tanggal', '')).strip()
                s_kelas = str(row.get('Kelas', '')).strip()
                s_nama = str(row.get('Nama', '')).strip()

                if s_tanggal == tanggal_str and s_kelas == kelas_selected:
                    data_terinput[s_nama] = {
                        'hadir': row.get('Hadir', 'Hadir'),
                        'khatam': row.get('Khatam', 0),
                        'awal': row.get('Awal', ''),
                        'akhir': row.get('Akhir', ''),
                        'jml': row.get('Jumlah', row.get('Jml', 0))
                    }
    except Exception as e:
        print(f"INFO: Belum ada riwayat atau gagal tarik data: {e}")

    # Gabungkan data daftar santri dengan data yang sudah ada di Sheets
    santris = []
    for i, nama in enumerate(nama_list):
        info = data_terinput.get(nama, {})
        santris.append({
            "id": i,
            "nama": nama,
            "terisi": True if info else False,
            "hadir": info.get('hadir', 'Hadir'),
            "khatam": info.get('khatam', 0),
            "awal": info.get('awal', ''),
            "akhir": info.get('akhir', ''),
            "jml": info.get('jml', 0)
        })
    
    return render(request, "monitoring/riwayat.html", {
        "santris": santris,
        "tanggal_sekarang": tanggal_str,
        "kelas_list": KELAS_CHOICES,
        "kelas_selected": kelas_selected,
    })

def simpan_laporan(request):
    # Default balik ke hari ini jika data POST hilang
    tanggal = str(date.today())
    kelas = "XA"
    
    if request.method == "POST":
        tanggal = request.POST.get("tanggal")
        kelas = request.POST.get("kelas_hidden")
        names = request.POST.getlist("santri_nama")
        hadir = request.POST.getlist("status_kehadiran")
        khatam = request.POST.getlist("jumlah_khatam")
        h_awal = request.POST.getlist("hal_awal")
        h_akhir = request.POST.getlist("hal_akhir")
        
        data_sheet = []
        waktu = datetime.now().strftime("%d/%m/%Y %H:%M")
        
        for i in range(len(names)):
            try:
                # Proteksi jika input kosong
                v_awal = h_awal[i] if (i < len(h_awal) and h_awal[i]) else "0"
                v_akhir = h_akhir[i] if (i < len(h_akhir) and h_akhir[i]) else "0"
                
                # Konversi ke angka untuk hitung selisih halaman
                awal_int = int(v_awal)
                akhir_int = int(v_akhir)
                selisih = akhir_int - awal_int + 1 if (akhir_int >= awal_int and awal_int > 0) else 0
                
                # Susun urutan kolom sesuai header di Google Sheets Bapak
                data_sheet.append([
                    waktu, 
                    tanggal, 
                    "Ustaz/Guru", 
                    kelas, 
                    names[i], 
                    hadir[i] if i < len(hadir) else "Hadir", 
                    khatam[i] if i < len(khatam) else "0", 
                    v_awal, 
                    v_akhir, 
                    selisih
                ])
            except (ValueError, IndexError):
                continue
            
        if data_sheet:
            sukses, pesan = kirim_ke_spreadsheet(data_sheet)
            if sukses:
                messages.success(request, "Alhamdulillah, data setoran berhasil tersimpan!")
            else:
                # Pesan error sekarang akan menampilkan alasan teknis (misal: Permission Denied)
                messages.error(request, f"Waduh, gagal simpan: {pesan}")
                
    return redirect(f"/?tanggal={tanggal}&kelas={kelas}")
