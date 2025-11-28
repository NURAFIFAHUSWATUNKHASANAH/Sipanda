document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("registerForm").addEventListener("submit", function (event) {
        event.preventDefault(); // Mencegah form langsung submit

        let formData = new FormData(this); // Ambil data form

        fetch("/register", {
            method: "POST",
            body: formData
        })
        .then(response => response.json()) // Konversi response ke JSON
        .then(data => {
            var successModal = new bootstrap.Modal(document.getElementById("successModal"));
            document.getElementById("modalTitle").textContent = data.status;
            document.getElementById("modalMessage").textContent = data.message;

            if (data.success) {
                document.getElementById("modalIcon").src = "/static/image/success.png"; // Ikon sukses
                document.getElementById("closeModal").onclick = function () {
                    window.location.href = "/login"; // Redirect ke login jika sukses
                };
            } else {
                document.getElementById("modalIcon").src = "/static/image/error.png"; // Ikon error
                document.getElementById("closeModal").onclick = function () {
                    successModal.hide(); // Tutup modal jika gagal
                };
            }

            successModal.show();
        })
        .catch(error => console.error("Error:", error));
    });
});
