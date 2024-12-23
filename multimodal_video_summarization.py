# -*- coding: utf-8 -*-
"""MultiModal_Video_Summarization.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/github/Dada-Tech/multimodal-video-summarization-educational-content/blob/main/MultiModal_Video_Summarization.ipynb

# Configuration
"""

import os
import subprocess

notebook_mode = "auto"
dev_mode = False

# Notebook Mode: Auto-detect Google Colab instance
notebook_mode = (True if 'COLAB_GPU' in os.environ else False) if notebook_mode == "auto" else notebook_mode
print(f"""Notebook Mode: {notebook_mode}""")

def print_section(message):
  """Prints a section separator with a custom message embedded.

  Args:
    message: The message to embed within the separator.
  """
  separator_length = 40
  separator_char = "="

  # Calculate padding for the message
  message_length = len(message)
  padding = (separator_length - message_length - 2) // 2
  padding = max(padding, 0)

  # Separator line
  top_line = separator_char * separator_length

  # Message line
  message_line = separator_char * padding + " " + message + " " + separator_char * padding
  if len(message_line) == 39:
    message_line += separator_char
  message_line = message_line[:separator_length]

  print(top_line)
  print(message_line)
  print(top_line,'\n')


def print_info(message, preview = None, max_length=80):
  print(f"""\n=== {message}\n""")
  if preview:
    print("--- Preview:")
    print(preview[:max_length] + "..." if len(preview) > max_length else preview)


def notebook_mode_print(message_or_df):
  if notebook_mode:
    display(message_or_df) if isinstance(message_or_df, pd.DataFrame) else print(message_or_df)

def dev_mode_print(message):
  if dev_mode:
    print(message)

"""# Installation & Setup"""

if notebook_mode:
    print_section("installing deps")

    # download requirements.txt from repository
    subprocess.run(["curl", "-O", "https://raw.githubusercontent.com/Dada-Tech/multimodal-video-trimming/main/requirements.txt"], check=True)

    subprocess.check_call(['python', '-m', 'pip', 'install', '--no-cache-dir', '-r', 'requirements.txt'])

    print_info("installation done.")
else:
    print_info("skipping installation")

from pydantic import BaseModel, validator, conint, confloat, ValidationError
from enum import Enum
import argparse

class ModelSize(Enum):
    BASE = "base"
    LARGE = "large"

class AutoSummary(BaseModel):
    summary_length_percentage: confloat(ge=0.2, le=0.5)
    min_summary_length: conint(ge=30, le=60)
    max_summary_length: conint(ge=100, le=1000)

class DeletionMetric(BaseModel):
    threshold: confloat(ge=0.2, le=0.5)

class Metric1(BaseModel):
    model_size: ModelSize

class Hyperparameters(BaseModel):
    auto_summary: AutoSummary
    deletion_metric: DeletionMetric
    metric_1: Metric1

"""# Inputs & Hyperparameters

### Auto Summary

*   **`summary_length_percentage`**: 0.3
    *   Determines the target length of the summary as a percentage of the original text length.
*   **`min_summary_length`**: 30
    *   Sets the minimum number of words (or tokens) allowed in the summary.
*   **`max_summary_length`**: 600
    *   Sets the maximum number of words (or tokens) allowed in the summary.

### Deletion Metric

*   **`threshold`**: 0.3
    *   The minimum relevance score a sentence needs to have to be included in the final output. Sentences below this threshold are considered for removal.
"""

if notebook_mode:
  video_input = "dataset/teamwork in the classroom.mov"
  video_export_max_length_seconds = 0 # set develop video max length to export a shortened version of the multimedia

  # original was max_length=150, min_length=30
  hyperparameters = {
      "auto_summary": {
        "summary_length_percentage": 0.3,
        "min_summary_length": 30,
        "max_summary_length": 600
      },
      "deletion_metric": {
          "threshold": 0.3
      },
      "metric_1": {
          "model_size": ModelSize.BASE
      }
  }

