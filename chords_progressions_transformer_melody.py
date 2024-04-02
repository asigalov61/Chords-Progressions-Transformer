# -*- coding: utf-8 -*-
"""Chords_Progressions_Transformer_Melody.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/13YJSFR0K6Wxa_mX5HCKADwEDns6X7HIS

# Chords Progressions Transformer Melody (ver. 1.0)

***

Powered by tegridy-tools: https://github.com/asigalov61/tegridy-tools

***

WARNING: This complete implementation is a functioning model of the Artificial Intelligence. Please excercise great humility, care, and respect. https://www.nscai.gov/

***

#### Project Los Angeles

#### Tegridy Code 2024

***

# (GPU CHECK)
"""

#@title NVIDIA GPU check
!nvidia-smi

"""# (SETUP ENVIRONMENT)"""

#@title Install dependencies
!git clone --depth 1 https://github.com/asigalov61/Chords-Progressions-Transformer
!pip install huggingface_hub
!pip install einops
!pip install torch-summary
!apt install fluidsynth #Pip does not work for some reason. Only apt works

# Commented out IPython magic to ensure Python compatibility.
#@title Import modules

print('=' * 70)
print('Loading core Chords Progressions Transformer modules...')

import os
import copy
import pickle
import secrets
import statistics
from time import time
import tqdm

print('=' * 70)
print('Loading main Chords Progressions Transformer modules...')
import torch

# %cd /content/Chords-Progressions-Transformer

import TMIDIX

from midi_to_colab_audio import midi_to_colab_audio

from x_transformer_1_23_2 import *

import random

# %cd /content/
print('=' * 70)
print('Loading aux Chords Progressions Transformer modules...')

import matplotlib.pyplot as plt

from torchsummary import summary
from sklearn import metrics

from IPython.display import Audio, display

from huggingface_hub import hf_hub_download

from google.colab import files

print('=' * 70)
print('Done!')
print('Enjoy! :)')
print('=' * 70)

"""# (LOAD MODEL)"""

#@title Load Chords Progressions Transformer Pre-Trained Model

#@markdown Model precision option

model_precision = "bfloat16" # @param ["bfloat16", "float16"]

#@markdown bfloat16 == Half precision/faster speed (if supported, otherwise the model will default to float16)

#@markdown float16 == Full precision/fast speed

plot_tokens_embeddings = False # @param {type:"boolean"}

print('=' * 70)
print('Loading Chords Progressions Transformer Melody Pre-Trained Model...')
print('Please wait...')
print('=' * 70)

full_path_to_models_dir = "/content/Chords-Progressions-Transformer/Models"

dim = 1024
depth = 4
heads = 8

model_checkpoint_file_name = 'Chords_Progressions_Transformer_Melody_Trained_Model_31061_steps_0.3114_loss_0.9002_acc.pth'
model_path = full_path_to_models_dir+'/Melody/'+model_checkpoint_file_name
if os.path.isfile(model_path):
  print('Model already exists...')

else:
  hf_hub_download(repo_id='asigalov61/Chords-Progressions-Transformer',
                  filename=model_checkpoint_file_name,
                  local_dir='/content/Chords-Progressions-Transformer/Models/Melody',
                  local_dir_use_symlinks=False)


print('=' * 70)
print('Instantiating model...')

device_type = 'cuda'

if model_precision == 'bfloat16' and torch.cuda.is_bf16_supported():
  dtype = 'bfloat16'
else:
  dtype = 'float16'

if model_precision == 'float16':
  dtype = 'float16'

ptdtype = {'bfloat16': torch.bfloat16, 'float16': torch.float16}[dtype]
ctx = torch.amp.autocast(device_type=device_type, dtype=ptdtype)

SEQ_LEN = 4096 # Models seq len
PAD_IDX = 449 # Models pad index

# instantiate the model

model = TransformerWrapper(
    num_tokens = PAD_IDX+1,
    max_seq_len = SEQ_LEN,
    attn_layers = Decoder(dim = dim, depth = depth, heads = heads, attn_flash = True)
    )

model = AutoregressiveWrapper(model, ignore_index = PAD_IDX, pad_value=PAD_IDX)

model.cuda()
print('=' * 70)

print('Loading model checkpoint...')

model.load_state_dict(torch.load(model_path))
print('=' * 70)

model.eval()

print('Done!')
print('=' * 70)

print('Model will use', dtype, 'precision...')
print('=' * 70)

# Model stats
print('Model summary...')
summary(model)

