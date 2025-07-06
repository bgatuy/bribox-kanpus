const pdfInput = document.getElementById("pdfFile");
const output = document.getElementById("output");
const copyBtn = document.getElementById("copyBtn");

pdfInput.addEventListener("change", async () => {
  const file = pdfInput.files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append("file", file);

  output.textContent = "⏳ Sedang diproses...";

  try {
    const response = await fetch("http://127.0.0.1:5000/upload", {
      method: "POST",
      body: formData,
    });

    const data = await response.json();
    output.textContent = data.hasil || "⚠️ Gagal mengekstrak data.";
  } catch (error) {
    output.textContent = "❌ Error saat mengirim ke server.";
    console.error("Fetch error:", error);
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
