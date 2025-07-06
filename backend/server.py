from PyPDF2 import PdfReader

def extract_pdf(path):
    reader = PdfReader(path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"

    import re
    def ambil(regex, fallback="-"):
        match = re.search(regex, text, re.DOTALL | re.IGNORECASE)
        return match.group(1).strip() if match else fallback

    def clean_jam(raw):
        match = re.search(r"(\d{2})[.:](\d{2})", raw or "")
        return f"{match.group(1)}:{match.group(2)}" if match else "-"

    from datetime import datetime
    tgl = ambil(r"Tanggal\s*:\s*(\d{2}/\d{2}/\d{4})")
    try:
        tgl_obj = datetime.strptime(tgl, "%d/%m/%Y")
        tanggal = tgl_obj.strftime("%d %B %Y")
    except:
        tanggal = "-"

    return f"""Selamat Pagi/Siang/Sore Petugas Call Center, Update Pekerjaan

Unit Kerja : {ambil(r"Unit Kerja\s*:\s*(.+?)\s*Kantor Cabang")}
Kantor Cabang : {ambil(r"Kantor Cabang\s*:\s*(.+?)\s*Tanggal")}
Tanggal : {tanggal}

Jenis Pekerjaan (Problem) : {ambil(r"Problem\s*[:\-]?\s*(.+?)\s*(Berangkat|Progress)")}

Berangkat : {clean_jam(ambil(r"Berangkat\s*[:\-]?\s*(.+?)\s*(Tiba|Mulai)"))}
Tiba : {clean_jam(ambil(r"Tiba\s*[:\-]?\s*(.+?)\s*(Mulai|Selesai)"))}
Mulai : {clean_jam(ambil(r"Mulai\s*[:\-]?\s*(.+?)\s*Selesai"))}
Selesai : {clean_jam(ambil(r"Selesai\s*[:\-]?\s*(.+?)\n"))}

Progress : {ambil(r"Progress\s*[:\-]?\s*(.+?)\s*(Jenis|Serial|Merk|Type|PIC|Status)")}

Jenis Perangkat : {ambil(r"Jenis Perangkat\s*[:\-]?\s*(.+?)\s*(Serial|Merk|Type|PIC|Status)")}
Serial Number : {ambil(r"Serial Number\s*[:\-]?\s*(.+?)\s*(Merk|Type|PIC|Status)")}
Merk Perangkat : {ambil(r"Merk Perangkat\s*[:\-]?\s*(.+?)\s*(Type|PIC|Status)")}
Type Perangkat : {ambil(r"Type Perangkat\s*[:\-]?\s*(.+?)\s*(PIC|Status)")}

PIC : {ambil(r"PIC\s*[:\-]?\s*(.+?)\s*Status")}
Status : {ambil(r"Status\s*[:\-]?\s*(Done|Pending|On Progress|-)")}
"""
