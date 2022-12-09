#!/usr/bin/env bash
## CONFIG LIST
## groovae_4bar : GrooVAE + GrooveConverter
## musicvae_4bar_paper_org : MusicVAE + GrooveConverter
## musicvae_4bar_paper_reduceunit : MusicVAE(Reduce Unit) + GrooveConverter
## musicvae_4bar_paper_drumconv : MusicVAE(Reduce Unit) + DrumsConverter (BEST WAY)

CONFIG=musicvae_4bar_paper_drumconv
MIDIDATA_PATH=./data/midi/groove-v1.0.0-midionly
FEATURE_PATH=./data/preprocess/groove_midi_features.tfrecord
MIDIOUT_PATH=./result_generate/$CONFIG

### 데이터 전처리 ###
python3 ./preprocess_code/convert_dir_to_note_sequences.py \
  --input_dir=$MIDIDATA_PATH \
  --output_file=$FEATURE_PATH \
  --recursive

## 데이터 학습 ###
python3 music_vae_train.py \
--config=$CONFIG \
--run_dir=./model_checkpoint/$CONFIG/ \
--mode=train \
--examples_path=$FEATURE_PATH  \

### 모델 활용 MIDI 생성기 ###
#python3 music_vae_generate.py \
#--config=$CONFIG \
#--checkpoint_file=./model_checkpoint/musicvae_4bar_paper_drumconv/train/model.ckpt-4532 \
#--mode=sample \
#--num_outputs=5 \
#--output_dir=$MIDIOUT_PATH

