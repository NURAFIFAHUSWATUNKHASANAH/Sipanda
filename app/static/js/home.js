document.addEventListener("DOMContentLoaded", function () {
    const images = [
        "url('/static/img/in.jpg')",
        "url('/static/img/en.jpg')",
        "url('/static/img/un.jpg')"
    ];

    let currentIndex = 0; // Indeks gambar aktif
    const jumbotron = document.getElementById('Jumbroton');
    const imgPG = document.querySelectorAll('.imgPG'); // Card gambar kecil
    const indicators = document.querySelectorAll('.ila'); // Indikator kecil
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');

    // Fungsi untuk memperbarui jumbotron besar dan indikator kecil
    function updateJumbotron(index) {
        if (jumbotron) {
            jumbotron.style.backgroundImage = `linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.5)), ${images[index]}`;
        }

        // Perbarui status indikator
        indicators.forEach((indicator, i) => {
            indicator.classList.toggle('ila-active', i === index);
            indicator.classList.toggle('ila', i !== index);
        });
    }

    // Inisialisasi jumbotron besar
    updateJumbotron(currentIndex);

    // Event listener untuk tombol navigasi
    prevBtn.addEventListener('click', function () {
        currentIndex = (currentIndex === 0) ? images.length - 1 : currentIndex - 1;
        updateJumbotron(currentIndex);
    });

    nextBtn.addEventListener('click', function () {
        currentIndex = (currentIndex === images.length - 1) ? 0 : currentIndex + 1;
        updateJumbotron(currentIndex);
    });

    // Event listener untuk klik card gambar kecil
    imgPG.forEach((img, index) => {
        img.addEventListener('click', function () {
            currentIndex = index; // Set indeks sesuai dengan gambar kecil yang diklik
            updateJumbotron(currentIndex);
        });
    });

    // Event listener untuk klik indikator kecil
    indicators.forEach((indicator, index) => {
        indicator.addEventListener('click', function () {
            currentIndex = index; // Set indeks sesuai dengan indikator yang diklik
            updateJumbotron(currentIndex);
        });
    });
});
