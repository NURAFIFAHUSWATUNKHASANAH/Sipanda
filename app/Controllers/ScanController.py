# from keras.models import load_model  # Gunakan keras, bukan tensorflow.keras
# from keras.preprocessing import image
# import numpy as np
# import os
# import logging
# from PIL import Image

# # Path ke model
# MODEL_PATH = 'app/Controllers/deteksi3_kategorikal.h5'

# # Cek apakah file model ada
# if not os.path.exists(MODEL_PATH):
#     raise FileNotFoundError(f'Model file tidak ditemukan di {MODEL_PATH}')

# # Load model hanya sekali di awal
# model = load_model(MODEL_PATH, compile=False)

# # Logging
# logging.basicConfig(level=logging.INFO)

# # Info spesies
# species_info = {
#     "Badak Jawa": {
#         "status": "DILINDUNGI",
#         "latin_name": "Rhinoceros sondaicus",
#         "habitat": "Hutan hujan tropis di Jawa Barat",
#         "description": "Badak Jawa adalah salah satu spesies badak yang paling terancam punah di dunia. Saat ini hanya ditemukan di Taman Nasional Ujung Kulon, Banten."
#     },
#     "Beruang Madu": {
#         "status": "DILINDUNGI",
#         "latin_name": "Ursus malayanus",
#         "habitat": "Hutan tropis di Asia Tenggara",
#         "description": "Beruang madu adalah spesies beruang yang terancam punah, dengan ciri khas bulu leher yang berbentuk sabuk berwarna kuning keemasan."
#     },
#     "Burung Cendrawasih": {
#         "status": "DILINDUNGI",
#         "latin_name": "Paradisaeidae",
#         "habitat": "Hutan hujan tropis Papua dan sekitarnya",
#         "description": "Burung cendrawasih terkenal karena keindahan bulu-bulunya yang memukau, dan menjadi simbol keanekaragaman hayati Indonesia."
#     },
#     "Burung Maleo": {
#         "status": "DILINDUNGI",
#         "latin_name": "Macrocephalon maleo",
#         "habitat": "Hutan tropis Sulawesi",
#         "description": "Burung Maleo adalah spesies burung endemik Sulawesi yang terkenal dengan cara bertelurnya yang unik, yaitu dengan cara menanamkan telur ke dalam pasir panas."
#     },
#     "Harimau Sumatra": {
#         "status": "DILINDUNGI",
#         "latin_name": "Panthera tigris sumatrae",
#         "habitat": "Hutan tropis Sumatra",
#         "description": "Harimau Sumatra adalah subspesies harimau yang hanya ditemukan di pulau Sumatra dan saat ini terancam punah akibat perusakan habitat."
#     },
#     "Komodo": {
#         "status": "DILINDUNGI",
#         "latin_name": "Varanus komodoensis",
#         "habitat": "Pulau Komodo, Flores, dan sekitarnya",
#         "description": "Komodo adalah kadal terbesar di dunia yang hanya ditemukan di beberapa pulau di Indonesia. Spesies ini dikenal karena kekuatan dan kemampuan berburu yang luar biasa."
#     },
#     "Macan Tutul Jawa": {
#         "status": "DILINDUNGI",
#         "latin_name": "Panthera pardus melas",
#         "habitat": "Hutan tropis di Jawa",
#         "description": "Macan Tutul Jawa adalah subspesies harimau tutul yang hanya ditemukan di pulau Jawa, Indonesia, dan terancam punah karena perusakan habitat."
#     },
#     "Merak Hijau": {
#         "status": "DILINDUNGI",
#         "latin_name": "Pavo muticus",
#         "habitat": "Hutan tropis Asia Tenggara",
#         "description": "Merak Hijau adalah burung besar dengan bulu ekor yang indah, ditemukan di hutan tropis di Asia Tenggara, dan termasuk dalam spesies yang dilindungi."
#     },
#     "Orangutan Kalimantan": {
#         "status": "DILINDUNGI",
#         "latin_name": "Pongo pygmaeus",
#         "habitat": "Hutan tropis Kalimantan",
#         "description": "Orangutan Kalimantan adalah spesies primata yang hanya ditemukan di pulau Kalimantan. Mereka sangat terancam punah akibat deforestasi dan perburuan."
#     },
#     "Trenggiling": {
#         "status": "DILINDUNGI",
#         "latin_name": "Manis javanica",
#         "habitat": "Hutan tropis di Asia Tenggara",
#         "description": "Trenggiling adalah mamalia yang memiliki sisik keras dan sering diburu untuk perdagangan ilegal. Mereka termasuk dalam spesies yang dilindungi di banyak negara."
#     },
#     "Ikan Koi": {
#         "status": "TIDAK DILINDUNGI",
#         "latin_name": "Cyprinus rubrofuscus",
#         "habitat": "Kolam dan danau di Asia Timur",
#         "description": "Ikan Koi adalah jenis ikan hias yang populer, sering ditemukan dalam kolam dan danau taman Jepang."
#     },
#     "Ikan Cupang": {
#         "status": "TIDAK DILINDUNGI",
#         "latin_name": "Betta splendens",
#         "habitat": "Perairan payau dan sungai di Asia Tenggara",
#         "description": "Ikan cupang dikenal karena keindahan siripnya dan agresivitas antar sesama jenis. Mereka banyak dipelihara sebagai ikan hias."
#     },
#     "Cicak": {
#         "status": "TIDAK DILINDUNGI",
#         "latin_name": "Gekkonidae",
#         "habitat": "Daerah tropis di seluruh dunia",
#         "description": "Cicak adalah reptil kecil yang sering ditemukan di sekitar rumah. Mereka tidak dilindungi karena keberadaannya yang melimpah."
#     },
#     "Burung Perkutut": {
#         "status": "TIDAK DILINDUNGI",
#         "latin_name": "Geopelia striata",
#         "habitat": "Hutan dan pemukiman di Asia Tenggara",
#         "description": "Burung Perkutut adalah burung kecil yang banyak dipelihara sebagai burung peliharaan di Indonesia."
#     }
# }

