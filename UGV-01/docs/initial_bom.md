# İlk BOM ve maliyet kapsamı

Asıl dosya: [initial_bom.csv](../manufacturing/bom/initial_bom.csv). 22.09.2026, USD, vergi/kargo/ithalat/işçilik dışarıda. Yalnız CM5 fiyatı üretici brief'inde görülen195 USD referanstır; diğer bedeller **mühendislik bütçe tahmini**, canlı teklif değildir. Yerel stok teyidi yapılmadı. Sipariş verilmedi.

V1 satırları toplamı **2082 USD**; %30 prototip/sarf payıyla yaklaşık **2707 USD**. A2 ile iki göz kamerası, dört servo, pan rulmanı, ışık şeridi, iki ToF, kamera kabloları ve servo buck V1'e alındı (+83 USD; [A2 elektronik](a2_electronics.md)); A1 toplamı 1999 USD idi. Laboratuvar ekipmanı, tasarım işçiliği, başarısız PCB revizyonları, LiDAR ve diğer otonomi sensörleri dahil değildir. DETAIL_INCLUDED satırları kartların içeriğini gösterir, maliyet toplamına tekrar eklenmez. FUTURE satırları da V1 toplamı dışında.

Motor/CM5/MCU/driver/hücre için gerçek üretici adayları var. BMS, kesici, kamera, servo, direnç, rulman gibi kritik açık MPN'ler kesin seçilmiş gibi gösterilmez. Alternatifler otomatik pin veya mekanik uyum anlamına gelmez. Tam üretim BOM'u PH4/5/6'daki şematik ve çizimlerden refdes, terminal ve bağlantı elemanı düzeyinde üretilecek.