# Plot Token Embeddings
if plot_tokens_embeddings:
  tok_emb = model.net.token_emb.emb.weight.detach().cpu().tolist()

  cos_sim = metrics.pairwise_distances(
    tok_emb, metric='cosine'
  )
  plt.figure(figsize=(7, 7))
  plt.imshow(cos_sim, cmap="inferno", interpolation="nearest")
  im_ratio = cos_sim.shape[0] / cos_sim.shape[1]
  plt.colorbar(fraction=0.046 * im_ratio, pad=0.04)
  plt.xlabel("Position")
  plt.ylabel("Position")
  plt.tight_layout()
  plt.plot()
  plt.savefig("/content/Chords-Progressions-Transformer-Tokens-Embeddings-Plot.png", bbox_inches="tight")

"""# (GENERATE)"""

#@title Load Seed MIDI

#@markdown Press play button to to upload your own seed MIDI or to load one of the provided sample seed MIDIs from the dropdown list below

select_seed_MIDI = "Upload your own custom MIDI" # @param ["Upload your own custom MIDI", "Chords-Progressions-Transformer-Piano-Seed-1", "Chords-Progressions-Transformer-Piano-Seed-2", "Chords-Progressions-Transformer-Piano-Seed-3", "Chords-Progressions-Transformer-Piano-Seed-4", "Chords-Progressions-Transformer-Piano-Seed-5", "Chords-Progressions-Transformer-Piano-Seed-6", "Chords-Progressions-Transformer-MI-Seed-1", "Chords-Progressions-Transformer-MI-Seed-2", "Chords-Progressions-Transformer-MI-Seed-3", "Chords-Progressions-Transformer-MI-Seed-4", "Chords-Progressions-Transformer-MI-Seed-5", "Chords-Progressions-Transformer-MI-Seed-6"]
render_MIDI_to_audio = False # @param {type:"boolean"}

print('=' * 70)
print('Chords Progressions Transformer Seed MIDI Loader')
print('=' * 70)

f = ''

if select_seed_MIDI != "Upload your own custom MIDI":
  print('Loading seed MIDI...')
  f = '/content/Chords-Progressions-Transformer/Seeds/'+select_seed_MIDI+'.mid'

else:
  print('Upload your own custom MIDI...')
  print('=' * 70)
  uploaded_MIDI = files.upload()
  if list(uploaded_MIDI.keys()):
    f = list(uploaded_MIDI.keys())[0]

if f != '':

  print('=' * 70)
  print('File:', f)
  print('=' * 70)

  #=======================================================
  # START PROCESSING

  raw_score = TMIDIX.midi2single_track_ms_score(open(f, 'rb').read())

  raw_escore = TMIDIX.advanced_score_processor(raw_score, return_enhanced_score_notes=True)[0]

  raw_escore = [e for e in raw_escore if e[3] != 9]

  escore = TMIDIX.augment_enhanced_score_notes(raw_escore)

  cscore = TMIDIX.chordify_score([1000, escore])

  chords_tokens = []
  cho_toks = []

  for c in cscore:
    tones_chord = sorted(set([t[4] % 12 for t in c]))

    try:
      chord_token = TMIDIX.ALL_CHORDS_SORTED.index(tones_chord)
    except:
      chord_token = TMIDIX.ALL_CHORDS_SORTED.index(TMIDIX.check_and_fix_tones_chord(tones_chord))

    cho_toks.append(chord_token+128)

    if cho_toks:
      if len(cho_toks) > 1:

        chords_tokens.append(cho_toks)
        cho_toks = [cho_toks[-1]]

  cho_toks = cho_toks + cho_toks

  chords_tokens.append(cho_toks)
  #=======================================================

  song = raw_escore
  song_f = []

  time = 0
  dur = 0
  vel = 90
  pitch = 0
  channel = 0

  patches = [0] * 16

  channel = 0

  for ss in song:

    time = ss[1]

    dur = ss[2]

    pitch = ss[4]

    vel = ss[5]

    song_f.append(['note', time, dur, channel, pitch, vel, 0])

  detailed_stats = TMIDIX.Tegridy_ms_SONG_to_MIDI_Converter(song_f,
                                                          output_signature = 'Chords Progressions Transformer',
                                                          output_file_name = '/content/Chords-Progressions-Transformer-Seed-Composition',
                                                          track_name='Project Los Angeles',
                                                          list_of_MIDI_patches=patches
                                                          )

  #=======================================================

  print('=' * 70)
  print('Composition stats:')
  print('Composition has', len(cscore), 'chords')
  print('Composition has', len(chords_tokens), 'chords tokens')
  print('=' * 70)

  print('Displaying resulting composition...')
  print('=' * 70)

  fname = '/content/Chords-Progressions-Transformer-Seed-Composition'

  if render_MIDI_to_audio:
    midi_audio = midi_to_colab_audio(fname + '.mid')
    display(Audio(midi_audio, rate=16000, normalize=False))

  TMIDIX.plot_ms_SONG(song_f, plot_title=fname)

