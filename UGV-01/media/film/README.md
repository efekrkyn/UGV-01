# UGV-01 tanıtım filmi

91 s, 1920×1080, 30 fps. Baştan sona kodla üretilir; tek bir hazır görsel ya da ses örneği yoktur:

- **Görüntü:** robot, projenin gerçek CAD modelidir (`tools/build_viewer.py` ağları, 96 parça, eklem zinciri). `film_template.html` her kareyi `renderAt(t)` ile belirlenimci çizer: robotun sürüşü (tekerler kat edilen yola göre döner), kamera yolları ve müziğin vuruşlarına oturan kesmeler, kol duruş grafiği, patlatılmış görünüm, X-ışını, sesli komut ve AI araç çağrılarını gösteren operatör paneli, ağırlık merkezi, imzalı paketler, E-stop, 36 kontrol ve ampullü tabela. Sayılar projeden gelir; kontrol listesi `tests/README.md`'den okunur.
- **Müzik:** `music.py` numpy ile 60'lar big band swing'i sentezler: kontrbas yürüyüşü, ride ve fırçalar, parmak şıklatma, sürdinli trompet, 4 sesli brass ve saksafon armonileri (fall-off'larla), vibrafon köprüsü; 132 BPM, Fa majör, final chorus Sol majöre çıkar ve button vuruşuyla biter. "Dur" anında orkestra susar. Melodi ve akorlar özgündür, hiçbir şarkıdan alınmamıştır.
- **Ses:** operatörün sesli komutları ("Mavi küpü al, kutuya koy.", "Dur!") ve robotun sözleri ("Merhaba.", "Küp kutuda.", "Hazırım.") macOS `say` Yelda sesinden üretilir; robotunki tizleştirilip hafifçe robotlaştırılır.
- **Şarkılı sürüm:** `vocals.py` (`music.py --vocal`), README'deki sözleri robotun kendisine söyletir. Her kelime macOS `say` (Daniel) ile okunur, özgün vokal melodinin notalarına sündürülür ve taşıyıcısı melodiyi izleyen 24 bantlı bir kanal vokoderinden geçer: portamento, uzun notalarda vibrato, "vintage mikrofon" rengi ve slap-back yankı. Notalar hedefin ±6 cent yakınında ölçüldü. Kıtalar grup ve mühendislik bölümlerinde, "say the word stop…" köprüsü güven bölümünde; son "alone" Sol majöre geçişin üstünde tutulur. Nakarat shout chorus'ta, "that's the little machine" kapanışta. AI bölümü operatör komutları duyulsun diye sözsüzdür. Açılış anonsu (Ralph): "Ladies and gentlemen… the little machine!". Aranje vokal için değişir: melodiyi çalan trompet ve saksafon, satır aralarında cevap, pedler ve brass vuruşlarına çekilir.
- **Müzik dosyaları:** `audio/UGV-01_swing_enstrumantal.mp3` ve `audio/UGV-01_swing_sarkili.mp3` (91 s, 192 kbps).
- **Senkron:** `timeline.json` tek saattir. Müzik, yazılar, kol, baş ve kamera aynı dosyadan beslenir.

Robot, projenin kuralı gereği özgün tasarım UGV-01 olarak anlatılır. Filmde başka bir karakterin adı, logosu ya da müziği kullanılmaz.

## Üretmek

```sh
zsh media/film/make_film.sh        # müzik (iki sürüm) → film sayfası → 2730 kare (Chrome, GPU) → out/UGV-01_tanitim.mp4 ve out/UGV-01_tanitim_sarkili.mp4
```

Gerekenler: ffmpeg, Node ≥22, Google Chrome, macOS `say` (Yelda), CAD sanal ortamı (`.venv`, cadquery). Kareler varsayılan olarak `/tmp/ugv-film-frames` altına yazılır (≈1 GB). Yazıyı, zamanlamayı ya da kamerayı değiştirmek için `timeline.json`'u düzenleyip betiği yeniden çalıştırmak yeter.

## Sözler ve isteğe bağlı insan sesli sürüm (Suno)

Şarkılı sürümde bu sözleri robot vokoderle söyler. İnsan sesli bir crooner sürümü istenirse aynı sözler ve stil Suno'ya verilebilir. Üretilen şarkı `out/score.wav` yerine konur (sesli komut ve robot sesleri istenirse üstüne yeniden karıştırılır) ve yalnız son ffmpeg adımı çalıştırılır. Suno ücretli ya da hesaplı bir hizmettir; kullanıcı kendisi üretir. Suno sanatçı adlarını kabul etmeyebilir; stil bu yüzden tarif edilir.

**Stil:** `1960s Las Vegas big band swing, smooth baritone crooner, brassy shout chorus with trumpet fall-offs, walking upright bass, brushed drums and finger snaps, muted trumpet fills, vibraphone bridge, key change up a whole step, button ending, 132 bpm, confident, witty, cool`

**Sözler (özgün):**

```
[Intro – drum roll, brass hit]
(spoken) Ladies and gentlemen... the little machine.

[A]
Four wheels rolling, nice and slow,
every turn counted, top to toe,
two glass eyes that read the room —
well, I clock the cube before you do.

[A]
Ninety-six parts, not one to spare,
swept every angle with the greatest care,
seven roads my arm can take,
and not one bump, for goodness' sake.

[Bridge – vibes, finger snaps]
You say "pick it up", I say "consider it done",
I look, I roll, I reach — one, two, and one,
but say the word "stop" and I'm still as a stone,
'cause the brakes, my friend, are yours alone.

[Shout chorus – up a step]
I'm small, but I'm something,
built right from the ground,
I sign every message
that I'm passing around,
keep my center low and my promises true —
that's the little machine, and it's rolling to you.

[Tag – button]
Next stop... the printer.
(spoken) Ready when you are.
```
