import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from datetime import date, datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

# --- DAFTAR SANTRI MANUAL (Agar tidak Error 500) ---
# Tambahkan nama santri Bapak di sini agar muncul di web
# --- DAFTAR SANTRI ASLI (Data Lengkap) ---
DATA_SANTRI = {
    'XA': [
        'ABDUL HAAMID', 'ALIF WARDHANI SANTOSO', 'ALVARO SYARIF FERYANSYAH', 'ARKAN SYAIBANU SOFYAN', 
        'ARKANSYAH NAKHLAN ZAKARIA', 'AZKA IRHAM PURWANSYAH', 'AZZAM DZAKWAN AL FARUQ', 'DAVA KEANU PUTRA', 
        'EL FAYAADH', 'FAIZ HAQIQI', 'GALYZVITO DWIYANDRA', 'HABIBURRAHMAN AL HASYIM', 'HAFIZ KIYOSHI ARIF', 
        'HASAN', 'HUDZAIFAH AL HUMAIDI', 'LYAS MUSTHAFA AKHYAR', 'IRFANDA ADHA MIRZALI', 
        'KENNARD DZAKI HERLAMBANG', 'LUQMAN ABDUL HAKIM', 'MOHAMMAD AL KAUTSAR', 
        'MOHAMMAD ARSYAD NARARYA PRATOMO', 'MUHAMMAD AL - FATIH', 'MUHAMMAD AYYASH GHAZI MIFZAL', 
        'MUHAMMAD BINTANG PUTRARASYA', 'MUHAMMAD FADHIL AZKARA', 'NOUVAL RASYDAN ENDRI', 
        'RAQOIS FAWWAZ BAARI\'UL MUMTAAZ', 'RANJANA MUMTAZ ATHALLAH', 'ZIDANE'
    ],
    'XB': [
        'ABDULLAH MUHAMMAD RAHMAN', 'AFFAN FIRDAUS', 'AHMAD DANI', 'AKHDAN HELMI', 'AMMAAR ZAKKY BATHHEF', 
        'ANAS WILDAN SOBARI', 'ARIF KHAIRUL AZAM', 'ATILLA DHIYAEL FAJRI', 'BINTANG ALFIANO BRILIANT SAPUTRA', 
        'DARU AZRI ARMANSYAH', 'FA\'IQ', 'FAKHRY MUHAMMAD RAYYAN', 'FAUZAN HUSEIN BADJRY', 
        'HAFIDZ KHALFANI HAMISENA', 'HANIF ALFARIZI', 'KEANU AL GHIFARI AHMAD JAEPUTRA', 
        'LUQMANUL HAKIM ADDATIN', 'MOCH. REYZA SYARIF ABIDIN', 'MUCHAMMAD THORIQ AL MUZACKY', 
        'MUHAMMAD FATHURRAHMAN', 'MUHAMMAD NATHAN AL FAIQ', 'MUHAMMAD RASYID', 'MUSH\'AB UMAIR ZACHA WERUS', 
        'RAYZA FIDIANO SIREGAR', 'SAMI RABBANI HARTONO', 'UBAIDAH AS SA\'DY', 'UMAR MUBARAK', 
        'ZIYAD GHASSAN AZRI SASONO'
    ],
    'XC': [
        'AHMAD HARIS IKHWAN', 'AHMAD TSABIT', 'ANDRA AIDILLAH', 'ARAFAH ZHILLAN AMIR NASUTION', 
        'AUFA SAKHA SALMAN', 'AZFAR IRHAM PURWANSYAH', 'DARRELL YUSRAN ILMANY RAFAN', 'FAIZ ABDUL AZIZ', 
        'FARRAS MUHAMMAD RAMADHAN', 'FATHI RAYA NONCI', 'GAVIN EKISA AQILA FIKRA', 'GHILMAN ADZKA SYUHADA', 
        'KHALISMAN RAMADHAN', 'LUQMAN HAFIDZ ANNURIL HIDAYAT', 'MIQDAD', 'MUHAMMAD ALIFFATTAH AS-SYIFA\' SUYANTOM', 
        'MUHAMMAD AMMAR NUFAIL', 'MUHAMMAD FA\'IQ FAYYADH QUSHAYYI', 'MUHAMMAD NABIL MAKARIM', 
        'MUHAMMAD RAFIIF GATHFAN', 'MUHAMMAD SETYO ABDUN NASTIR', 'MUHAMMAD TEGUH HASAN', 
        'MUHAMMAD TIFATULLAH ARRASYID ISMAIL', 'RAIKHAN RASHEED DZAKIANSYAH', 'TENGKU MUADZ', 
        'UWAIS UBAIDILLAH', 'YAVI AL\'FIAN CHRISTIANDY'
    ],
    'XD': [
        'AHMAD HANIF FAUZAN', 'AHNAF FARRAS JATMIKA', 'ARKAN UMAIR ROFIF', 'ARKANANTA RA\'UUF BAADILLA', 
        'ATHASYAH REIZKI RAMADHAN', 'AZZAM BAWAZIER', 'BRAMANTYO PURWOKO NURINGDAVIANDRA JULIAN SISWOYO', 
        'DHEVIN ADELIO TAMAM', 'ELMALIK ANANDYA SOFYAN', 'FAWAAZ KARIIM BENZEMA', 
        'GHAISAN ALTHAF NAZURAKHADAFI FAHRIANSYAH', 'M YUSUP', 'MAUZA YUSUF RAFFASYA', 'MUHAMMAD BINAR PRAWISENO', 
        'MUHAMMAD FADHIL KHAIRULLAH', 'MUHAMMAD FAREL ISVIKHRAM', 'MUHAMMAD RASHID RIZWAAN', 
        'MUHAMMAD RHAMDHANI EL HAQQ', 'NAUFAL FAWWAZ ALFIAN', 'RADEN MIKAIL HAFIZH GOENAWAN', 
        'RAFA DLAIFURRAHMAN FAHAMSYAH', 'RAFI MUHAMAD RIZQI', 'SALMAN ALI', 'SHAQUILLE MUFTY KASYAFANI', 
        'SULAEMAN HARUN MAR\'IZIGGY ALVA RADZAVIER'
    ],
    'XE': [
        'ADKHILNI MUDKHALA SIDQI', 'ARKAAN ABDILLAH PRANAAWALIAH', 'ARKHAREGA RADITHYA NARARYA AGUSTIAN', 
        'ATHAYA SHABRAZAN ADHSY', 'AZZAM SHIDIQ NURYANTO', 'DAFFA TRISTAN ADINATA KHRISNADIYANTO', 
        'DAFFI HADI YURIAWAN', 'DASTAN ZAHIR MANAF', 'DZAKY ALMER RAFIF', 'FARZAN FAEYZA RAVIDYATAMA', 
        'FATHAN ZIDANE ATTAYA', 'HAMDY MOHAMMAD GHOSAN', 'HAZZA IRSA ASWATAMA', 'MUHAMAD ATHADZAKI UKASYAH ZAENAL', 
        'MUHAMMAD DZUL HABIE MUKTIADIM', 'MUHAMMAD FARIS HUMAM', 'MUHAMMAD MULTAZAM AL GHAZALI', 
        'PARAMA RAISSA OBADIAH', 'QAISHAR FADHIL DZIHNI', 'R. MUHAMMAD TERZAGHI INDRA HERMAWAN', 
        'REYHAN FADHLILLAH PANGESTU', 'RHAFAEL FATURAHMAN', 'RYANDRA PUTRA RIFAI', 'SA\'AD ALI', 
        'SYED AHMAD ZAKY ABDURAHMAN', 'THUFAIL MUHAMMAD KHALIDI', 'THUFEIL TSANI AR-ROYYAN'
    ],
    'XF': [
        'ABRISAM TRYSTAN AL-LYADI', 'ALTAF ADLI ARYASATYA', 'AMRU ABDUL FATTAH', 'ARYAN MIKA USAID', 
        'AULIA ABDURRAHMAN RAFIUDDIN', 'DANISH MUMTAAZ AHMAD', 'DEWA ANUGERAH SUNARTO', 'DZIKRA AQSHA RAMADHAN', 
        'FAIDHUL KHOIR', 'FARREL RASYA FAUZI', 'GHAZI MAGHRIBI FATHUL MAKKI', 'HASAN RAFA AQILAH', 
        'IBNU JAMIL MAJIDI', 'IHSAN MAULANA KEANDRE', 'MIKHAIL ALFATIH HADINA', 'MUHAMMAD DENDY JUNSEN DUOVAN', 
        'MUHAMMAD FACHRI ANGGARA', 'MUHAMMAD NAZRIL BAIHAQI', 'MUHAMMAD RAFA CAKSONO', 'MUHAMMAD RIFQI', 
        'MUHAMMAD SYAUQI ABRAR', 'RADITYA ABDI WIENATA', 'RANGGA ADYATMA BRAMANTYO', 'RAYYAN MALIK ARYASATYA', 
        'SULTHAN ALTHAF OHINPUTRA RAHIM', 'ZAHRAN DZIAULHAQ KAMIL', 'ZHAFIR KHALISH AL MASY\'AL'
    ],
    'XIA': [
        'ABDILLAH', 'ABDURRAHMAN MUSAA', 'ADYA RAKHA RAMADHAN', 'AHMAD HAIDAR', 'AHMAD RAFAN KAYSAN', 
        'ALTHEDA RAFA ATTALLAH', 'AZZAM ABDUL AZIS', 'BISMA ANDI PRADIPTA', 'DAFFA FAUZAN NOOR', 
        'DJAGA DZAR AL GHIFARI', 'FAKHRI NUR', 'FARUQ ABDUL AZIZ', 'FATHONI NUR ISMAIL', 'FERDIAN MAHARADIKO', 
        'GARDIANO NUSANTARA NUGROHO', 'LUQMAN AL ABRAR', 'MUHAMAD FIKRI MAULUDIN', 
        'MUHAMMAD ARKAN ARDIONA FIRJATULLAH', 'MUHAMMAD FERNANDO', 'MUHAMMAD HAQQI SUKMARA', 
        'MUHAMMAD IBRAHIM MAHMOUD SULAIMAN', 'MUJAHIDURRAHMAN', 'NASHIR AHMAD', 'RAIHAN PASYA PRATAMA', 
        'RASHADYA ALIF RIZQ PUTRA', 'SOFWANUL FIKRI RAMADHAN', 'SULTHON HANIF AL MUSHTHOFA', 
        'THARIQ PRADYGTA PUTRA', 'YUKIO TAUFIQILLAH'
    ],
    'XIB': [
        'ANIF RIDWAN', 'AHMAD GHAZY', 'AHMAD RASYAD AL-HAFIZH', 'AKBAR TEDIA MUHAMMAD', 'ALIEF RAIHAN PUTRA', 
        'BAYHAQIY VITO NAGATA', 'DZAKI AQILAH AHMAD', 'GAZA MUHAMMAD JIBRIL SARDIN', 'HAMZAH FAKHRI ASLAMI', 
        'IDRIS AFWAN ABDILLAH', 'FATHURAHMAN KHAIRURIZKI', 'MAFAZA HIZBUNA', 'MALKA HAYFA ASYARI', 
        'MOCHAMAD HAIKAL NOVANTO', 'MUAFA HAIDAR MUSHLIH', 'MUFID MUBAROK', 'MUHAMMAD ABRISAM TAQY MUFID', 
        'MUHAMMAD AKBAR KUSUMA', 'MUHAMMAD AKMAL RASYIDI', 'MUHAMMAD ALIF ARSA UPANGGA', 
        'MUHAMMAD FAIDRAKY PRANAWA', 'MUHAMMAD FAYADH AQWAN', 'MUHAMMAD IZZUDDIN UBAIDILLAH', 
        'MUHAMMAD RAFFA HUSAINI', 'NABIL ZULHAJJI DANIAL', 'RASYA TAUFIQ RAHMAN AL AZIZY', 
        'HESA FADHILLAH NUGROHO', 'SULTAN MAULANA FATIH', 'SYAHDAKA SATRIA ARSALAN'
    ],
    'XIC': [
        'ABDULLAH SAID ALI AL FAWWAZ', 'ALMER NIBRAS JIZENKA', 'ARKAN ABDUL GHAFAR RAMADHAN', 
        'ARKAN ADI BENNOVRY', 'DHIWA ADZIQ ANNAFI', 'DHOBITH SYATHIR MUHAMMAD ASH SHIDDIQ', 
        'FABIAN ADHIDAMA SAILENDRA', 'ALFACHRY ADLAN', 'IHSAN MUBARAK HASRUL', 'KHOLID', 
        'ILYASA ZHAFRAN ARAFA', 'JAMIKAIL MUHAMMAD ALTAFTSALIS', 'MUCHAMMAD SILVAN MAULANA', 
        'MUHAMMAD ALFATH', 'MUHAMMAD AZKA DZIKRULLAH AL-MUZAKKI', 'MUHAMMAD BARIQ', 
        'MUHAMMAD DAFFA DIPRAJA', 'MUHAMMAD FAIQ ATALLAH', 'MUHAMMAD FILZA FAWAZ ZIHNI', 
        'MUHAMMAD IQBAL RASYID', 'MUHAMMAD TAQY NASHARY', 'AHDAN MUHAMMAD DUDUS', 'RAFLIE SAPUTRA', 
        'RIDHO FADILLAH YUSUF', 'RIDWAN MAULANA', 'RIZQY AZZAM ZULFITRAH KAMAL', 'ZAAHIR AKRAM ALVARO', 
        'ZHAFIF AZKA SASONO'
    ],
    'XID': [
        'ABIYYU AMMAR WITJAKSONO', 'AIMAN AL AKHSHONI', 'AKMA FADHILAH PARIKESIT', 'ANDI NABIL FAHRIZA RAHMAN', 
        'ANDREA AULIA AL-GHAZALI', 'DANIEL SYAHREZA', 'FARHAN ROSADI ALEXANDER', 'FAUZAN ALI WIBOWO', 
        'HAIKAL RAMADHAN NUR HAKIM', 'HARITS ABQARY SYAHDAN M. JAKFAR', 'M. NADA DARRYL SYAHIN', 
        'KAMAL \'UBAIDILLAH', 'LUTHFI MARANDEWA', 'MUHAMMAD ARKAAN HARRIS', 'MUHAMMAD FAJRIL FIRDAUS', 
        'MUHAMMAD HAFY YAZID NATHIQ', 'MUHAMMAD HAZIQ ALFIQNOV', 'MUHAMMAD LUTHFI RUSYDI', 
        'MUHAMMAD RAMZY RAMADHAN', 'MUHAMMAD RAYYAN DHIA', 'MUHAMMAD ROYAN', 'MUHAMMAD SYAMIL ZULFA SULAIMAN', 
        'RADITYA FARHAN NURHUDA', 'RAFFI AFKAR FIRMANSYAH', 'ZUHDI FADHLURRAHMAN HAAJ', 'SALMAN AL FATHON', 
        'SULTHAN AZHAR RAFIF HABIBIE'
    ],
    'XIE': [
        'ABDILLAH RAFI AGUNG', 'BISMA DZAKY WAHYU SATRIO', 'DAR ARKAN TAJUSA SULANJANA', 
        'FACHRIZAL ADITYA RIZQI RAMADHAN', 'FARRAND FADHILAH FAISOL', 'FATIH AFZALURAHMAN RAHTOMO', 
        'FAUZAAN ADITYA NUGRAHA', 'HAMMAD RIFAI', 'IQBAL ATHAR PATRIA LUKMAN', 'JIBRIL AESAR AULAYAIN', 
        'JIBRIL ARIFIN PUTRA', 'MUH REHAN FADILAH', 'MUHAMMAD ALIF ALFAZA', 'MUHAMMAD AMMAAR ZIYAADH', 
        'MUHAMMAD DIHYAH HARAHAP', 'MUHAMMAD GHAZZA AL GHIFFARI', 'MUHAMMAD HAFIZH NAWWAFL', 'MUHAMMAD HAMZAH', 
        'MUHAMMAD IZZA IBRAHIM', 'MUHAMMAD KHALIF ABDUL AZIZ', 'MUHAMMAD SALMAN AL ASYAH', 
        'RAFIF AHNAF NASUTION', 'YAHYA EL YASIN', 'ZIYYAD ABBEY POHAN'
    ]
}

