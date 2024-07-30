import wave
import speech_recognition as sr
import argparse
import os
import re

def get_parser():
    """
    Generate a parameters parser.
    """
    # parse parameters
    parser = argparse.ArgumentParser(description="ASR")

    # model / output paths
    parser.add_argument("--audio", type=str, default="", help="audio path")
    parser.add_argument("--text", type=str, default="", help="text path")
    parser.add_argument("--output_path", type=str, default="", help="output path")
    
    return parser

def create_directory_if_not_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def write_sentence_to_file(words, filename):
    sentence = " ".join(words)

    with open(filename, 'w') as file:
        file.write(sentence)

def remove_punctuation(text):
    punctuation_pattern = r'^[\'\",.?!]+|[\'\",.?!]+$'
    cleaned_text = re.sub(punctuation_pattern, '', text)
    return cleaned_text

def split_audio(audio_file, output_path):
    
    wave_file = wave.open(audio_file, "r")
    
    sample_width = wave_file.getsampwidth() 
    frame_rate = wave_file.getframerate()   
    num_channels = wave_file.getnchannels() 
    num_frames = wave_file.getnframes()   
    
    interval = 2 
    interval_frames = int(interval * frame_rate)
    
    create_directory_if_not_exists(output_path)
    
    # 分割音频数据并保存为多个小文件
    last_start_frame = 0
    start_frame = 0
    file_count = 0

    while start_frame < num_frames:
        
        end_frame = min(start_frame + interval_frames, num_frames)
        
        wave_file.setpos(start_frame)
        audio_data = wave_file.readframes(end_frame - start_frame)
    
        new_wave_file = wave.open(os.path.join(output_path, f"audio_{file_count}.wav"), "w")
        new_wave_file.setparams((num_channels, sample_width, frame_rate, end_frame - start_frame, "NONE", "not compressed"))
        if last_start_frame != 0:
            new_wave_file.setparams((num_channels, sample_width, frame_rate, end_frame - last_start_frame, "NONE", "not compressed"))
            new_wave_file.writeframes(last_audio_data)
        new_wave_file.writeframes(audio_data)
        new_wave_file.close()
        
        last_audio_data = audio_data
        last_start_frame = start_frame
        start_frame += interval_frames
        file_count += 1
    
    wave_file.close()

    return file_count

def find_best_position(_long_words, short_words):
    max_word_count = 0
    best_position = 0

    long_words = [''] * (len(short_words) - 1) + _long_words

    token_list = ['(break)', '(laugh)', '(lip-smack)', '(clap)', '(slience)']
    pos = []
    for i in range(len(long_words)):
        if remove_punctuation(long_words[i]) not in token_list:
            pos.append(i)
    long_words = [word for word in long_words if remove_punctuation(word) not in token_list]

    for i in range(len(long_words) - len(short_words) + 1):
        word_count = 0
        for j in range(len(short_words)):
            a = remove_punctuation(long_words[i + j].lower())
            b = remove_punctuation(short_words[j].lower())
            if a == b:
                word_count += 1
        if word_count > max_word_count:
            max_word_count = word_count
            best_position = i + len(short_words) - 1
  
    return max(pos[best_position] - (len(short_words) - 1), 0)

def get_audio_length_wave(filename):
    with wave.open(filename, 'rb') as audio_file:
        frames = audio_file.getnframes()
        framerate = audio_file.getframerate()
        duration = frames / float(framerate)
        return duration

def main(params):

    recognizer = sr.Recognizer()

    savedir = os.path.abspath(params.output_path)
    savedir_audio = os.path.join(savedir, 'audio')
    create_directory_if_not_exists(savedir)
    create_directory_if_not_exists(savedir_audio)

    text_file = params.text
    f = open(text_file, 'r')
    ref = f.read()
    ref = ref.replace('\n', '')
    ref = ref.replace('{BR}', '<break>')
    ref = ref.replace('{LG}', '(laugh)')
    ref = ref.replace('{LS}', '(lip-smack)')
    ref = ref.replace('{NS}', '(clap)')
    ref = ref.replace('{SL}', '(slience)')
    ref = ref.replace('{CG}', '(cough)')
    ref = ref.split()

    # 加载音频文件
    audio_file = params.audio 
    length = get_audio_length_wave(audio_file)

    file_count = split_audio(audio_file, savedir_audio)
    print("Split audio file into {} pieces.".format(file_count))

    cnt = 0
    last_last_position = 0
    last_position = 0
    for i in range(file_count):
        with sr.AudioFile(os.path.join(savedir_audio, f"audio_{i}.wav")) as source:
            cnt += 2
            audio = recognizer.record(source)
            try:
                text = recognizer.recognize_google(audio)
                print(text)
                best_position = find_best_position(ref[last_last_position:last_position + 2*16], text.split())
                next_position = max(last_last_position + best_position + 1, last_position + 1)
                print(ref[last_last_position: next_position])
                print(ref[last_position: next_position])
                write_sentence_to_file(ref[last_position:next_position], os.path.join(savedir, '{}.txt'.format(int(cnt/2))))
                last_last_position = last_position
                last_position = next_position
            except sr.UnknownValueError:
                next_position = last_position
                write_sentence_to_file(ref[last_position:next_position], os.path.join(savedir, '{}.txt'.format(int(cnt/2))))
                last_last_position = last_position
                last_position = next_position
                print("UnknownValueError")
            except sr.RequestError as e:
                print("RequestError: ", str(e))
            print("Progress: {}/{}, Time: {}/{}\n".format(last_position, len(ref), cnt, length))


if __name__ == '__main__':

    # generate parser / parse parameters
    parser = get_parser()
    params = parser.parse_args()

    main(params)