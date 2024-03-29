# -*- coding: utf-8 -*-
"""Chords_Progressions_Transformer_Aux_Maker.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1WOkuW3Kq4Xp2BNiaF7FNMqghuuz5mH8x

# Chords Progressions Transformer Aux Maker (ver. 1.0)

***

Powered by tegridy-tools: https://github.com/asigalov61/tegridy-tools

***

WARNING: This complete implementation is a functioning model of the Artificial Intelligence. Please excercise great humility, care, and respect. https://www.nscai.gov/

***

#### Project Los Angeles

#### Tegridy Code 2024

***

# (SETUP ENVIRONMENT)
"""

# @title NVIDIA GPU Check
!nvidia-smi

#@title Install all dependencies (run only once per session)
!git clone --depth 1 https://github.com/asigalov61/tegridy-tools
!pip install einops
!pip install torch-summary

# Commented out IPython magic to ensure Python compatibility.
#@title Import all needed modules

print('Loading modules...')

import os
import pickle
import secrets
import statistics
import tqdm
import math
import copy
import torch
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset

import matplotlib.pyplot as plt

from torchsummary import summary
from sklearn import metrics

# %cd /content/tegridy-tools/tegridy-tools/

import TMIDIX

# %cd /content/tegridy-tools/tegridy-tools/X-Transformer

from x_transformer_1_23_2 import *

torch.set_float32_matmul_precision('high')
torch.backends.cuda.matmul.allow_tf32 = True # allow tf32 on matmul
torch.backends.cudnn.allow_tf32 = True # allow tf32 on cudnn

# %cd /content/

if not os.path.exists('/content/Dataset'):
    os.makedirs('/content/Dataset')

if not os.path.exists('/content/INTS'):
    os.makedirs('/content/INTS')

import random

from joblib import Parallel, delayed, parallel_config

print('PyTorch version:', torch.__version__)
print('Done')

"""# (DOWNLOAD AND UNZIP MIDI DATASET)"""

# Commented out IPython magic to ensure Python compatibility.
# @title Download and unzip Beautiful Music Seeds MIDI Dataset
# %cd /content/Dataset
!wget https://github.com/asigalov61/Tegridy-MIDI-Dataset/raw/master/Beautiful-Music-Seeds-CC-BY-NC-SA.zip
!unzip Beautiful-Music-Seeds-CC-BY-NC-SA.zip
!rm Beautiful-Music-Seeds-CC-BY-NC-SA.zip
# %cd /content/

"""# (MIDI PROCESSOR)"""

#@title Load TMIDIX MIDI Processor

print('=' * 70)
print('Loading TMIDIX MIDI Processor...')
print('=' * 70)

def TMIDIX_MIDI_Processor(midi_file):

    melody_chords = []

    try:

        fn = os.path.basename(midi_file)

        #=======================================================
        # START PROCESSING

        raw_score = TMIDIX.midi2single_track_ms_score(midi_file)

        escore_notes = TMIDIX.advanced_score_processor(raw_score, return_enhanced_score_notes=True)[0]

        escore_notes = TMIDIX.augment_enhanced_score_notes(escore_notes)

        all_scores = []

        for pa in range(-6, 6):

          escore_paug = copy.deepcopy(escore_notes)

          for e in escore_paug:
            e[4] += pa

          cscore = TMIDIX.chordify_score([1000, escore_paug])

          chords = [321]

          for c in cscore:

            tones_chord = sorted(set([cc[4] % 12 for cc in c]))

            if tones_chord:

              try:
                chord_tok = TMIDIX.ALL_CHORDS_SORTED.index(tones_chord)
                chords.append(chord_tok)
              except:
                continue

          if chords:
            all_scores.append(chords)

        return all_scores

    except Exception as e:
      print('Error!')
      print('Exception', e)
      return None

print('Done!')
print('=' * 70)

"""# (FILE LIST)"""

#@title Save file list
###########

print('=' * 70)
print('Loading MIDI files...')
print('This may take a while on a large dataset in particular.')

dataset_addr = "/content/Dataset"

# os.chdir(dataset_addr)
filez = list()
for (dirpath, dirnames, filenames) in os.walk(dataset_addr):
    filez += [os.path.join(dirpath, file) for file in filenames]
print('=' * 70)

if not filez:
    print('Could not find any MIDI files. Please check Dataset dir...')
    print('=' * 70)

else:
  print('Randomizing file list...')
  random.shuffle(filez)
  print('Done!')
  print('=' * 70)
  print('Total files:', len(filez))
  print('=' * 70)

"""# (PROCESS MIDIs)"""