# class_names = list(species_info.keys())  # Daftar nama kelas

# def deteksi(image_path):
#     try:
#         # Preprocessing gambar
#         img = image.load_img(image_path, target_size=(224, 224))
#         img_array = image.img_to_array(img) / 255.0
#         img_array = np.expand_dims(img_array, axis=0)

#         # Prediksi
#         predictions = model.predict(img_array)
#         predicted_class = np.argmax(predictions, axis=1)[0]

#         # Validasi indeks
#         if predicted_class >= len(class_names):
#             return {
#                 "error": "Predicted class index out of range.",
#                 "predicted_class_index": predicted_class
#             }

#         predicted_label = class_names[predicted_class]
#         species_data = species_info.get(predicted_label, {
#             "status": "Tidak Diketahui",
#             "latin_name": "Tidak Diketahui",
#             "habitat": "Tidak Diketahui",
#             "description": "Tidak ada deskripsi yang tersedia."
#         })

#         return {
#             "predicted_label": predicted_label,
#             "confidence": round(float(predictions[0][predicted_class]), 4),
#             "species_info": species_data
#         }

#     except Exception as e:
#         return {
#             "error": str(e),
#             "message": "Terjadi kesalahan saat memproses gambar."
#         }


from ultralytics import YOLO
import os
import logging

# Path ke model YOLOv8 hasil training
MODEL_PATH = "app/model/sipanda.pt"

# Pastikan model ada
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model YOLO tidak ditemukan di {MODEL_PATH}")

# Load model YOLO hanya sekali di awal
model = YOLO(MODEL_PATH)

# Logging
logging.basicConfig(level=logging.INFO)

