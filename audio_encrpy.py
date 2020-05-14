import os
import wave

class Steganography:
    def lsb(self,input_song,msg):        
        song = wave.open(input_song, mode='rb')
        frame_bytes = bytearray(list(song.readframes(song.getnframes())))
        string=msg
        string = string + int((len(frame_bytes)-(len(string)*8*8))/8) *'#'
        bits = list(map(int, ''.join([bin(ord(i)).lstrip('0b').rjust(8,'0') for i in string])))
        for i, bit in enumerate(bits):
            frame_bytes[i] = (frame_bytes[i] & 254) | bit
        frame_modified = bytes(frame_bytes)
        if not os.path.exists('outputs'):
            os.mkdir('outputs')
        filepath = os.path.join('outputs','song_emb.wav')
        with wave.open(filepath,'wb') as fdd:
            fdd.setparams(song.getparams())
            fdd.writeframes(frame_modified)
        song.close()
        # delete uploaded file
        
        return fdd


