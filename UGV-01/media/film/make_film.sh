#!/bin/zsh
# UGV-01 tanıtım filmi: müzik + ses (music.py), CAD'den film sayfası (build_film.py), kare kare yakalama (render.mjs),
# ffmpeg ile birleştirme. Çıktı: media/film/out/UGV-01_tanitim.mp4 (git dışı). Kareler FRAMES altında (varsayılan /tmp).
set -e
cd "${0:A:h}"
FRAMES=${FRAMES:-/tmp/ugv-film-frames}
PORT=8777
python3 music.py
../../.venv/bin/python build_film.py
python3 -m http.server $PORT --bind 127.0.0.1 --directory out >/dev/null 2>&1 &
SERVER=$!
trap "kill $SERVER 2>/dev/null" EXIT
sleep 1
node render.mjs "http://127.0.0.1:$PORT/film.html" "$FRAMES"
ffmpeg -v error -y -framerate 30 -i "$FRAMES/f%05d.jpg" -i out/score.wav \
  -c:v libx264 -preset slow -tune film -crf 20 -maxrate 14M -bufsize 28M -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart -shortest \
  out/UGV-01_tanitim.mp4
echo "out/UGV-01_tanitim.mp4"