else:
  # Define the argparse parser
  parser = argparse.ArgumentParser(description="Process video and hyperparameters.")

  # Define the arguments for the inputs
  parser.add_argument("--video_export_max_length_seconds", type=int, default=0, help="Maximum length of the video to export (in seconds)")
  parser.add_argument("--video_input", type=str, required=True, help="Path to the video input file")

  # Hyperparameters as individual arguments
  parser.add_argument("--auto_summary_summary_length_percentage", type=float, default=0.3, help="Summary length as a percentage")
  parser.add_argument("--auto_summary_min_summary_length", type=int, default=30, help="Minimum summary length")
  parser.add_argument("--auto_summary_max_summary_length", type=int, default=600, help="Maximum summary length")
  parser.add_argument("--deletion_metric_threshold", type=float, default=0.3, help="Threshold for deletion metric")
  parser.add_argument("--metric_1_model_size", type=str, choices=["base", "large"], default="base", help="Model size for metric 1")

  parser.add_argument("--install", action="store_true", help="Installation dependencies in requirements.txt")

  # Parse arguments
  args = parser.parse_args()

  # Now you can use the parsed arguments
  video_export_max_length_seconds = args.video_export_max_length_seconds
  video_input = args.video_input

  hyperparameters = {
      "auto_summary": {
          "summary_length_percentage": args.auto_summary_summary_length_percentage,
          "min_summary_length": args.auto_summary_min_summary_length,
          "max_summary_length": args.auto_summary_max_summary_length
      },
      "deletion_metric": {
          "threshold": args.deletion_metric_threshold
      },
      "metric_1": {
          "model_size": args.metric_1_model_size
      }
  }



# Validate Hyperparameters
try:
    validated_hyperparameters = Hyperparameters(**hyperparameters)
except ValidationError as e:
    print(f"Hyperparameter validation error: {e}")

    print_info("exiting...")
    os._exit(1)

"""# Imports


"""

print_info("importing...")

import os
import numpy as np
import pandas as pd
import tarfile
import gdown
import re
from functools import reduce
import subprocess

# ML General
from datasets import load_dataset
import torch
import torchaudio
import torch.nn.functional as F
from transformers import \
LongformerTokenizer, LongformerModel, LongformerForSequenceClassification, LongformerConfig, \
RobertaTokenizer, RobertaForTokenClassification, TrainingArguments, \
LEDTokenizer, LEDForConditionalGeneration

# Text
import pytextrank
import nltk
from nltk.tokenize import sent_tokenize
import spacy
import srt

# Audio
import whisperx
import silero_vad
from silero_vad import load_silero_vad, read_audio, get_speech_timestamps
from pydub import AudioSegment

# Video
import ffmpeg

print_info("importing done")

print_info("downloading NLTK libraries...")

nltk.download('punkt')
nltk.download('punkt_tab')

print_info("downloading done")

"""# Variables"""

full_base = os.path.dirname(video_input)
path_dataset = full_base
filename = os.path.basename(video_input)
filename_without_extension = os.path.splitext(filename)[0]
filename_video_extension = video = os.path.splitext(video_input)[1]


filename_video_input = filename
filename_subtitles_output = filename_without_extension + ".srt"
filename_audio_output = filename_without_extension + ".wav"
filename_audio_output_skimmed = filename_without_extension + "_skimmed.wav"
filename_video_output_skimmed = filename_without_extension + "_skimmed" + filename_video_extension

subtitles_output = os.path.join(full_base, filename_subtitles_output)
audio_output = os.path.join(full_base, filename_audio_output)
audio_output_skimmed = os.path.join(full_base, filename_audio_output_skimmed)
video_output_skimmed = os.path.join(full_base, filename_video_output_skimmed)

video = ''
audio = ''
subtitles = ''
sentences = ''

"""# Functions"""

