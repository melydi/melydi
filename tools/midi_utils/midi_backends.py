import mido

possible_backends = ['mido.backends.pygame', 'mido.backends.rtmidi', 'mido.backends.portmidi', 'mido.backends.rtmidi_python', 'mido.backends.amidi']
found_backend = False
for backend in possible_backends:
    try:
        mido.set_backend(backend)
        mido.get_input_names()
        found_backend = True
        break
    except:
        pass
if not found_backend:
    raise Excetion("Error: could not find valid backend for mido.")

if __name__=='__main__':
    print (mido.get_input_names())
    import IPython as ipy
    ipy.embed() 
