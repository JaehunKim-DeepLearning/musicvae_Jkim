#!/usr/bin/env bash
## CONFIG LIST 
## hierdec-mel_4bar : MusicVAE(Reduce Unit) + OneHotMelodyConverter

CONFIG=hierdec-mel_4bar
MIDIDATA_PATH=./data/midi/maestro-v3.0.0/2015
FEATURE_PATH=./data/preprocess/maestro-v3.0.0.tfrecord
MIDIOUT_PATH=./result_generate/$CONFIG

### 데이터 전처리 ###d
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

## 모델 활용 MIDI 생성기 ###
#python3 music_vae_generate.py \
#--config=$CONFIG \
#--checkpoint_file=./model_checkpoint/hierdec-mel_4bar/train/model.ckpt-1945 \
#--mode=sample \
#--num_outputs=5 \
#--output_dir=$MIDIOUT_PATH