def drop_if_exists(df, col_name):
  """Drops a column from a DataFrame if it exists
  Args:
    df: The pandas DataFrame to modify.
    col_name: The name of the column to drop and insert.
  """
  if col_name in df.columns:
    df.drop(col_name, axis=1, inplace=True)

# # Test Question-Answering Evaluation

# from transformers import pipeline

# # Load the question-answering pipeline
# qa_pipeline = pipeline(
#     "question-answering",
#     # model="distilbert-base-cased-distilled-squad"
#     model="valhalla/longformer-base-4096-finetuned-squadv1"
#   )

# # Example texts
# unsummarized_text = """
# Albert Einstein was a theoretical physicist born in Germany. He developed the theory of relativity,
# one of the two pillars of modern physics. He won the Nobel Prize in Physics in 1921.
# """

# summarized_text = """
# Einstein, a German physicist, developed relativity and won the 1921 Nobel Prize.
# """

# # Define a list of questions to ask
# questions = [
#     "Who developed the theory of relativity?",
#     "When did he win the Nobel Prize?",
#     "Where was he born?"
# ]

# # Function to get answers from a given text
# def evaluate_qa(text, questions):
#     answers = {}
#     for question in questions:
#         result = qa_pipeline(question=question, context=text)
#         answers[question] = result['answer']
#     return answers

# # Get answers for both texts
# answers_unsummarized = evaluate_qa(unsummarized_text, questions)
# answers_summarized = evaluate_qa(summarized_text, questions)

# # Compare the answers
# print("Answers from Unsummarized Text:")
# for q, a in answers_unsummarized.items():
#     print(f"{q} -> {a}")

# print("\nAnswers from Summarized Text:")
# for q, a in answers_summarized.items():
#     print(f"{q} -> {a}")

"""# Datasets

- teamwork in the classroom.mov - `190MB`
- flipped learning basics.mov - `380MB`
- assessing students without exams.mov - `830MB`
"""

if notebook_mode:
  from google.colab import files

  # Google Drive Dataset Location
  folder_id = '1k7DLJPl1xz9lpU4l3dZYtPe1XawhrXeC' # taken from drive.google.com/drive/u/1/folders/1k7D...(this part)
  gdown.download_folder(id=folder_id, quiet=False, use_cookies=False)

"""# Preprocessing"""

print_section("Preprocessing")

"""## Audio - Extract"""

# Extract audio (wav) from video
# !ffmpeg -y -i "$video_input" -vn -acodec pcm_s16le -ar 44100 -ac 2 "$audio_output"
print_info("extracting audio from video")

subprocess.run(['ffmpeg', '-y', '-i', video_input, '-vn', '-acodec', 'pcm_s16le', '-ar', '44100', '-ac', '2', audio_output], check=True)
# subprocess.run(["ffmpeg", '-y', '-i', video_input, '-vn', '-acodec', 'pcm_s16le', '-ar', '44100', '-ac', '2', audio_output], check=True, capture_output=True)

"""## Audio - SRT File Generation

##### Time Taken: ~4min

SRT  
each **`subtitle`** in the subtitles array has the following properties:

1. **`index`**
   - The sequential number of the subtitle within the SRT file.
   - `1`, `2`, `3`, etc. (Integer)
2. **`start`**
   - The time (in milliseconds) when the subtitle should appear on the screen.
   - `00:00:05,000` (String representing HH:MM:SS,SSS)
3. **`end`**
   - The time (in milliseconds) when the subtitle should disappear from the screen.
   - `00:00:10,000` (String representing HH:MM:SS,SSS)
4. **`content`**
   - The actual text of the subtitle that will be displayed.
   - "Hello, world!" (String)
5. **`proprietary`**
   - This field holds any additional data or formatting specific to the SRT file or software used to create it. Often empty and can usually be ignored.
   - `''` (Empty string, or sometimes contains specific formatting codes)
"""

def seconds_to_srt_timestamp(seconds):
    """
    Extract hours, minutes, seconds, and milliseconds
    from a given number of seconds.
    """

    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = seconds % 60
    milliseconds = int((seconds - int(seconds)) * 1000)

    # Format as HH:MM:SS,MS
    return f"{hours:02}:{minutes:02}:{int(seconds):02},{milliseconds:03}"