# Update daftar pilihan kelas Bapak
KELAS_CHOICES = [
    ('XA', 'Kelas XA'), ('XB', 'Kelas XB'), ('XC', 'Kelas XC'), ('XD', 'Kelas XD'), 
    ('XE', 'Kelas XE'), ('XF', 'Kelas XF'), ('XIA', 'Kelas XIA'), ('XIB', 'Kelas XIB'), 
    ('XIC', 'Kelas XIC'), ('XID', 'Kelas XID'), ('XIE', 'Kelas XIE')
]

def format_spreadsheet(sheet):
    try:
        sheet.format("A1:J1", {"backgroundColor": {"red": 0.0, "green": 0.4, "blue": 0.0}, "textFormat": {"foregroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0}, "bold": True}})
    except:
        pass

def kirim_ke_spreadsheet(data_list):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        if os.getenv('GOOGLE_CREDENTIALS'):
            creds_dict = json.loads(os.getenv('GOOGLE_CREDENTIALS'))
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        else:
            json_path = os.path.join(os.getcwd(), 'credentials.json')
            creds = ServiceAccountCredentials.from_json_keyfile_name(json_path, scope)
            
        client = gspread.authorize(creds)
        spreadsheet_id = "1gKsf0NS1MkEC5-GtN4eRFhDqWLYEaGFMhAkfEYJ8Fvc"
        worksheet = client.open_by_key(spreadsheet_id).get_worksheet(0)
        worksheet.append_rows(data_list)
        format_spreadsheet(worksheet)
        return True
    except Exception as e:
        print(f"Gagal Sinkron ke Sheets: {e}")
        return False

# Hapus sementara @login_required agar Bapak bisa tes tanpa database user
def riwayat_laporan(request):
    tanggal_str = request.GET.get('tanggal', str(date.today()))
    kelas_selected = request.GET.get('kelas', 'XA')
    
    # Ambil daftar nama dari variabel DATA_SANTRI di atas, bukan dari database
    nama_santris = DATA_SANTRI.get(kelas_selected, [])
    
    # Buat objek buatan agar template tidak error
    santris = []
    for i, nama in enumerate(nama_santris):
        santris.append({'id': i, 'nama': nama})

    return render(request, 'monitoring/riwayat.html', {
        'santris': santris, 
        'data_map': {}, 
        'auto_fill_data': {},
        'tanggal_sekarang': tanggal_str, 
        'kelas_list': KELAS_CHOICES, 
        'kelas_selected': kelas_selected,
    })

def simpan_laporan(request):
    if request.method == 'POST':
        tanggal = request.POST.get('tanggal')
        kelas = request.POST.get('kelas_hidden')
        santri_names = request.POST.getlist('santri_nama') # Kita pakai nama sekarang
        kehadiran = request.POST.getlist('status_kehadiran')
        khatam = request.POST.getlist('jumlah_khatam')
        h_awal = request.POST.getlist('hal_awal')
        h_akhir = request.POST.getlist('hal_akhir')
        
        data_sheet = []
        waktu_input = datetime.now().strftime("%d/%m/%Y %H:%M")
        user_sekarang = request.user.username if request.user.is_authenticated else "Guest"

        for i in range(len(santri_names)):
            awal = int(h_awal[i] or 0)
            akhir = int(h_akhir[i] or 0)
            jml = akhir - awal + 1 if (akhir >= awal and awal > 0) else 0
            
            # Langsung bungkus untuk Google Sheets (Skip simpan ke SQL karena memory bakal hilang)
            data_sheet.append([
                waktu_input, tanggal, user_sekarang, kelas, 
                santri_names[i], kehadiran[i], khatam[i] or 0, 
                awal, akhir, jml
            ])

        if data_sheet: 
            kirim_ke_spreadsheet(data_sheet)
            
        return redirect(f"/?tanggal={tanggal}&kelas={kelas}")
