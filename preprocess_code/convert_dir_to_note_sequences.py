# Copyright 2022 The Magenta Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

r""""Converts music files to NoteSequence protos and writes TFRecord file.

Currently supports MIDI (.mid, .midi) and MusicXML (.xml, .mxl) files.

Example usage:
  $ python magenta/scripts/convert_dir_to_note_sequences.py \
    --input_dir=/path/to/input/dir \
    --output_file=/path/to/tfrecord/file \
    --log=INFO
"""




'''
import tensorflow.compat.v1 as tf
import collections
import io
import sys

from note_seq import constants
from note_seq.protobuf import music_pb2
import pretty_midi


def midi_to_note_sequence(midi_data):
  """Convert MIDI file contents to a NoteSequence.
  Converts a MIDI file encoded as a string into a NoteSequence. Decoding errors
  are very common when working with large sets of MIDI files, so be sure to
  handle MIDIConversionError exceptions.
  Args:
    midi_data: A string containing the contents of a MIDI file or populated
        pretty_midi.PrettyMIDI object.
  Returns:
    A NoteSequence.
  Raises:
    MIDIConversionError: An improper MIDI mode was supplied.
  """
  # In practice many MIDI files cannot be decoded with pretty_midi. Catch all
  # errors here and try to log a meaningful message. So many different
  # exceptions are raised in pretty_midi.PrettyMidi that it is cumbersome to
  # catch them all only for the purpose of error logging.
  # pylint: disable=bare-except
  if isinstance(midi_data, pretty_midi.PrettyMIDI):
    midi = midi_data
  else:
    try:
      midi = pretty_midi.PrettyMIDI(io.BytesIO(midi_data))  #### PrettyMIDI를 통한 midi 객체 생성
    except:
      raise MIDIConversionError('Midi decoding error %s: %s' %
                                (sys.exc_info()[0], sys.exc_info()[1]))
  # pylint: enable=bare-except


  sequence = music_pb2.NoteSequence() ### 빈 시퀀스 생성
  #print(sequence)

  # Populate header.
  sequence.ticks_per_quarter = midi.resolution
  sequence.source_info.parser = music_pb2.NoteSequence.SourceInfo.PRETTY_MIDI
  sequence.source_info.encoding_type = (
      music_pb2.NoteSequence.SourceInfo.MIDI)

  # Populate time signatures.
  for midi_time in midi.time_signature_changes:
    time_signature = sequence.time_signatures.add()
    time_signature.time = midi_time.time
    time_signature.numerator = midi_time.numerator
    try:
      # Denominator can be too large for int32.
      time_signature.denominator = midi_time.denominator
    except ValueError:
      raise MIDIConversionError('Invalid time signature denominator %d' %
                                midi_time.denominator)


  # Populate key signatures.
  for midi_key in midi.key_signature_changes:
    key_signature = sequence.key_signatures.add()
    key_signature.time = midi_key.time
    key_signature.key = midi_key.key_number % 12
    midi_mode = midi_key.key_number // 12
    if midi_mode == 0:
      key_signature.mode = key_signature.MAJOR
    elif midi_mode == 1:
      key_signature.mode = key_signature.MINOR
    else:
      raise MIDIConversionError('Invalid midi_mode %i' % midi_mode)

  # Populate tempo changes.
  tempo_times, tempo_qpms = midi.get_tempo_changes()
  for time_in_seconds, tempo_in_qpm in zip(tempo_times, tempo_qpms):
    tempo = sequence.tempos.add()
    tempo.time = time_in_seconds
    tempo.qpm = tempo_in_qpm

  # Populate notes by gathering them all from the midi's instruments.
  # Also set the sequence.total_time as the max end time in the notes.
  midi_notes = []
  midi_pitch_bends = []
  midi_control_changes = []
  for num_instrument, midi_instrument in enumerate(midi.instruments):
    # Populate instrument name from the midi's instruments
    if midi_instrument.name:
      instrument_info = sequence.instrument_infos.add()
      instrument_info.name = midi_instrument.name
      instrument_info.instrument = num_instrument
    for midi_note in midi_instrument.notes:
      if not sequence.total_time or midi_note.end > sequence.total_time:
        sequence.total_time = midi_note.end
      midi_notes.append((midi_instrument.program, num_instrument,
                         midi_instrument.is_drum, midi_note))
    for midi_pitch_bend in midi_instrument.pitch_bends:
      midi_pitch_bends.append(
          (midi_instrument.program, num_instrument,
           midi_instrument.is_drum, midi_pitch_bend))
    for midi_control_change in midi_instrument.control_changes:
      midi_control_changes.append(
          (midi_instrument.program, num_instrument,
           midi_instrument.is_drum, midi_control_change))

  for program, instrument, is_drum, midi_note in midi_notes:
    note = sequence.notes.add()
    note.instrument = instrument
    note.program = program
    note.start_time = midi_note.start
    note.end_time = midi_note.end
    note.pitch = midi_note.pitch
    note.velocity = midi_note.velocity
    note.is_drum = is_drum

  for program, instrument, is_drum, midi_pitch_bend in midi_pitch_bends:
    pitch_bend = sequence.pitch_bends.add()
    pitch_bend.instrument = instrument
    pitch_bend.program = program
    pitch_bend.time = midi_pitch_bend.time
    pitch_bend.bend = midi_pitch_bend.pitch
    pitch_bend.is_drum = is_drum

  for program, instrument, is_drum, midi_control_change in midi_control_changes:
    control_change = sequence.control_changes.add()
    control_change.instrument = instrument
    control_change.program = program
    control_change.time = midi_control_change.time
    control_change.control_number = midi_control_change.number
    control_change.control_value = midi_control_change.value
    control_change.is_drum = is_drum

  # TODO(douglaseck): Estimate note type (e.g. quarter note) and populate
  # note.numerator and note.denominator.
  print(sequence)
  return sequence


def midi_to_sequence_proto(midi_data):
  """Renamed to midi_to_note_sequence."""
  return midi_to_note_sequence(midi_data)

sequence = midi_to_sequence_proto(tf.gfile.GFile('/media/server/EXSSD/MIDI/magenta-main/magenta/models/music_vae/groove-v1.0.0-midionly/groove/drummer1/session1/6_jazz-funk_116_fill_4-4.mid', 'rb').read())
#print(sequence)
exit()
'''