# Select device (GPU if available, otherwise CPU)
language="en"

from multiprocessing import Queue

# GPU
if torch.cuda.is_available():
  device = "cuda"
  compute_type = "float16"
  batch_size = 16
  model_whisperx = "base"

  print_info(f"""Generating SRT File with {device}...""")
else:
  device = "cpu"
  compute_type = "int8"
  batch_size = 1
  model_whisperx = "tiny"

  queue = Queue(maxsize=200)

  print_info(f"""WARNING: Generating SRT File with {device}...""")


# Model WhisperX
model = whisperx.load_model(model_whisperx, device=device, language=language, compute_type=compute_type) # Choose "base" or "large" model

# Transcribe audio
aligned_segments = model.transcribe(audio_output, batch_size=batch_size)

# Align with forced alignment
alignment_model, metadata = whisperx.load_align_model(language_code=aligned_segments["language"], device=device)
aligned_segments = whisperx.align(aligned_segments["segments"], alignment_model, metadata, audio_output, device)

# Generate SRT file with aligned sentences
with open(subtitles_output, "w") as f:
    for i, segment in enumerate(aligned_segments["segments"], 1):
        # Get start and end times in SRT format
        start_time = seconds_to_srt_timestamp(segment["start"])
        end_time = seconds_to_srt_timestamp(segment["end"])

        # Write SRT entry
        f.write(f"{i}\n{start_time} --> {end_time}\n{segment['text']}\n\n")

print_info("SRT file generated", subtitles_output)

"""## Text - Load SRT File"""

# Subtitles:
with open(subtitles_output, "r", encoding="utf-8") as f:
    subtitles = list(srt.parse(f.read()))

"""## Text - Sentence Segmentation"""

