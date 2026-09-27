#!/bin/zsh
# UGV-01 tanıtım filmi: müzik + ses (music.py), CAD'den film sayfası (build_film.py), kare kare yakalama (render.mjs),
# ffmpeg ile birleştirme. Çıktı: media/film/out/UGV-01_tanitim.mp4 (git dışı). Kareler FRAMES altında (varsayılan /tmp).
set -e
cd "${0:A:h}"
FRAMES=${FRAMES:-/tmp/ugv-film-frames}
PORT=8777
python3 music.py
uv run --no-project --with pyworld --with 'setuptools<81' --with numpy --with scipy python music.py --vocal  # sung version (vocals.py, WORLD vocoder)
../../.venv/bin/python build_film.py
python3 -m http.server $PORT --bind 127.0.0.1 --directory out >/dev/null 2>&1 &
SERVER=$!
trap "kill $SERVER 2>/dev/null" EXIT
sleep 1
node render.mjs "http://127.0.0.1:$PORT/film.html" "$FRAMES"
for pair in "score:UGV-01_tanitim" "score_vocal:UGV-01_tanitim_sarkili"; do
  ffmpeg -v error -y -framerate 30 -i "$FRAMES/f%05d.jpg" -i "out/${pair%%:*}.wav" \
    -c:v libx264 -preset slow -tune film -crf 20 -maxrate 14M -bufsize 28M -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart -shortest \
    "out/${pair##*:}.mp4"
  echo "out/${pair##*:}.mp4"
done
mkdir -p audio
ffmpeg -v error -y -i out/score.wav -c:a libmp3lame -b:a 192k audio/UGV-01_swing_enstrumantal.mp3
ffmpeg -v error -y -i out/score_vocal.wav -c:a libmp3lame -b:a 192k audio/UGV-01_swing_sarkili.mp3
