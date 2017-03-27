# autoscribe
Pitch Detection for Polyphonic Piano Music

See https://aiqiliu.github.io/polyscribe/ for more details on the method and results.


# usage
Run the maps_polyphonic_general.ipynb jupyter notebook with Python 3. Change the specified file names to correctly identify relative paths to the training set, the polyphonic piece to approximate, and the ground-truth of the piece (to calculate performance). The rest of the notebook can be run on the polyphonic music to generate an approximate transcription. Due to high memory requirements, it is recommended that the song be less than 30 seconds in length, sampled at 11.025kHz
