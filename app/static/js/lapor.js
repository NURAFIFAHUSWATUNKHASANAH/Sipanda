// Inisialisasi peta dengan Leaflet
var map = L.map('map').setView([-6.200000, 106.816666], 13); // Default: Jakarta

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

var marker;

// Tambahkan event untuk klik pada peta
map.on('click', function (e) {
    var latlng = e.latlng;
    var coords = latlng.lat.toFixed(6) + ',' + latlng.lng.toFixed(6);

    if (marker) {
        marker.setLatLng(latlng);
    } else {
        marker = L.marker(latlng).addTo(map);
    }

    document.getElementById('maps').value = coords;
});

// Fungsi untuk mencari alamat dengan Nominatim (OpenStreetMap API)
function geocodeAddress(address) {
    // 1️⃣ Bersihkan format alamat yang tidak dikenali
    let cleanedAddress = address
        .replace(/\b(RT\.?\s*\d+|RW\.?\s*\d+|KAB\.?|KEC\.?|PROV\.?|DSN\.?|DESA\.?|DS\.?)\b/gi, '')
        .replace(/\s+/g, ' ') // hilangkan spasi berlebih
        .trim();

    // 2️⃣ Tambahkan konteks Indonesia biar lebih akurat
    let fullAddress = `${cleanedAddress}, Indonesia`;

    // 3️⃣ Panggil API Nominatim
    fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(fullAddress)}&addressdetails=1`)
        .then(response => response.json())
        .then(data => {
            if (data.length > 0) {
                const lat = parseFloat(data[0].lat);
                const lon = parseFloat(data[0].lon);

                map.setView([lat, lon], 16);
                if (marker) marker.setLatLng([lat, lon]);
                else marker = L.marker([lat, lon]).addTo(map);

                document.getElementById('maps').value = `${lat.toFixed(6)},${lon.toFixed(6)}`;
            } else {
                // 4️⃣ Jika gagal, coba fallback: ambil kata terakhir (misal "Slawi", "Tegal")
                const parts = cleanedAddress.split(' ');
                if (parts.length > 1) {
                    const fallback = parts.slice(-2).join(' ');
                    fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(fallback + ', Indonesia')}`)
                        .then(res => res.json())
                        .then(fallbackData => {
                            if (fallbackData.length > 0) {
                                const lat = parseFloat(fallbackData[0].lat);
                                const lon = parseFloat(fallbackData[0].lon);
                                map.setView([lat, lon], 13);
                                if (marker) marker.setLatLng([lat, lon]);
                                else marker = L.marker([lat, lon]).addTo(map);
                                document.getElementById('maps').value = `${lat.toFixed(6)},${lon.toFixed(6)}`;
                            } else {
                                alert("Lokasi tidak ditemukan, silakan klik langsung pada peta untuk memilih posisi.");
                            }
                        });
                } else {
                    alert("Lokasi tidak ditemukan, silakan klik langsung pada peta untuk memilih posisi.");
                }
            }
        })
        .catch(err => {
            console.error(err);
            alert("Terjadi kesalahan saat mencari lokasi. Coba lagi nanti.");
        });
}


// Event listener untuk input alamat
document.getElementById('alamat').addEventListener('input', function () {
    var address = this.value;

    if (address.length > 3) { // Mulai mencari jika input lebih dari 3 karakter
        geocodeAddress(address);
    }
});

// const form = document.querySelector('.activity-form');
// form.addEventListener('submit', function (event) {
//     event.preventDefault(); // Mencegah submit default

//     const formData = new FormData(form); // Ambil data form
//     fetch(form.action, {
//         method: 'POST',
//         body: formData,
//     })
//         .then(response => response.json())
//         .then(data => {
//             if (data.success) {
//                 alert('Laporan berhasil dikirim, terima kasih!');
//                 window.location.href = "{{ url_for('home') }}"; // Redirect ke home
//             } else {
//                 alert('Gagal mengirim laporan: ' + data.message);
//             }
//         })
//         .catch(error => {
//             console.error('Error:', error);
//             alert('Terjadi kesalahan saat mengirim laporan.');
//         });
// });
// const form = document.querySelector('.activity-form');
// form.addEventListener('submit', function (event) {
//     event.preventDefault(); // Mencegah submit default

//     setTimeout(function () {
//         alert('Laporan berhasil dikirim, terima kasih!');
//         window.location.href = homeUrl; // Gunakan variabel homeUrl dari template
//     }, 1000);
// });