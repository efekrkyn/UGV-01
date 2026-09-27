# ROS 2 çalışma alanı

Dokuz paket ve arayüzler [yazılım mimarisi](../../docs/software_architecture.md) içinde. Şu anda paket uygulaması yok; geometri ön modeli [simulation/ugv_geometry.urdf](../../simulation/ugv_geometry.urdf) ortak ölçü dosyasından üretilir. PH9'da Xacro, collision/inertial, launch, package.xml, CMake/setup ve simülasyon entegrasyonu gelir.

A2 (24.09.2026): ROS dışı, test edilmiş Python AI katmanı `software/ugv_ai/` ([ai_control.md](../../docs/ai_control.md)); ROS düğümüne sarılması alt proje 5'te.
