# History Shorts (Daily Dose of Wow: YouTube Shorts + Instagram Reels)

Narrated "Forgotten stories from India" Shorts, 30-40 s, English narration with an Indian accent.
One render goes to YouTube (Short) and to the Instagram page @your.dailydoseofwow (Reel).
Only the narration costs Runway credits (~1 credit per 50 characters, ~8-9 per Short). Everything else is free.

## Pipeline
1. **Script** (70-85 words, ~30-35 s). Line 1 is a hook that stops the scroll. Plain, accurate English.
   Last line: `Follow for more forgotten stories from India.` Split the script into caption chunks at every
   sentence end and every comma, in speaking order, and save as `captions.json` (list of strings).
2. **Voice**: Runway `generate_speech` with voice `Arjun`, model `eleven_multilingual_v2`, languageCode `en`,
   speed `1.05`, text = the script with a line break after each sentence. Poll `get_task` for the mp3 URL.
3. **Download**: the Runway CDN is blocked in the sandbox. Pass the URL to Orshot `orshot_upload_brand_audio`
   (`file` = URL, tags `voiceover`, `history-shorts`), then `curl -o vo.mp3 <storage.orshot.com URL>`.
4. **Audio prep**: `python3 tools/history/audio.py vo.mp3 captions.json WORKDIR`
   -> `voice.wav` (narration only, tightened pauses), `mix_yt.wav` (narration + very soft self-made drone),
   `timeline.json` (caption timings). It prints whether timing is `exact` (one speech part per caption chunk)
   or `proportional`; both are fine, exact is better.
5. **Scenes**: copy `examples/moksha_patam.py` to a new file outside the repo and rewrite the scenes for the
   new topic (big title text, a simple drawn motif, Devanagari words where natural, a punchy final word, then
   the CTA scene "FORGOTTEN STORIES FROM INDIA / Follow for more / DAILY DOSE OF WOW"). Map each scene to the
   caption indices it covers. Keep all scene text between y=150 and y=1350 (captions sit at ~1450-1600; the
   bottom ~320 px and the right ~120 px are covered by app buttons).
6. **Preview**: `python3 that.py WORKDIR prev.jpg --preview t1,t2,...` (one time per scene) and Read the image.
   Nothing may overlap or be cut off; fix and preview again.
7. **Render both versions** (~2 min each):
   `python3 that.py WORKDIR reels/history/<slug>_yt.mp4 --audio mix_yt` and
   `python3 that.py WORKDIR reels/history/<slug>_ig.mp4 --audio voice`.
   Check frames with ffmpeg (`ffmpeg -ss 10 -i x.mp4 -frames:v 1 f.png`) and Read them.
8. **Host**: commit the two mp4 files to branch `post-images` (never `main`) and push. URLs:
   `https://raw.githubusercontent.com/anjaltiwari1994/daily-dose-of-gita/post-images/reels/history/<file>.mp4`
9. **Schedule in Metricool** (brand blogId 7323490, timezone Asia/Calcutta), see the scheduled task prompt:
   YouTube Short with the `_yt` file; Instagram Reel with the `_ig` file plus Instagram library music via
   `instagramData.audioConfiguration` (`audioId` numeric, `audioVolume` 15, `videoVolume` 100).
   If the search term matches several tracks, Metricool returns candidates: pick a calm, fitting instrumental
   and retry with its numeric id.

Music rule (owner's decision): narration must stay clearly on top. YouTube gets only the very soft self-made
drone baked in (copyright free); Instagram gets only the low-volume library track. Never both.

Fonts in `fonts/` are SIL Open Font License (Cinzel, Inter, Playfair Display, Tiro Devanagari Sanskrit, Poppins).