#@title Process MIDIs with TMIDIX MIDI processor

print('=' * 70)
print('TMIDIX MIDI Processor')
print('=' * 70)
print('Starting up...')
print('=' * 70)

###########

melody_chords_f = []

print('Processing MIDI files. Please wait...')
print('=' * 70)

for i in tqdm.tqdm(range(0, len(filez), 16)):

  with parallel_config(backend='threading', n_jobs=16, verbose = 0):

    output = Parallel()(delayed(TMIDIX_MIDI_Processor)(f) for f in filez[i:i+16])

    for o in output:

        if o is not None:
            melody_chords_f.append(o)

print('Done!')
print('=' * 70)

"""# (SAVE/LOAD PROCESSED MIDIs)"""

# @title Save processed MIDIs
TMIDIX.Tegridy_Any_Pickle_File_Writer(melody_chords_f, '/content/Processed_MIDIs')

# @title Load processed MIDIs
melody_chords_f = TMIDIX.Tegridy_Any_Pickle_File_Reader('/content/Processed_MIDIs')
print('Done!')

"""# (TEST PROCESSED MIDIs)"""

#@title Test Processed MIDIs

train_data1 = random.choice(melody_chords_f)[6]

#train_data1 = max(melody_chords_f, key = len)

print('Sample data:', train_data1[:15])

out = train_data1

patches = [0] * 16
patches[3] = 40

if len(out) != 0:

    song = out
    song_f = []

    time = 0
    dur = 0
    vel = 90
    pitch = 0
    channel = 0

    for ss in song[1:]:

        chord = TMIDIX.ALL_CHORDS_SORTED[ss]

        time += 200
        dur = 200

        for c in chord:

          ptc1 = 48+c
          ptc2 = 60+c

          song_f.append(['note', time, dur, channel, ptc1, vel ])
          song_f.append(['note', time, dur, channel, ptc2, vel ])

detailed_stats = TMIDIX.Tegridy_ms_SONG_to_MIDI_Converter(song_f,
                                                          output_signature = 'Chords Progressions Transformer',
                                                          output_file_name = '/content/Chords-Progressions-Transformer-Composition',
                                                          track_name='Project Los Angeles',
                                                          )

print('Done!')

"""# (PREP INTs)"""

# @title Convert processed MIDIs to INTs
SEQ_LEN = 1024
PAD_IDX = 322

print('=' * 70)

train_data = []

for m in tqdm.tqdm(melody_chords_f):
  for dat in m:

    dat = dat[:SEQ_LEN+1]
    dat += [PAD_IDX] * ((SEQ_LEN+1) - len(dat))

    train_data.append(dat)

# Total dict size 644

random.shuffle(train_data)

print('Done!')
print('=' * 70)
print(len(train_data), max(train_data, key=len) == min(train_data, key=len))
print('=' * 70)
print(len(max(train_data, key=len)), len(min(train_data, key=len)))
print('=' * 70)
print(train_data[0][:15])
print('=' * 70)

"""# (SAVE/LOAD INTs)"""

# @title Save INTs
TMIDIX.Tegridy_Any_Pickle_File_Writer(train_data, '/content/Training_INTs')

# @title Load INTs
train_data = TMIDIX.Tegridy_Any_Pickle_File_Reader('/content/Training_INTs')
print('Done!')

"""# (PREP MODEL)"""

# @title Setup and init the model

# constants

SEQ_LEN = 1024 # Models seq len
PAD_IDX = 322 # Models pad index

BATCH_SIZE = 32
NUM_EPOCHS = 200
GRADIENT_ACCUMULATE_EVERY = 1

LEARNING_RATE = 1e-4

VALIDATE_EVERY  = 100
SAVE_EVERY = 500
GENERATE_EVERY  = 100
PRINT_STATS_EVERY = 20

GENERATE_LENGTH = 32

# helpers

def cycle(loader):
    while True:
        for data in loader:
            yield data

# instantiate the model

model = TransformerWrapper(
    num_tokens = PAD_IDX+1,
    max_seq_len = SEQ_LEN,
    attn_layers = Decoder(dim = 1024, depth = 4, heads = 16, attn_flash = True)
    )

model = AutoregressiveWrapper(model, ignore_index=PAD_IDX)

model.cuda()

print('Done!')

summary(model)

# Dataloader

class MusicDataset(Dataset):
    def __init__(self, data, seq_len):
        super().__init__()
        self.data = data
        self.seq_len = seq_len

    def __getitem__(self, index):

        full_seq = torch.Tensor(self.data[index][:self.seq_len+1]).long()

        return full_seq.cuda()

    def __len__(self):
        return (len(self.data) // BATCH_SIZE) * BATCH_SIZE

# precision/optimizer/scaler

dtype = torch.float16

ctx = torch.amp.autocast(device_type='cuda', dtype=dtype, enabled=False)

optim = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)

