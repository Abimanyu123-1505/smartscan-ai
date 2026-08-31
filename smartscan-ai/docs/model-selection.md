# Model Selection

We evaluate several model architectures:
1. **ResNet-1D**: Good baseline for time-series I/Q data.
2. **Spectrogram-CNNs**: Effective for localized interference detection.
3. **Temporal Convolutional Networks (TCNs)**: Best suited for capturing long-term dependencies in the spectrum allocation over time.

Model selection is strictly based on the F1-score and inference latency constraints established in the performance benchmarks.
