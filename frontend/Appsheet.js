const pdfInput = document.getElementById("pdfFile");
const output = document.getElementById("output");
const copyBtn = document.getElementById("copyBtn");

pdfInput.addEventListener("change", async () => {
  const file = pdfInput.files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append("file", file);

  output.textContent = "⏳ Sedang memproses...";

  try {
    const response = await fetch("http://127.0.0.1:5000/upload", {
  method: "POST",
  body: formData,
});

    if (!response.ok) {
      throw new Error(`Server error ${response.status}`);
    }

    const data = await response.json();
    output.textContent = data.hasil || "⚠️ Gagal mengekstrak data.";
  } catch (err) {
    output.textContent = "❌ Gagal menghubungi server atau memproses file.";
    console.error("Fetch error:", err);
  }
});

copyBtn.addEventListener("click", () => {
  const textarea = document.createElement("textarea");
  textarea.value = output.textContent;
  document.body.appendChild(textarea);
  textarea.select();
  document.execCommand("copy");
  document.body.removeChild(textarea);
  copyBtn.textContent = "✔ Copied!";
  setTimeout(() => (copyBtn.textContent = "Copy"), 1500);
});
