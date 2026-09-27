# Üretim alanı

Henüz üretim release'i yok. STL/STEP/DXF kavram dosyaları `cad/assembly/generated` altında tutulur; buradaki üretim klasörleri bilerek boş. `bom/initial_bom.csv` satın alma listesi değil ön bütçe ve aday listesidir.

PH4 release: her PN/revizyon için malzeme, kalınlık, tolerans, datum, yüzey işlemi, STEP ve teknik resim; baskılarda STL/3MF, yön/nozzle/layer ve kupon sonucu; metalde gerekiyorsa DXF.

PH7 release: KiCad kaynakları, ERC/DRC, üretici stackup, Gerber, drill, BOM/refdes, PnP, assembly drawing, üretim/test notları ve checksum manifesti. Konektör terminal/crimp ve kablo boyları montaj BOM'una dahil edilir.