# Informasi status dan deskripsi tiap spesies
species_info = {
    "Bekantan": {
        "status": "DILINDUNGI",
        "latin_name": "Nasalis larvatus",
        "habitat": "Hutan mangrove dan rawa di Kalimantan",
        "description": "Bekantan dikenal dengan hidung panjang pada jantan dan merupakan primata endemik Kalimantan yang populasinya menurun akibat deforestasi dan perburuan."
    },
    "Beruang Madu": {
        "status": "DILINDUNGI",
        "latin_name": "Helarctos malayanus",
        "habitat": "Hutan tropis Asia Tenggara termasuk Sumatra dan Kalimantan",
        "description": "Beruang madu adalah spesies beruang terkecil di dunia, dikenal dengan tanda berwarna kuning di dada dan populasinya terancam oleh kehilangan habitat."
    },
    "Cendrawasih Botak": {
        "status": "DILINDUNGI",
        "latin_name": "Cicinnurus respublica",
        "habitat": "Hutan dataran rendah di Pulau Waigeo dan Batanta, Papua Barat",
        "description": "Cendrawasih Botak adalah burung endemik Papua Barat dengan kepala biru terang dan tubuh merah, dikenal karena keindahan tarian kawinnya."
    },
    "Gelatik Jawa": {
        "status": "DILINDUNGI",
        "latin_name": "Padda oryzivora",
        "habitat": "Sawah dan padang rumput di Pulau Jawa dan Bali",
        "description": "Gelatik Jawa adalah burung kecil pemakan biji yang endemik Jawa dan terancam punah akibat perburuan untuk perdagangan burung hias."
    },
    "Kakatua Jambul Kuning": {
        "status": "DILINDUNGI",
        "latin_name": "Cacatua sulphurea",
        "habitat": "Hutan kering, savana, dan daerah pantai di Nusa Tenggara dan Sulawesi",
        "description": "Kakatua Jambul Kuning memiliki jambul kuning khas dan merupakan spesies burung endemik Indonesia yang sangat terancam punah."
    },
    "Kasturi Kepala Hitam": {
        "status": "DILINDUNGI",
        "latin_name": "Lorius lory",
        "habitat": "Hutan hujan Papua dan pulau-pulau sekitarnya",
        "description": "Kasturi Kepala Hitam adalah burung paruh bengkok berwarna cerah dengan kepala hitam pekat, sangat aktif dan mudah dikenali suaranya."
    },
    "Kasturi Ternate": {
        "status": "DILINDUNGI",
        "latin_name": "Lorius garrulus",
        "habitat": "Hutan tropis di Kepulauan Maluku Utara, termasuk Ternate dan Halmahera",
        "description": "Kasturi Ternate memiliki bulu merah cerah dengan corak ungu dan hijau, merupakan burung endemik Maluku yang populasinya menurun karena perdagangan ilegal."
    },
    "Kukang Jawa": {
        "status": "DILINDUNGI",
        "latin_name": "Nycticebus javanicus",
        "habitat": "Hutan tropis dan hutan sekunder di Jawa Barat",
        "description": "Kukang Jawa adalah primata kecil nokturnal dengan mata besar, bergerak lambat, dan dilindungi karena terancam oleh perdagangan satwa liar."
    },
    "Landak Jawa": {
        "status": "DILINDUNGI",
        "latin_name": "Hystrix javanica",
        "habitat": "Hutan tropis dan pegunungan di Jawa dan Bali",
        "description": "Landak Jawa memiliki duri panjang tajam sebagai pertahanan diri dan kini populasinya menurun akibat perburuan serta kerusakan habitat."
    },
    "Owa Jawa": {
        "status": "DILINDUNGI",
        "latin_name": "Hylobates moloch",
        "habitat": "Hutan pegunungan di Jawa Barat dan Tengah",
        "description": "Owa Jawa adalah primata arboreal dengan suara panggilan khas, hidup berpasangan, dan sangat terancam punah karena fragmentasi hutan."
    }
}


def deteksi(image_path):
    """
    Fungsi deteksi menggunakan model YOLOv8.
    Mengembalikan label, confidence, dan informasi spesies.
    """
    try:
        # Jalankan prediksi dengan YOLO
        results = model.predict(source=image_path, conf=0.25)

        if not results or len(results[0].boxes) == 0:
            return {"error": "Tidak ada objek terdeteksi."}

        detections = []
        for box in results[0].boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            label = model.names[cls_id]

            info = species_info.get(label, {
                "status": "Tidak Diketahui",
                "latin_name": "Tidak Diketahui",
                "habitat": "Tidak Diketahui",
                "description": "Tidak ada deskripsi yang tersedia."
            })

            detections.append({
                "label": label,
                "confidence": round(conf, 3),
                "species_info": info
            })

        return {"detections": detections}

    except Exception as e:
        return {"error": str(e)}
