
"""Transcribe a video (Whisper) and build a JSONL dataset for Llama-3.2 Instruct.

This script does 3 things:
 1) Extracts audio with ffmpeg
 2) Runs ASR (openai-whisper OR faster-whisper) to produce transcript.txt
 3) Builds dataset JSONL using the same deterministic rules as build_dataset_from_transcript.py

Usage examples:
  # Option A: openai-whisper (GPU optional)
  pip install -U openai-whisper ffmpeg-python

  python transcribe_video_and_build_dataset.py \
    --video video.mp4 \
    --backend whisper \
    --whisper_model small \
    --language es \
    --out_jsonl dataset_audio.jsonl

  # Option B: faster-whisper (recommended for speed)
  pip install -U faster-whisper

  python transcribe_video_and_build_dataset.py \
    --video video.mp4 \
    --backend faster \
    --faster_model small \
    --language es \
    --out_jsonl dataset_audio.jsonl

Requirements:
- ffmpeg installed and available in PATH.
- One of: openai-whisper OR faster-whisper.

"""

import argparse
import subprocess
from pathlib import Path
import sys

def run(cmd):
  p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
  if p.returncode != 0:
    raise RuntimeError(f"Command failed ({p.returncode}): {' '.join(cmd)}\n{p.stderr}")
  return p

def extract_audio(video: Path, wav_out: Path):
  cmd = [
    "ffmpeg", "-y", "-i", str(video),
    "-vn", "-ac", "1", "-ar", "16000", "-f", "wav", str(wav_out)
  ]
  run(cmd)

def transcribe_whisper(wav: Path, out_txt: Path, model_name: str, language: str):
  try:
    import whisper
  except Exception as e:
    raise RuntimeError("openai-whisper not installed. Install with: pip install -U openai-whisper") from e

  model = whisper.load_model(model_name)
  res = model.transcribe(str(wav), language=language, fp16=False)
  text = (res.get("text") or "").strip()
  out_txt.write_text(text + "\n", encoding="utf-8")
  return text

def transcribe_faster(wav: Path, out_txt: Path, model_name: str, language: str):
  try:
    from faster_whisper import WhisperModel
  except Exception as e:
    raise RuntimeError("faster-whisper not installed. Install with: pip install -U faster-whisper") from e

  # device selection: cuda if available; otherwise cpu
  device = "cuda" if "--cuda" in sys.argv else "cpu"
  compute_type = "float16" if device == "cuda" else "int8"
  model = WhisperModel(model_name, device=device, compute_type=compute_type)
  segments, info = model.transcribe(str(wav), language=language, vad_filter=True)

  parts = []
  for seg in segments:
    if seg.text:
      parts.append(seg.text.strip())
  text = " ".join(parts).strip()
  out_txt.write_text(text + "\n", encoding="utf-8")
  return text

def build_dataset(transcript_txt: Path, out_jsonl: Path):
  # reuse the deterministic builder from the companion script
  builder = Path(__file__).with_name("build_dataset_from_transcript.py")
  if not builder.exists():
    raise RuntimeError("Missing build_dataset_from_transcript.py in the same folder.")
  run([sys.executable, str(builder), "--transcript", str(transcript_txt), "--out", str(out_jsonl)])

def main():
  ap = argparse.ArgumentParser()
  ap.add_argument("--video", required=True, help="Input video path (mp4, etc.)")
  ap.add_argument("--backend", choices=["whisper", "faster"], default="whisper")
  ap.add_argument("--whisper_model", default="small")
  ap.add_argument("--faster_model", default="small")
  ap.add_argument("--language", default="es")
  ap.add_argument("--out_jsonl", required=True)
  ap.add_argument("--workdir", default=".")
  ap.add_argument("--cuda", action="store_true", help="(faster-whisper) use CUDA if available")
  args = ap.parse_args()

  video = Path(args.video)
  workdir = Path(args.workdir)
  workdir.mkdir(parents=True, exist_ok=True)

  wav = workdir / (video.stem + "_16k.wav")
  transcript = workdir / (video.stem + "_transcript.txt")

  extract_audio(video, wav)

  if args.backend == "whisper":
    transcribe_whisper(wav, transcript, args.whisper_model, args.language)
  else:
    transcribe_faster(wav, transcript, args.faster_model, args.language)

  build_dataset(transcript, Path(args.out_jsonl))
  print(f"OK: {args.out_jsonl}")

if __name__ == "__main__":
  main()