import hashlib
import os

from note_seq import abc_parser
from note_seq import midi_io
from note_seq import musicxml_reader
import tensorflow.compat.v1 as tf

FLAGS = tf.app.flags.FLAGS

tf.app.flags.DEFINE_string('input_dir', None,
                           'Directory containing files to convert.')
tf.app.flags.DEFINE_string('output_file', None,
                           'Path to output TFRecord file. Will be overwritten '
                           'if it already exists.')
tf.app.flags.DEFINE_bool('recursive', False,
                         'Whether or not to recurse into subdirectories.')
tf.app.flags.DEFINE_string('log', 'INFO',
                           'The threshold for what messages will be logged '
                           'DEBUG, INFO, WARN, ERROR, or FATAL.')


def generate_note_sequence_id(filename, collection_name, source_type):
  """Generates a unique ID for a sequence.

  The format is:'/id/<type>/<collection name>/<hash>'.

  Args:
    filename: The string path to the source file relative to the root of the
        collection.
    collection_name: The collection from which the file comes.
    source_type: The source type as a string (e.g. "midi" or "abc").

  Returns:
    The generated sequence ID as a string.
  """
  filename_fingerprint = hashlib.sha1(filename.encode('utf-8'))
  return '/id/%s/%s/%s' % (
      source_type.lower(), collection_name, filename_fingerprint.hexdigest())


def convert_files(root_dir, sub_dir, writer, recursive=False):
  """Converts files.

  Args:
    root_dir: A string specifying a root directory.
    sub_dir: A string specifying a path to a directory under `root_dir` in which
        to convert contents.
    writer: A TFRecord writer
    recursive: A boolean specifying whether or not recursively convert files
        contained in subdirectories of the specified directory.

  Returns:
    A map from the resulting Futures to the file paths being converted.
  """
  dir_to_convert = os.path.join(root_dir, sub_dir)
  tf.logging.info("Converting files in '%s'.", dir_to_convert)
  files_in_dir = tf.gfile.ListDirectory(os.path.join(dir_to_convert))
  recurse_sub_dirs = []
  written_count = 0
  for file_in_dir in files_in_dir:
    tf.logging.log_every_n(tf.logging.INFO, '%d files converted.',
                           1000, written_count)
    full_file_path = os.path.join(dir_to_convert, file_in_dir)

    ##### MIDI CONVERT PROCESS #####
    if (full_file_path.lower().endswith('.mid') or
        full_file_path.lower().endswith('.midi')):
      try:
        sequence = convert_midi(root_dir, sub_dir, full_file_path)
      except Exception as exc:  # pylint: disable=broad-except
        tf.logging.fatal('%r generated an exception: %s', full_file_path, exc)
        continue
      if sequence:
        #print(sequence.SerializeToString())
        #print(sequence)
        writer.write(sequence.SerializeToString())


    elif (full_file_path.lower().endswith('.xml') or
          full_file_path.lower().endswith('.mxl')):
      try:
        sequence = convert_musicxml(root_dir, sub_dir, full_file_path)
      except Exception as exc:  # pylint: disable=broad-except
        tf.logging.fatal('%r generated an exception: %s', full_file_path, exc)
        continue
      if sequence:
        writer.write(sequence.SerializeToString())


    elif full_file_path.lower().endswith('.abc'):
      try:
        sequences = convert_abc(root_dir, sub_dir, full_file_path)
      except Exception as exc:  # pylint: disable=broad-except
        tf.logging.fatal('%r generated an exception: %s', full_file_path, exc)
        continue
      if sequences:
        for sequence in sequences:
          writer.write(sequence.SerializeToString())

    else:
      if recursive and tf.gfile.IsDirectory(full_file_path):
        recurse_sub_dirs.append(os.path.join(sub_dir, file_in_dir))
      else:
        tf.logging.warning(
            'Unable to find a converter for file %s', full_file_path)

  for recurse_sub_dir in recurse_sub_dirs:
    convert_files(root_dir, recurse_sub_dir, writer, recursive)


