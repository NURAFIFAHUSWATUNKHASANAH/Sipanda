document.addEventListener("DOMContentLoaded", function () {

    const menuIcon = document.getElementById("menu-icon");
    const menuList = document.getElementById("menu-list");

    menuIcon.addEventListener("click", () => {
        menuList.classList.toggle("hidden");
    });


    const icPg = document.querySelectorAll('.imgPG img');
    const jb = document.getElementById('Jumbroton');


    icPg.forEach(img => {
        img.addEventListener('click', function () {
            const parentDiv = this.parentElement;
            const bgIg = parentDiv.getAttribute('datajm');
            if (jb && bgIg) {
                jb.style.backgroundImage = `url(${bgIg.replace("url('", "").replace("')", "")})`;
            }
        });
    });
    // // JavaScript untuk mengendalikan dropdown profil
    // document.getElementById("profileBtn").addEventListener("click", function (e) {
    //     e.preventDefault();  // Mencegah link default
    //     var dropdown = document.getElementById("profileDropdown");
    //     dropdown.style.display = (dropdown.style.display === "block") ? "none" : "block";
    // });

    // // Menutup dropdown ketika mengklik di luar area dropdown
    // window.onclick = function (event) {
    //     if (!event.target.matches('#profileBtn')) {
    //         var dropdowns = document.getElementsByClassName("dropdown-content");
    //         for (var i = 0; i < dropdowns.length; i++) {
    //             var openDropdown = dropdowns[i];
    //             if (openDropdown.style.display === "block") {
    //                 openDropdown.style.display = "none";
    //             }
    //         }
    //     }
    // }
});

// $(document).ready(function () {
//     // Optional: Clear modal fields when it's closed
//     $('#editProfil').on('hidden.bs.modal', function () {
//         $(this).find('input').val(''); // Reset input fields
//     });

//     $('#editEmailModal').on('hidden.bs.modal', function () {
//         $(this).find('input').val(''); // Reset input fields
//     });

//     $('#editTelpModal').on('hidden.bs.modal', function () {
//         $(this).find('input').val(''); // Reset input fields
//     });

//     // Additional logic for handling form submissions or validations can be added here
// });