else:
  print('=' * 70)

# @title Generate chords progressions melody from custom MIDI chords

#@markdown NOTE: You can stop the generation at any time to render partial results

#@markdown Generation settings

melody_MIDI_patch_number = 40 # @param {type:"slider", min:0, max:127, step:1}
chords_MIDI_patch_number = 0 # @param {type:"slider", min:0, max:127, step:1}
chords_duration = 32 # @param {type:"slider", min:4, max:128, step:4}
number_of_chords_to_generate_melody_for = 128 # @param {type:"slider", min:8, max:4096, step:1}
max_number_of_melody_notes_per_chord = 4 # @param {type:"slider", min:1, max:10, step:1}
number_of_memory_tokens = 4096 # @param {type:"slider", min:32, max:8188, step:4}
temperature = 0.9 # @param {type:"slider", min:0.1, max:1, step:0.05}

#@markdown Other settings

render_MIDI_to_audio = True # @param {type:"boolean"}

#===============================================================================

print('=' * 70)
print('Chords Progressions Transformer Melody Model Generator')
print('=' * 70)

torch.cuda.empty_cache()

output = []

for i in tqdm.tqdm(range(len(chords_tokens[:number_of_chords_to_generate_melody_for]))):
  try:

    output.extend(chords_tokens[i])

    o = 0

    count = 0

    while o < 128 and count < max_number_of_melody_notes_per_chord:

      x = torch.LongTensor([[output]]).cuda()

      with ctx:
          out = model.generate(x[-number_of_memory_tokens:],
                              1,
                              temperature=temperature,
                              return_prime=False,
                              verbose=False)

      o = out.tolist()[0][0]

      if o < 128:
        output.append(o)
        count += 1

  except KeyboardInterrupt:
    print('=' * 70)
    print('Stopping generation...')
    break

  except Exception as e:
    print('=' * 70)
    print('Error:', e)
    break

torch.cuda.empty_cache()

#===============================================================================
print('=' * 70)

out1 = output

print('Sample INTs', out1[:12])
print('=' * 70)

patches = [0] * 16

patches[3] = melody_MIDI_patch_number
patches[0] = chords_MIDI_patch_number

if len(output) != 0:

    song = output
    song_f = []

    time = 0
    dur = 10
    vel = 90
    pitch = 0
    channel = 0

    song1 = []
    ptc = []
    cho = []

    for s in song:
      if s < 128:
        ptc.append(s)
      else:
        if ptc:
          grp = [cho, ptc]
          song1.append(grp)
          cho = []
          ptc = []

        cho.append(s)

    for ss in song1:

      tones_chord = TMIDIX.ALL_CHORDS_SORTED[(ss[0][0]-128)]

      dur = chords_duration

      for t in tones_chord:
        song_f.append(['note', time * 16, dur * 16, 0, 60+t, vel, chords_MIDI_patch_number])
        song_f.append(['note', time * 16, dur * 16, 0, 48+t, vel, chords_MIDI_patch_number])

      ptc_count = len(ss[1])
      ptc_time_dur = dur // ptc_count

      for p in ss[1]:
        song_f.append(['note', time * 16, ptc_time_dur * 16, 3, p, vel, melody_MIDI_patch_number])
        time += ptc_time_dur

    detailed_stats = TMIDIX.Tegridy_ms_SONG_to_MIDI_Converter(song_f,
                                                            output_signature = 'Chords Progressions Transformer',
                                                            output_file_name = '/content/Chords-Progressions-Transformer-Composition',
                                                            track_name='Project Los Angeles',
                                                            list_of_MIDI_patches=patches
                                                            )



    print('=' * 70)
    print('Displaying resulting composition...')
    print('=' * 70)

    fname = '/content/Chords-Progressions-Transformer-Composition'

    if render_MIDI_to_audio:
      midi_audio = midi_to_colab_audio(fname + '.mid')
      display(Audio(midi_audio, rate=16000, normalize=False))

    TMIDIX.plot_ms_SONG(song_f, plot_title=fname)

"""# Congrats! You did it! :)"""