def convert_midi(root_dir, sub_dir, full_file_path):
  """Converts a midi file to a sequence proto.

  Args:
    root_dir: A string specifying the root directory for the files being
        converted.
    sub_dir: The directory being converted currently.
    full_file_path: the full path to the file to convert.

  Returns:
    Either a NoteSequence proto or None if the file could not be converted.
  """
  try:
    sequence = midi_io.midi_to_sequence_proto(tf.gfile.GFile(full_file_path, 'rb').read())

  except midi_io.MIDIConversionError as e:
    tf.logging.warning(
        'Could not parse MIDI file %s. It will be skipped. Error was: %s',
        full_file_path, e)
    return None

  sequence.collection_name = os.path.basename(root_dir)
  sequence.filename = os.path.join(sub_dir, os.path.basename(full_file_path))

  sequence.id = generate_note_sequence_id(
      sequence.filename, sequence.collection_name, 'midi')

  tf.logging.info('Converted MIDI file %s.', full_file_path)

  return sequence


def convert_musicxml(root_dir, sub_dir, full_file_path):
  """Converts a musicxml file to a sequence proto.

  Args:
    root_dir: A string specifying the root directory for the files being
        converted.
    sub_dir: The directory being converted currently.
    full_file_path: the full path to the file to convert.

  Returns:
    Either a NoteSequence proto or None if the file could not be converted.
  """
  try:
    sequence = musicxml_reader.musicxml_file_to_sequence_proto(full_file_path)
  except musicxml_reader.MusicXMLConversionError as e:
    tf.logging.warning(
        'Could not parse MusicXML file %s. It will be skipped. Error was: %s',
        full_file_path, e)
    return None
  sequence.collection_name = os.path.basename(root_dir)
  sequence.filename = os.path.join(sub_dir, os.path.basename(full_file_path))
  sequence.id = generate_note_sequence_id(
      sequence.filename, sequence.collection_name, 'musicxml')
  tf.logging.info('Converted MusicXML file %s.', full_file_path)
  return sequence


def convert_abc(root_dir, sub_dir, full_file_path):
  """Converts an abc file to a sequence proto.

  Args:
    root_dir: A string specifying the root directory for the files being
        converted.
    sub_dir: The directory being converted currently.
    full_file_path: the full path to the file to convert.

  Returns:
    Either a NoteSequence proto or None if the file could not be converted.
  """
  try:
    tunes, exceptions = abc_parser.parse_abc_tunebook(
        tf.gfile.GFile(full_file_path, 'rb').read())
  except abc_parser.ABCParseError as e:
    tf.logging.warning(
        'Could not parse ABC file %s. It will be skipped. Error was: %s',
        full_file_path, e)
    return None

  for exception in exceptions:
    tf.logging.warning(
        'Could not parse tune in ABC file %s. It will be skipped. Error was: '
        '%s', full_file_path, exception)

  sequences = []
  for idx, tune in tunes.items():
    tune.collection_name = os.path.basename(root_dir)
    tune.filename = os.path.join(sub_dir, os.path.basename(full_file_path))
    tune.id = generate_note_sequence_id(
        '{}_{}'.format(tune.filename, idx), tune.collection_name, 'abc')
    sequences.append(tune)
    tf.logging.info('Converted ABC file %s.', full_file_path)
  return sequences


def convert_directory(root_dir, output_file, recursive=False):
  """Converts files to NoteSequences and writes to `output_file`.

  Input files found in `root_dir` are converted to NoteSequence protos with the
  basename of `root_dir` as the collection_name, and the relative path to the
  file from `root_dir` as the filename. If `recursive` is true, recursively
  converts any subdirectories of the specified directory.

  Args:
    root_dir: A string specifying a root directory.
    output_file: Path to TFRecord file to write results to.
    recursive: A boolean specifying whether or not recursively convert files
        contained in subdirectories of the specified directory.
  """
  with tf.io.TFRecordWriter(output_file) as writer:
    convert_files(root_dir, '', writer, recursive)


def main(unused_argv):
  tf.logging.set_verbosity(FLAGS.log)

  if not FLAGS.input_dir:
    tf.logging.fatal('--input_dir required')
    return
  if not FLAGS.output_file:
    tf.logging.fatal('--output_file required')
    return

  input_dir = os.path.expanduser(FLAGS.input_dir)
  output_file = os.path.expanduser(FLAGS.output_file)
  output_dir = os.path.dirname(output_file)

  if output_dir:
    tf.gfile.MakeDirs(output_dir)

  convert_directory(input_dir, output_file, FLAGS.recursive)


def console_entry_point():
  tf.disable_v2_behavior()
  tf.app.run(main)


if __name__ == '__main__':
  console_entry_point()