def format_timedelta(timedelta_obj):
    """Formats a datetime.timedelta object into HH:MM:SS.mmm timestamp.

    Args:
        timedelta_obj: The datetime.timedelta object.

    Returns:
        A string representing the timestamp in HH:MM:SS.mmm format.
    """
    total_seconds = timedelta_obj.total_seconds()
    hours = int(total_seconds // 3600)  # Get hours
    minutes = int((total_seconds % 3600) // 60)  # Get minutes
    seconds = int(total_seconds % 60)  # Get seconds
    milliseconds = int((total_seconds % 1) * 1000)  # Get milliseconds

    return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}"

sentences = []
for i, segment in enumerate(subtitles):
    sentences.append({
        'base_idx': i,
        'start_time': format_timedelta(segment.start),
        'end_time': format_timedelta(segment.end),
        'sentence': segment.content
    })

df_sentences = pd.DataFrame(sentences)
sentences = df_sentences['sentence'].tolist()

notebook_mode_print(df_sentences)

"""## Text - Paragraph
combination of all subtitle parts.  

WhisperAI enhances transcription with basic punctuation.
"""

paragraph = reduce(lambda acc, seg: acc + seg.strip() + ' ', sentences, '')

# Print the paragraph
notebook_mode_print(paragraph)
print_info("paragraph sample", paragraph)

"""## Text - Paragraph Summarized

##### Time Taken: ~1min
"""

print_info("Summarizing Paragraph")

# Model: Longformer Encoder-Decoder
model_name = "allenai/led-base-16384"
tokenizer = LEDTokenizer.from_pretrained(model_name)
model = LEDForConditionalGeneration.from_pretrained(model_name)
text = paragraph

# Tokenization
inputs = tokenizer(text, return_tensors="pt", max_length=4096, truncation=True)

# Calculate dynamic summary length
summary_length_percentage = hyperparameters["auto_summary"]["summary_length_percentage"]
min_summary_length = hyperparameters["auto_summary"]["min_summary_length"]
max_summary_length = hyperparameters["auto_summary"]["max_summary_length"]


input_length = len(inputs["input_ids"][0])
summary_length = int(input_length * summary_length_percentage)
summary_length = max(min_summary_length, min(summary_length, max_summary_length))

# Summary Generation
summary_ids = model.generate(
    inputs["input_ids"],
    max_length=summary_length,
    min_length=min_summary_length,
    length_penalty=1.2,
    num_beams=4,
    early_stopping=True
)

paragraph_summarized = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
print_info("paragraph summarized", paragraph_summarized)

# Simple Metrics
print_info("Simple Metrics")

original_length = len(paragraph)
summary_length = len(paragraph_summarized)

print(f"original length: {original_length}")
print(f"summary length: {summary_length}")

summarization_ratio = (original_length - summary_length) / original_length
print(f"Summarized/Original Length Ratio: {summarization_ratio:.2f}")

"""# Text

## Metric 1: Sentence- Summarized Paragraph Relevancy (Cosine Similarity)

##### Time Taken: ~2min
"""

print_section("Metric 1: Sentence-Summarized Relevancy")

# config
attention_window = 256
model_size = hyperparameters["metric_1"]["model_size"].value
model_name_lf = f'allenai/longformer-{model_size}-4096'
config = LongformerConfig.from_pretrained(model_name_lf, attention_window=attention_window)

# model: Longformer
model_lf = LongformerModel.from_pretrained(model_name_lf, config=config)
tokenizer_lf = LongformerTokenizer.from_pretrained(model_name_lf, model_max_length=attention_window)

# 2: Tokenization
paragraph_tokens = tokenizer_lf(paragraph_summarized, return_tensors='pt')
# sentence_tokens = [tokenizer_lf(sentence, return_tensors='pt') for sentence in sentences]

sentence_tokens = tokenizer_lf(sentences, padding=True, truncation=True, return_tensors='pt')

# 3: Embedding
with torch.no_grad():  # Disable gradient computation for efficiency
    paragraph_embedding = model_lf(**paragraph_tokens).last_hidden_state[:, 0, :]  # Get the [CLS] token embedding

    # Process batched sentence tokens
    sentence_embeddings = model_lf(**sentence_tokens).last_hidden_state[:, 0, :]

"""Embedding Explanation  
The [CLS] (classification) token is often used in transformer models to represent the overall meaning or summary of the input sequence. By extracting its embedding, you're essentially obtaining a representation that captures the main point or essence of the paragraph.
"""

# 4: Relevance scores
relevance_scores = [torch.cosine_similarity(paragraph_embedding, sentence_embedding).item() for sentence_embedding in sentence_embeddings]

# Normalization: min-max normalization
min_score = min(relevance_scores)
max_score = max(relevance_scores)
normalized_scores = [(score - min_score) / (max_score - min_score) for score in relevance_scores]

# round
normalized_scores = [np.format_float_positional(score, precision=2, unique=False, fractional=False, trim='k') for score in normalized_scores]

# 5: Display Results
drop_if_exists(df_sentences, "metric_1_score")
df_sentences.insert(0, "metric_1_score", normalized_scores)

notebook_mode_print(df_sentences)

# Interactive Sheet for easy exporting
# from google.colab import sheets
# sheet = sheets.InteractiveSheet(df=df_sentences)

"""## Metric 2: Intra-sentence relevancy
Score by if current sentence is needded by adjacent sentences.
"""

# from transformers import BertForSequenceClassification, BertTokenizer

# # Load pre-trained model and tokenizer
# model = BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=2)
# tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

# # Store predictions for each sentence
# predictions = []

# # Iterate through sentence pairs
# for i in range(len(sentences) - 1):
#     sentence1 = sentences[i]
#     sentence2 = sentences[i + 1]

#     # Tokenize and prepare input
#     inputs = tokenizer(sentence1, sentence2, return_tensors='pt', truncation=True, padding=True, add_special_tokens=True)

#     # Get model prediction
#     outputs = model(**inputs)
#     prediction = torch.argmax(outputs.logits).item()

#     # Store prediction
#     predictions.append(prediction)

# # Handle last sentence (no next sentence)
# predictions.append(0)  # Assume last sentence doesn't need a next sentence

# # Add predictions to DataFrame
# df_sentences = df_sentences.assign(**{"Previous Sentence Needed": predictions})

# display(df_sentences)

"""## Metric 3: Intelligent Sentence-Paragraph Relevancy

##### Time Taken: 13min - 26min
"""

# tokenizer = LongformerTokenizer.from_pretrained("allenai/longformer-base-4096")
# model = LongformerForSequenceClassification.from_pretrained("allenai/longformer-base-4096")

# # Ensure the model is in evaluation mode
# model.eval()

# # Example usage
# body_paragraph = paragraph

# relevance_scores = []

# for sentence in sentences:
#     # Prepare the input for Longformer
#     inputs = tokenizer(
#         body_paragraph,
#         sentence,
#         return_tensors='pt',
#         max_length=4096,
#         truncation=True,
#         padding='max_length'  # Pad to max length to avoid issues with model input size
#     )

#     # Get model predictions
#     with torch.no_grad():
#         outputs = model(**inputs)

#     # Assuming binary classification (relevant/not relevant)
#     relevance_score = torch.softmax(outputs.logits, dim=1)[0][1].item()  # Probability of being relevant
#     relevance_scores.append((sentence, relevance_score))

# # Sort sentences based on relevance scores
# sorted_sentences = sorted(relevance_scores, key=lambda x: x[1], reverse=True)
# ranked_sentences = [sentence for sentence, score in sorted_sentences]

# relevance_scores[0]

# sentence_indices = list(range(len(relevance_scores)))
# scores = [score for sentence, score in relevance_scores]
# sentences_text = [sentence for sentence, score in relevance_scores]

# df_relevance = pd.DataFrame({'Sentence Index': sentence_indices, 'Score': scores, 'Sentence': sentences_text})
# df_relevance

"""## Metric 4: Keyword extraction and Ranking
using TextRank
"""

# # Load a spaCy model
# nlp = spacy.load("en_core_web_sm")

# # Add the pytextrank pipeline component to spaCy
# nlp.add_pipe("textrank")

# phrase_data = []

# # Process the text
# doc = nlp(paragraph)

# for phrase in doc._.phrases:
#   phrase_data.append([phrase.text, phrase.rank, phrase.count])

# df_phrases = pd.DataFrame(phrase_data, columns=['Phrase', 'Rank', 'Count'])
# df_phrases.sort_values(by=['Rank'], ascending=False, inplace=True)

# display(df_phrases)

"""# Audio

## Metric 5: Silence Detection
* From the Paragraph boundaries, get the time in aduio that we care about
* For each time in audio we care about, analyze if they are low volume

OR
* analyze all potential sentence boundaries first
* match with end of sentences
"""

# # 0: Load audio, extract timestamps

# SAMPLING_RATE = 16000 # 16 kHz

# model = load_silero_vad()
# wav = read_audio(audio_output)
# speech_timestamps = get_speech_timestamps(wav, model)

# # Check the shape of the wav tensor
# print(f"Audio shape: {wav.shape}")
# print(f"Audio length (seconds): {len(wav) / SAMPLING_RATE:.2f}")

# # Speech Intervals
# speech_intervals = []
# for i in range(0, len(speech_timestamps)-1):
#     speech_intervals.append((speech_timestamps[i]['start'] / SAMPLING_RATE, speech_timestamps[i]['end'] / SAMPLING_RATE))

# # Silence Intervals
# silence_intervals = []
# for i in range(1, len(speech_timestamps)):
#     silence_start = speech_timestamps[i-1]['end']  # End of previous speech segment
#     silence_end = speech_timestamps[i]['start']     # Start of current speech segment
#     silence_intervals.append((silence_start / SAMPLING_RATE, silence_end / SAMPLING_RATE))

# notebook_mode_print(speech_timestamps[0:3])
# notebook_mode_print(speech_intervals[0:3])
# notebook_mode_print(silence_intervals[0:3])

"""# Video

# Final Score - Metric Weighting
"""

# Add Final Metric Column
drop_if_exists(df_sentences, "metric_final")
df_sentences.insert(0, "metric_final", 1)

# Metric 1 Apply
df_sentences['metric_final'] = 1 * df_sentences['metric_final'] * df_sentences['metric_1_score'].astype(float)


notebook_mode_print(df_sentences)

"""### Deletion Metric"""

# Threshold
threshold = hyperparameters['deletion_metric']['threshold']

filtered_df_to_keep = df_sentences[df_sentences['metric_final'] >= threshold]
filtered_df_to_delete = df_sentences[df_sentences['metric_final'] < threshold]
filtered_df = filtered_df_to_keep

# Percentage
# percentage_cutoff = 0.2
# percentile_20 = df_sentences['metric_final'].quantile(0.2)
# filtered_df = df_sentences[df_sentences['metric_final'] <= percentile_20]

# Timestamps
# sample_timestamps = [('00:00:00.00','00:00:01.25'), ('00:00:08.766', '00:00:11.042')]
sentence_timestamps = list(zip(filtered_df['start_time'], filtered_df['end_time']))


notebook_mode_print(sentence_timestamps)

"""### Text to Keep"""

notebook_mode_print(filtered_df_to_keep[['metric_final', 'start_time', 'end_time', 'sentence']])

text_to_keep = " ".join(filtered_df_to_keep['sentence'].tolist())

notebook_mode_print(text_to_keep)

"""### Text to Delete"""

notebook_mode_print(filtered_df_to_delete[['metric_final', 'start_time', 'end_time', 'sentence']])

text_to_delete = " ".join(filtered_df_to_delete['sentence'].tolist())

notebook_mode_print(text_to_delete)

"""# PostProcessing

#### Time Taken: ~1.5min
6min video: ~2min to process, ~30sec to download
"""

print_section("Postprocessing")

def ts_to_s(timestamp):
    """Converts a timestamp string in HH:MM:SS.mmm format to seconds.

    Args:
        timestamp: The timestamp string in HH:MM:SS.mmm format.

    Returns:
        The timestamp in seconds as a float.
    """
    hours, minutes, seconds_milliseconds = re.split(r':', timestamp)
    seconds, milliseconds = seconds_milliseconds.split('.')

    # Convert to seconds
    total_seconds = int(hours) * 3600 + int(minutes) * 60 + int(seconds) + int(milliseconds) / 1000.0

    return total_seconds

def skim_video(input_video, output_video, segments_to_retain):
    """
    Skims a video by keeping only the specified segments and removes others.

    Args:
        input_video (str): Path to the input video file.
        output_video (str): Path to the output video file.
        segments_to_retain (list of tuples): List of tuples where each tuple contains
                                             (start_time, end_time) in seconds to retain.
    """
    print_info("Processed video...")

    # Prepare the select filter for video (only select the specified ranges)
    video_select_filter = '+'.join([
        f"between(t,{start},{end})"
        for start, end in segments_to_retain
    ])

    # Prepare the select filter for audio (only select the specified ranges)
    audio_select_filter = '+'.join([
        f"between(t,{start},{end})"
        for start, end in segments_to_retain
    ])

    # Construct the ffmpeg command with the specified filters
    ffmpeg_command = [
        "ffmpeg",
        "-y",
        "-i", input_video,
        "-vf", f"select='{video_select_filter}',setpts=N/FRAME_RATE/TB",
        "-af", f"aselect='{audio_select_filter}',asetpts=N/SR/TB",
        "-threads", str(os.cpu_count()),
         "-preset", "ultrafast",
        output_video
    ]

    # Run the FFmpeg command and capture the output
    result = subprocess.run(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Check if FFmpeg finished successfully or if there were errors
    if result.returncode != 0:
        print("FFmpeg Error:")
        print(result.stderr.decode())  # Print the error output
    else:
        print_info("Video processed successfully.")

def get_video_length(input_video):
    """Get the duration (length) of a video file using ffmpeg-python."""
    probe = ffmpeg.probe(input_video, v='error', select_streams='v:0', show_entries='format=duration')
    return float(probe['format']['duration'])

# def get_video_length(video_input):

#     # Run ffmpeg to get video information
#     result = subprocess.run([ffmpeg, '-i', video_input], stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)

#     # Extract duration from stderr output
#     stderr_output = result.stderr
#     for line in stderr_output.split('\n'):
#         if 'Duration' in line:
#             # Extract the duration: 'Duration: hh:mm:ss.xx'
#             duration_str = line.split(',')[0].split('Duration: ')[1].strip()
#             h, m, s = map(float, duration_str.split(':'))
#             return h * 3600 + m * 60 + s  # Convert to seconds
#     return 0  # Return 0 if duration is not found

def generate_keep_timestamps(timestamps_to_remove, video_length=None):
    """
    Given a list of timestamps to remove from a video, generates the list of timestamps to keep.

    Args:
        timestamps_to_remove (list of tuples): List of segments to remove (start_time, end_time) in seconds.
        video_length (float, optional): Total length of the video in seconds. If not provided, the last segment's end is used.

    Returns:
        list of tuples: Segments to keep.
    """
    # Sort the timestamps to remove by their start times (just in case they're out of order)
    timestamps_to_remove.sort()

    # Initialize the list of segments to keep
    timestamps = []

    # If the first removal starts after 0, keep from the start of the video to the first removal
    if timestamps_to_remove[0][0] > 0:
        timestamps.append((0.0, timestamps_to_remove[0][0]))

    # Now, for each consecutive pair of timestamps to remove, keep the time between them
    for i in range(len(timestamps_to_remove) - 1):
        end_of_previous_removal = timestamps_to_remove[i][1]
        start_of_next_removal = timestamps_to_remove[i + 1][0]

        # If there's a gap, keep that gap
        if end_of_previous_removal < start_of_next_removal:
            timestamps.append((end_of_previous_removal, start_of_next_removal))

    # If there is time left after the last removal, keep it
    if video_length is not None:
        last_end_time = timestamps_to_remove[-1][1]
        if last_end_time < video_length:
            timestamps.append((last_end_time, video_length))

    return timestamps

# Timestamp pre-processing
original_video_length = get_video_length(video_input)

# Dev mode: export shorter video
video_length = min(original_video_length, video_export_max_length_seconds) if video_export_max_length_seconds > 0 else original_video_length

# Trim Method 1: Video with sentences to remove, removed
# timestamps_to_remove = list(map(lambda x: (ts_to_s(x[0]), ts_to_s(x[1])), sentence_timestamps))
# timestamps_to_keep = generate_keep_timestamps(timestamps_to_remove, video_length)

# Trim method 2: Video of only sentences to keep
timestamps_to_keep = list(map(lambda x: (ts_to_s(x[0]), ts_to_s(x[1])), sentence_timestamps))

# print(f"Timestamps to remove: {timestamps_to_remove}")
notebook_mode_print(f"Timestamps to keep: {timestamps_to_keep}")

# Skim Video
skim_video(video_input, video_output_skimmed, timestamps_to_keep)

# Download
print_info("Downloading video...")

files.download(video_output_skimmed)

# Simple Metrics
print_section("Simple Metrics")

original_video_length = get_video_length(video_input)
print(f"Original Video Length: {original_video_length:.2f}s\n")

skimmed_video_length = get_video_length(video_output_skimmed)
print(f"Skimmed Video Length: {skimmed_video_length:.2f}s\n")

summarization_ratio = (original_video_length - skimmed_video_length) / original_video_length
print(f"Summarized/Original Video Length Ratio: {summarization_ratio:.2f}")