scaler = torch.cuda.amp.GradScaler(enabled=False)

"""# (TRAIN MODEL)"""

# @title Train the model

train_losses = []
val_losses = []

train_accs = []
val_accs = []

nsteps = 0

for ep in range(NUM_EPOCHS):

  print('=' * 70)
  print('Epoch #', ep)
  print('=' * 70)

  random.shuffle(train_data)

  train_dataset = MusicDataset(train_data, SEQ_LEN)
  val_dataset   = MusicDataset(train_data, SEQ_LEN)
  train_loader  = cycle(DataLoader(train_dataset, batch_size = BATCH_SIZE))
  val_loader    = cycle(DataLoader(val_dataset, batch_size = BATCH_SIZE))

  NUM_BATCHES = len(train_data) // BATCH_SIZE // GRADIENT_ACCUMULATE_EVERY

  for i in tqdm.tqdm(range(NUM_BATCHES), mininterval=10., desc='Training'):
      model.train()

      for __ in range(GRADIENT_ACCUMULATE_EVERY):
          with ctx:
              loss, acc = model(next(train_loader))
          # loss = loss / GRADIENT_ACCUMULATE_EVERY
          scaler.scale(loss).backward(torch.ones(loss.shape).cuda())

      if i % PRINT_STATS_EVERY == 0:
          print(f'Training loss: {loss.mean().item() * GRADIENT_ACCUMULATE_EVERY}')
          print(f'Training acc: {acc.mean().item()}')

      train_losses.append(loss.mean().item() * GRADIENT_ACCUMULATE_EVERY)
      train_accs.append(acc.mean().item())

      scaler.unscale_(optim)
      torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
      scaler.step(optim)
      scaler.update()
      optim.zero_grad(set_to_none=True)

      nsteps += 1

      if i % VALIDATE_EVERY == 0:
        model.eval()
        with torch.no_grad():
          with ctx:
            val_loss, val_acc = model(next(val_loader))

            print(f'Validation loss: {val_loss.mean().item()}')
            print(f'Validation acc: {val_acc.mean().item()}')

            val_losses.append(val_loss.mean().item())
            val_accs.append(val_acc.mean().item())

            print('Plotting training loss graph...')

            tr_loss_list = train_losses
            plt.plot([i for i in range(len(tr_loss_list))] ,tr_loss_list, 'b')
            plt.show()
            plt.close()
            print('Done!')

            print('Plotting training acc graph...')

            tr_loss_list = train_accs
            plt.plot([i for i in range(len(tr_loss_list))] ,tr_loss_list, 'b')
            plt.show()
            plt.close()
            print('Done!')

            print('Plotting validation loss graph...')
            tr_loss_list = val_losses
            plt.plot([i for i in range(len(tr_loss_list))] ,tr_loss_list, 'b')
            plt.show()
            plt.close()
            print('Done!')

            print('Plotting validation acc graph...')
            tr_loss_list = val_accs
            plt.plot([i for i in range(len(tr_loss_list))] ,tr_loss_list, 'b')
            plt.show()
            plt.close()
            print('Done!')

      if i % GENERATE_EVERY == 0:
        model.eval()

        inp = random.choice(val_dataset)[:512]

        print(inp)

        with ctx:

            sample = model.generate(inp[None, ...], GENERATE_LENGTH)

        print(sample)

      if i % SAVE_EVERY == 0:

          print('Saving model progress. Please wait...')
          print('model_checkpoint_' + str(nsteps) + '_steps_' + str(round(float(train_losses[-1]), 4)) + '_loss_' + str(round(float(train_accs[-1]), 4)) + '_acc.pth')

          fname = '/content/model_checkpoint_' + str(nsteps) + '_steps_' + str(round(float(train_losses[-1]), 4)) + '_loss_' + str(round(float(train_accs[-1]), 4)) + '_acc.pth'

          torch.save(model.state_dict(), fname)

          data = [train_losses, train_accs, val_losses, val_accs]

          TMIDIX.Tegridy_Any_Pickle_File_Writer(data, '/content/losses_accs')

          print('Done!')

#======================================================================================================

print('Saving model progress. Please wait...')
print('model_checkpoint_' + str(nsteps) + '_steps_' + str(round(float(train_losses[-1]), 4)) + '_loss_' + str(round(float(train_accs[-1]), 4)) + '_acc.pth')

