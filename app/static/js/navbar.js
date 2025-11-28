// === Toggle menu (strip 3) ===
const menuIcon = document.getElementById('menu-icon');
const menuList = document.getElementById('menu-list');

menuIcon.addEventListener('click', () => {
  menuList.classList.toggle('active');
});

// === Dropdown "Data" di mode mobile ===
const dropdownA = document.querySelector('.dropdownA');
dropdownA.addEventListener('click', (e) => {
  if (window.innerWidth <= 768) { // hanya aktif di layar kecil
    e.preventDefault();
    dropdownA.classList.toggle('active');
  }
});

// === Dropdown Profil di mode mobile ===
const profileContainer = document.getElementById('profileContainer');
if (profileContainer) {
  const profileBtn = document.getElementById('profileBtn');
  profileBtn.addEventListener('click', (e) => {
    if (window.innerWidth <= 768) {
      e.preventDefault();
      profileContainer.classList.toggle('active');
    }
  });
}
