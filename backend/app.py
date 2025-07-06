from flask import Flask, request, jsonify
from flask_cors import CORS
import fitz  # PyMuPDF
import re

app = Flask(__name__)
CORS(app)

# ==================== UTILITAS ====================

def format_tanggal(tanggal):
    bulan = [
        "Januari", "Februari", "Maret", "April", "Mei", "Juni",
        "Juli", "Agustus", "September", "Oktober", "November", "Desember"
    ]
    dd, mm, yyyy = tanggal.split("/")
    return f"{dd} {bulan[int(mm)-1]} {yyyy}"

def extract_text_from_pdf(file_stream):
    doc = fitz.open(stream=file_stream.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def ambil(pattern, text, fallback="-", flags=0):
    match = re.search(pattern, text, flags)
    return match.group(1).strip() if match else fallback

def cari_kantor_cabang(text):
    label = "Kantor Cabang"
    start = text.find(label)
    if start == -1:
        return "-"
    after_label = text[start + len(label):]
    stopwords = ["Asset ID", "Tanggal", "Jenis", "Progress", "Pelapor", "Status", "SN", "Type", "\n\n"]
    end_index = len(after_label)
    for stop in stopwords:
        idx = after_label.find(stop)
        if idx != -1 and idx < end_index:
            end_index = idx
    result = after_label[:end_index].strip().replace("\n", " ")
    result = re.sub(r"\s+", " ", result)
    return result

# ==================== ROUTE ====================

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file provided"}), 400

    text = extract_text_from_pdf(file)

    # === Unit Kerja ===
    unit_kerja = ambil(r"Unit Kerja\s*:\s*(.*?)\s*(Kantor Cabang|Tanggal|Perangkat|Tanggal\/Jam|$)", text, flags=re.DOTALL)
    unit_kerja = " ".join(unit_kerja.split())

    # === Kantor Cabang ===
    kantor_cabang = cari_kantor_cabang(text)

    # === Tanggal ===
    tanggal_raw = ambil(r"Tanggal\/Jam\s*:\s*(\d{2}/\d{2}/\d{4})", text)
    tanggal = format_tanggal(tanggal_raw) if tanggal_raw != "-" else "-"

    # === Problem ===
    problem = ambil(r"Trouble Dilaporkan\s*:\s*(.*?)\s+(Solusi|Progress|KETERANGAN)", text, flags=re.I)
    if problem == "-":
        problem = ambil(r"Problem\s*[:\-]?\s*(.*?)\s+(Solusi|Progress|KETERANGAN)", text, flags=re.I)

    # === Progress ===
    progress = ambil(r"Solusi\s*/?\s*Perbaikan\s*:\s*(.*?)\s+(KETERANGAN|Backup|Status)", text, flags=re.I)

    # === Jam ===
    def jam(label):
        return ambil(fr"{label}\s+(\d{{2}}[.:]\d{{2}})", text).replace(".", ":")

    berangkat = jam("BERANGKAT")
    tiba = jam("TIBA")
    mulai = jam("MULAI")
    selesai = jam("SELESAI")

    # === Perangkat ===
    jenis = ambil(r"Perangkat\s+(Notebook Highend|PC|Printer|.*?)\s+(Kantor Cabang|Asset ID|SN)", text)
    sn = ambil(r"SN\s+([A-Z0-9\-]+)", text)
    merk = ambil(r"Merk\s+(?:Perangkat)?\s*[:\-]?\s*([A-Za-z0-9]+)", text, flags=re.IGNORECASE)
    tipe = ambil(r"Type\s+([A-Za-z0-9\s\-]+?)(?:\s+SN|\s+PW|$)", text)

    # === PIC ===
    pic = ambil(r"Pelapor\s*:\s*(.*?)\s+(Type|Status|$)", text)
    if "(" in pic:
        pic = pic.split("(")[0].strip()

    # === Status ===
    status = ambil(r"Status Pekerjaan\s*:?\s*(Done|Pending|On\s?Progress)", text, flags=re.I)

    hasil = f"""Selamat Pagi/Siang/Sore Petugas Call Center, Update Pekerjaan

Unit Kerja : {unit_kerja}
Kantor Cabang : {kantor_cabang.lstrip(":").strip()}

Tanggal : {tanggal}

Jenis Pekerjaan (Problem) : {problem}

Berangkat : {berangkat}
Tiba : {tiba}
Mulai : {mulai}
Selesai : {selesai}

Progress : {progress}

Jenis Perangkat : {jenis}
Serial Number : {sn}
Merk Perangkat : {merk}
Type Perangkat : {tipe}

PIC : {pic}
Status : {status}
"""
    return jsonify({"hasil": hasil})

@app.route("/")
def home():
    return "Server is running!"

if __name__ == "__main__":
    app.run(debug=True)