fname = '/content/model_checkpoint_' + str(nsteps) + '_steps_' + str(round(float(train_losses[-1]), 4)) + '_loss_' + str(round(float(train_accs[-1]), 4)) + '_acc.pth'

torch.save(model.state_dict(), fname)

print('Done!')

data = [train_losses, train_accs, val_losses, val_accs]

TMIDIX.Tegridy_Any_Pickle_File_Writer(data, '/content/losses_accuracies')

# Save training loss graph

plt.plot([i for i in range(len(train_losses))] ,train_losses, 'b')
plt.savefig('/content/training_loss_graph.png')
plt.close()
print('Done!')

# Save training acc graph

plt.plot([i for i in range(len(train_accs))] ,train_accs, 'b')
plt.savefig('/content/training_acc_graph.png')
plt.close()
print('Done!')

# Save validation loss graph

plt.plot([i for i in range(len(val_losses))] ,val_losses, 'b')
plt.savefig('/content/validation_loss_graph.png')
plt.close()
print('Done!')

# Save validation acc graph

plt.plot([i for i in range(len(val_accs))] ,val_accs, 'b')
plt.savefig('/content/validation_acc_graph.png')
plt.close()
print('Done!')

"""# (SAVE MODEL)"""

# @title Manual save
print('Saving model progress. Please wait...')
print('model_checkpoint_' + str(nsteps) + '_steps_' + str(round(float(train_losses[-1]), 4)) + '_loss_' + str(round(float(train_accs[-1]), 4)) + '_acc.pth')

fname = '/content/model_checkpoint_' + str(nsteps) + '_steps_' + str(round(float(train_losses[-1]), 4)) + '_loss_' + str(round(float(train_accs[-1]), 4)) + '_acc.pth'

torch.save(model.state_dict(), fname)

print('Done!')

data = [train_losses, train_accs, val_losses, val_accs]

TMIDIX.Tegridy_Any_Pickle_File_Writer(data, '/content/losses_accuracies')

# Save training loss graph

plt.plot([i for i in range(len(train_losses))] ,train_losses, 'b')
plt.savefig('/content/training_loss_graph.png')
plt.close()
print('Done!')

# Save training acc graph

plt.plot([i for i in range(len(train_accs))] ,train_accs, 'b')
plt.savefig('/content/training_acc_graph.png')
plt.close()
print('Done!')

# Save validation loss graph

plt.plot([i for i in range(len(val_losses))] ,val_losses, 'b')
plt.savefig('/content/validation_loss_graph.png')
plt.close()
print('Done!')

# Save validation acc graph

plt.plot([i for i in range(len(val_accs))] ,val_accs, 'b')
plt.savefig('/content/validation_acc_graph.png')
plt.close()
print('Done!')

"""# (EVAL MODEL)"""

# @title Eval model
dtype = 'float16'
device_type = 'cuda'
ptdtype = {'float32': torch.float32, 'bfloat16': torch.bfloat16, 'float16': torch.float16}[dtype]
ctx = torch.amp.autocast(device_type=device_type, dtype=ptdtype)

model.eval()

x = torch.tensor(random.choice(train_data)[:128], dtype=torch.long, device='cuda')[None, ...]
x = torch.tensor([[321]] * 1, dtype=torch.long, device='cuda')


# run generation

#with ctx:
out = model.generate(x,
                    128,
                    temperature=0.9,
                    return_prime=False,
                    verbose=True)

y = out.tolist()

print('---------------')
print(y[0])

#@title Convert output INTs to MIDI

train_data1 = y[0] # batch number goes here

print('Sample INTs', train_data1[:15])

out = train_data1

patches = [0] * 16
patches[3] = 40

if len(out) != 0:

    song = out
    song_f = []

    time = 0
    dur = 0
    vel = 90
    pitch = 0
    channel = 0

    for ss in song:

        chord = TMIDIX.ALL_CHORDS_SORTED[ss]

        time += 200
        dur = 200

        for c in chord:

          ptc1 = 48+c
          ptc2 = 60+c

          song_f.append(['note', time, dur, channel, ptc1, vel ])
          song_f.append(['note', time, dur, channel, ptc2, vel ])

detailed_stats = TMIDIX.Tegridy_ms_SONG_to_MIDI_Converter(song_f,
                                                          output_signature = 'Chords Progressions Transformer',
                                                          output_file_name = '/content/Chords-Progressions-Transformer-Composition',
                                                          track_name='Project Los Angeles',
                                                          )

print('Done!')

"""# (PLOT TOKENS EMBEDDINGS)"""

# @title Plot model tokens embeddings
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

"""# Congrats! You did it! :)"""