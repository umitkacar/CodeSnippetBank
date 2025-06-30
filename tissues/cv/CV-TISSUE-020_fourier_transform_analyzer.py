"""
CV-TISSUE-020: Fourier Transform Analyzer
Advanced frequency domain analysis optimized for edge devices
"""

import numpy as np
from typing import Tuple, List, Optional, Dict, Any, Union

class FourierTransformAnalyzer:
    def __init__(self,
                 use_fft: bool = True,
                 window_function: str = 'hann',
                 pad_mode: str = 'constant'):
        """
        Initialize Fourier Transform Analyzer
        
        Args:
            use_fft: Use FFT (True) or DFT (False)
            window_function: Window function ('none', 'hann', 'hamming', 'blackman')
            pad_mode: Padding mode for FFT optimization
        """
        self.use_fft = use_fft
        self.window_function = window_function
        self.pad_mode = pad_mode
        
        # Cache for window functions
        self._window_cache = {}
        
    def compute_fourier_transform(self,
                                 image: np.ndarray,
                                 shift: bool = True) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute 2D Fourier Transform
        
        Args:
            image: Input image
            shift: Shift zero frequency to center
            
        Returns:
            Magnitude and phase arrays
        """
        # Apply window function
        windowed = self._apply_window(image)
        
        # Pad to optimal FFT size
        if self.use_fft:
            padded = self._pad_for_fft(windowed)
        else:
            padded = windowed
            
        # Compute transform
        if self.use_fft:
            fft_result = np.fft.fft2(padded)
        else:
            fft_result = self._compute_dft_2d(padded)
            
        # Shift if requested
        if shift:
            fft_result = np.fft.fftshift(fft_result)
            
        # Compute magnitude and phase
        magnitude = np.abs(fft_result)
        phase = np.angle(fft_result)
        
        return magnitude, phase
    
    def inverse_fourier_transform(self,
                                 magnitude: np.ndarray,
                                 phase: np.ndarray,
                                 shifted: bool = True) -> np.ndarray:
        """
        Compute inverse Fourier Transform
        
        Args:
            magnitude: Magnitude spectrum
            phase: Phase spectrum
            shifted: Whether spectrum is shifted
            
        Returns:
            Reconstructed image
        """
        # Reconstruct complex array
        fft_result = magnitude * np.exp(1j * phase)
        
        # Unshift if needed
        if shifted:
            fft_result = np.fft.ifftshift(fft_result)
            
        # Inverse transform
        if self.use_fft:
            result = np.fft.ifft2(fft_result)
        else:
            result = self._compute_idft_2d(fft_result)
            
        # Take real part and normalize
        result = np.real(result)
        
        # Remove padding if applied
        if hasattr(self, '_original_shape'):
            h, w = self._original_shape
            result = result[:h, :w]
            
        return result.astype(np.uint8)
    
    def apply_frequency_filter(self,
                              image: np.ndarray,
                              filter_type: str,
                              cutoff: float,
                              order: int = 2) -> np.ndarray:
        """
        Apply frequency domain filter
        
        Args:
            image: Input image
            filter_type: Filter type ('lowpass', 'highpass', 'bandpass', 'bandstop')
            cutoff: Cutoff frequency (0-1, normalized)
            order: Filter order (butterworth)
            
        Returns:
            Filtered image
        """
        # Compute FFT
        magnitude, phase = self.compute_fourier_transform(image)
        
        # Create filter
        h, w = magnitude.shape
        filter_mask = self._create_frequency_filter(h, w, filter_type, cutoff, order)
        
        # Apply filter
        filtered_magnitude = magnitude * filter_mask
        
        # Inverse transform
        return self.inverse_fourier_transform(filtered_magnitude, phase)
    
    def analyze_spectrum(self,
                        image: np.ndarray) -> Dict[str, Any]:
        """
        Analyze frequency spectrum
        
        Args:
            image: Input image
            
        Returns:
            Spectrum analysis results
        """
        magnitude, phase = self.compute_fourier_transform(image)
        
        # Log magnitude for better visualization
        log_magnitude = np.log1p(magnitude)
        
        # Find dominant frequencies
        center = np.array(magnitude.shape) // 2
        
        # Radial average
        radial_profile = self._compute_radial_average(magnitude, center)
        
        # Find peaks in radial profile
        peaks = self._find_spectrum_peaks(radial_profile)
        
        # Compute energy distribution
        total_energy = np.sum(magnitude ** 2)
        
        # Low frequency energy (center 10%)
        radius_low = int(0.1 * min(center))
        mask_low = self._create_circular_mask(magnitude.shape, center, radius_low)
        low_freq_energy = np.sum(magnitude[mask_low] ** 2) / total_energy
        
        # High frequency energy (outer 50%)
        radius_high = int(0.5 * min(center))
        mask_high = ~self._create_circular_mask(magnitude.shape, center, radius_high)
        high_freq_energy = np.sum(magnitude[mask_high] ** 2) / total_energy
        
        return {
            'magnitude': magnitude,
            'phase': phase,
            'log_magnitude': log_magnitude,
            'radial_profile': radial_profile,
            'dominant_frequencies': peaks,
            'low_freq_energy': low_freq_energy,
            'high_freq_energy': high_freq_energy,
            'total_energy': total_energy
        }
    
    def compute_phase_correlation(self,
                                 image1: np.ndarray,
                                 image2: np.ndarray) -> Tuple[float, float]:
        """
        Compute phase correlation for image registration
        
        Args:
            image1: First image
            image2: Second image
            
        Returns:
            Shift in x and y directions
        """
        # Compute FFTs
        fft1 = np.fft.fft2(image1)
        fft2 = np.fft.fft2(image2)
        
        # Compute cross-power spectrum
        cross_power = (fft1 * np.conj(fft2)) / (np.abs(fft1 * np.conj(fft2)) + 1e-6)
        
        # Inverse FFT
        correlation = np.fft.ifft2(cross_power)
        correlation = np.real(correlation)
        
        # Find peak
        peak_y, peak_x = np.unravel_index(np.argmax(correlation), correlation.shape)
        
        # Convert to shift
        h, w = image1.shape
        shift_x = peak_x if peak_x < w // 2 else peak_x - w
        shift_y = peak_y if peak_y < h // 2 else peak_y - h
        
        return shift_x, shift_y
    
    def _apply_window(self, image: np.ndarray) -> np.ndarray:
        """Apply window function to reduce edge artifacts"""
        if self.window_function == 'none':
            return image
            
        h, w = image.shape
        
        # Check cache
        cache_key = (self.window_function, h, w)
        if cache_key in self._window_cache:
            window = self._window_cache[cache_key]
        else:
            # Create 2D window
            if self.window_function == 'hann':
                window_1d_h = np.hanning(h)
                window_1d_w = np.hanning(w)
            elif self.window_function == 'hamming':
                window_1d_h = np.hamming(h)
                window_1d_w = np.hamming(w)
            elif self.window_function == 'blackman':
                window_1d_h = np.blackman(h)
                window_1d_w = np.blackman(w)
            else:
                raise ValueError(f"Unknown window function: {self.window_function}")
                
            window = np.outer(window_1d_h, window_1d_w)
            self._window_cache[cache_key] = window
            
        return image * window
    
    def _pad_for_fft(self, image: np.ndarray) -> np.ndarray:
        """Pad image to optimal FFT size"""
        h, w = image.shape
        self._original_shape = (h, w)
        
        # Find next power of 2
        next_h = 2 ** int(np.ceil(np.log2(h)))
        next_w = 2 ** int(np.ceil(np.log2(w)))
        
        # Pad if needed
        if next_h != h or next_w != w:
            pad_h = next_h - h
            pad_w = next_w - w
            
            if self.pad_mode == 'constant':
                padded = np.pad(image, ((0, pad_h), (0, pad_w)), mode='constant')
            elif self.pad_mode == 'edge':
                padded = np.pad(image, ((0, pad_h), (0, pad_w)), mode='edge')
            else:
                padded = np.pad(image, ((0, pad_h), (0, pad_w)), mode='reflect')
                
            return padded
        else:
            return image
    
    def _compute_dft_2d(self, image: np.ndarray) -> np.ndarray:
        """Compute 2D DFT (slow, for educational purposes)"""
        h, w = image.shape
        dft = np.zeros((h, w), dtype=complex)
        
        # Precompute exponentials
        exp_h = np.exp(-2j * np.pi * np.arange(h).reshape(-1, 1) @ np.arange(h).reshape(1, -1) / h)
        exp_w = np.exp(-2j * np.pi * np.arange(w).reshape(-1, 1) @ np.arange(w).reshape(1, -1) / w)
        
        # Compute DFT
        for u in range(h):
            for v in range(w):
                dft[u, v] = np.sum(image * exp_h[u, :].reshape(-1, 1) * exp_w[v, :])
                
        return dft
    
    def _compute_idft_2d(self, dft: np.ndarray) -> np.ndarray:
        """Compute 2D inverse DFT"""
        h, w = dft.shape
        image = np.zeros((h, w), dtype=complex)
        
        # Precompute exponentials
        exp_h = np.exp(2j * np.pi * np.arange(h).reshape(-1, 1) @ np.arange(h).reshape(1, -1) / h)
        exp_w = np.exp(2j * np.pi * np.arange(w).reshape(-1, 1) @ np.arange(w).reshape(1, -1) / w)
        
        # Compute IDFT
        for y in range(h):
            for x in range(w):
                image[y, x] = np.sum(dft * exp_h[y, :].reshape(-1, 1) * exp_w[x, :]) / (h * w)
                
        return image
    
    def _create_frequency_filter(self,
                                h: int, w: int,
                                filter_type: str,
                                cutoff: float,
                                order: int) -> np.ndarray:
        """Create frequency domain filter"""
        # Create coordinate grids
        u = np.arange(h) - h // 2
        v = np.arange(w) - w // 2
        u, v = np.meshgrid(u, v, indexing='ij')
        
        # Compute distance from center
        d = np.sqrt(u**2 + v**2)
        
        # Normalize cutoff
        d0 = cutoff * min(h, w) / 2
        
        # Create filter
        if filter_type == 'lowpass':
            # Butterworth lowpass
            filter_mask = 1 / (1 + (d / d0) ** (2 * order))
        elif filter_type == 'highpass':
            # Butterworth highpass
            filter_mask = 1 / (1 + (d0 / (d + 1e-6)) ** (2 * order))
        elif filter_type == 'bandpass':
            # Simple bandpass (needs two cutoffs in practice)
            d0_low = d0 * 0.5
            d0_high = d0 * 1.5
            mask_low = 1 / (1 + (d0_low / (d + 1e-6)) ** (2 * order))
            mask_high = 1 / (1 + (d / d0_high) ** (2 * order))
            filter_mask = mask_low * mask_high
        else:  # bandstop
            # Simple bandstop
            d0_low = d0 * 0.5
            d0_high = d0 * 1.5
            mask_low = 1 / (1 + (d / d0_low) ** (2 * order))
            mask_high = 1 / (1 + (d0_high / (d + 1e-6)) ** (2 * order))
            filter_mask = mask_low + mask_high
            filter_mask = np.clip(filter_mask, 0, 1)
            
        return filter_mask
    
    def _compute_radial_average(self,
                               spectrum: np.ndarray,
                               center: np.ndarray) -> np.ndarray:
        """Compute radial average of spectrum"""
        h, w = spectrum.shape
        y, x = np.ogrid[:h, :w]
        
        # Distance from center
        r = np.sqrt((x - center[1])**2 + (y - center[0])**2)
        r = r.astype(int)
        
        # Bin values
        max_radius = int(np.max(r))
        radial_profile = np.zeros(max_radius + 1)
        counts = np.zeros(max_radius + 1)
        
        for radius in range(max_radius + 1):
            mask = (r == radius)
            if np.any(mask):
                radial_profile[radius] = np.mean(spectrum[mask])
                counts[radius] = np.sum(mask)
                
        return radial_profile
    
    def _find_spectrum_peaks(self,
                            profile: np.ndarray,
                            min_prominence: float = 0.1) -> List[int]:
        """Find peaks in radial spectrum profile"""
        peaks = []
        
        # Simple peak detection
        for i in range(1, len(profile) - 1):
            if (profile[i] > profile[i-1] and 
                profile[i] > profile[i+1] and
                profile[i] > min_prominence * np.max(profile)):
                peaks.append(i)
                
        return peaks
    
    def _create_circular_mask(self,
                             shape: Tuple[int, int],
                             center: np.ndarray,
                             radius: int) -> np.ndarray:
        """Create circular mask"""
        h, w = shape
        y, x = np.ogrid[:h, :w]
        mask = (x - center[1])**2 + (y - center[0])**2 <= radius**2
        return mask


# Main tissue function
def analyze_fourier(image: np.ndarray,
                   operation: str = 'spectrum',
                   filter_type: Optional[str] = None,
                   cutoff: float = 0.1,
                   reference_image: Optional[np.ndarray] = None,
                   visualization: bool = True) -> Dict[str, Any]:
    """
    Main tissue function: Fourier transform analysis and filtering
    
    Args:
        image: Input image (grayscale)
        operation: Operation type ('spectrum', 'filter', 'phase_correlation')
        filter_type: Filter type for 'filter' operation
        cutoff: Cutoff frequency for filtering
        reference_image: Reference for phase correlation
        visualization: Generate visualizations
        
    Returns:
        Dictionary containing:
        - result: Analysis results or filtered image
        - spectrum: Frequency spectrum
        - visualization: Spectrum visualization
        - stats: Analysis statistics
        
    Tissue Metadata:
        - Input: Grayscale image
        - Output: Frequency analysis or filtered image
        - Edge Performance: 20-50ms for 256x256
        - Memory: ~8MB for 512x512
    """
    # Initialize analyzer
    analyzer = FourierTransformAnalyzer()
    
    if operation == 'spectrum':
        # Spectrum analysis
        analysis = analyzer.analyze_spectrum(image)
        
        # Create visualization
        if visualization:
            vis = _create_spectrum_visualization(
                analysis['log_magnitude'],
                analysis['radial_profile']
            )
        else:
            vis = None
            
        return {
            'result': analysis,
            'spectrum': analysis['magnitude'],
            'visualization': vis,
            'stats': {
                'low_freq_energy': analysis['low_freq_energy'],
                'high_freq_energy': analysis['high_freq_energy'],
                'dominant_frequencies': analysis['dominant_frequencies'],
                'sharpness_index': analysis['high_freq_energy'] / 
                                 (analysis['low_freq_energy'] + 1e-6)
            }
        }
        
    elif operation == 'filter' and filter_type:
        # Frequency filtering
        filtered = analyzer.apply_frequency_filter(
            image, filter_type, cutoff
        )
        
        # Get spectrum for visualization
        magnitude, _ = analyzer.compute_fourier_transform(image)
        
        # Create filter visualization
        if visualization:
            h, w = image.shape
            filter_mask = analyzer._create_frequency_filter(
                h, w, filter_type, cutoff, order=2
            )
            vis = _create_filter_visualization(image, filtered, filter_mask)
        else:
            vis = None
            
        return {
            'result': filtered,
            'spectrum': magnitude,
            'visualization': vis,
            'stats': {
                'filter_type': filter_type,
                'cutoff': cutoff,
                'pixels_changed': np.sum(np.abs(image - filtered) > 10),
                'mean_change': np.mean(np.abs(image.astype(float) - filtered.astype(float)))
            }
        }
        
    elif operation == 'phase_correlation' and reference_image is not None:
        # Phase correlation for registration
        shift_x, shift_y = analyzer.compute_phase_correlation(
            image, reference_image
        )
        
        # Create aligned image
        aligned = np.roll(reference_image, (-int(shift_y), -int(shift_x)), axis=(0, 1))
        
        # Create visualization
        if visualization:
            vis = _create_registration_visualization(
                image, reference_image, aligned
            )
        else:
            vis = None
            
        return {
            'result': {
                'shift_x': shift_x,
                'shift_y': shift_y,
                'aligned_image': aligned
            },
            'spectrum': None,
            'visualization': vis,
            'stats': {
                'shift_magnitude': np.sqrt(shift_x**2 + shift_y**2),
                'shift_angle': np.degrees(np.arctan2(shift_y, shift_x))
            }
        }
        
    else:
        raise ValueError(f"Unknown operation: {operation}")


def _create_spectrum_visualization(log_magnitude: np.ndarray,
                                  radial_profile: np.ndarray) -> np.ndarray:
    """Create spectrum visualization"""
    # Normalize log magnitude for display
    log_mag_norm = (log_magnitude - np.min(log_magnitude)) / \
                   (np.max(log_magnitude) - np.min(log_magnitude))
    log_mag_vis = (log_mag_norm * 255).astype(np.uint8)
    
    # Create combined visualization
    h, w = log_mag_vis.shape
    
    # Add radial profile plot (simplified)
    profile_height = 100
    vis = np.zeros((h + profile_height + 10, w), dtype=np.uint8)
    
    # Spectrum image
    vis[:h, :] = log_mag_vis
    
    # Radial profile plot
    profile_norm = radial_profile / (np.max(radial_profile) + 1e-6)
    x_scale = w / len(radial_profile)
    
    for i in range(len(radial_profile) - 1):
        x1 = int(i * x_scale)
        x2 = int((i + 1) * x_scale)
        y1 = h + 10 + int((1 - profile_norm[i]) * (profile_height - 10))
        y2 = h + 10 + int((1 - profile_norm[i + 1]) * (profile_height - 10))
        
        # Simple line drawing
        for x in range(x1, min(x2, w)):
            y = y1 + (y2 - y1) * (x - x1) // (x2 - x1)
            if 0 <= y < vis.shape[0]:
                vis[y, x] = 255
                
    return vis


def _create_filter_visualization(original: np.ndarray,
                               filtered: np.ndarray,
                               filter_mask: np.ndarray) -> np.ndarray:
    """Create filter visualization"""
    # Side by side comparison with filter
    h, w = original.shape
    vis = np.zeros((h, w * 3 + 20), dtype=np.uint8)
    
    # Original
    vis[:, :w] = original
    
    # Filter (normalized)
    filter_vis = (filter_mask * 255).astype(np.uint8)
    vis[:, w+10:2*w+10] = filter_vis
    
    # Filtered result
    vis[:, 2*w+20:] = filtered
    
    return vis


def _create_registration_visualization(image1: np.ndarray,
                                     image2: np.ndarray,
                                     aligned: np.ndarray) -> np.ndarray:
    """Create registration visualization"""
    # Create overlay showing alignment
    h, w = image1.shape
    vis = np.zeros((h, w, 3), dtype=np.uint8)
    
    # Red channel: image1
    vis[:, :, 0] = image1
    
    # Green channel: aligned image2
    vis[:, :, 1] = aligned
    
    # Blue channel: difference
    diff = np.abs(image1.astype(float) - aligned.astype(float))
    vis[:, :, 2] = np.clip(diff, 0, 255).astype(np.uint8)
    
    return vis


# Test the tissue
if __name__ == "__main__":
    # Create test image with patterns
    size = 256
    x = np.linspace(-1, 1, size)
    y = np.linspace(-1, 1, size)
    xx, yy = np.meshgrid(x, y)
    
    # Create image with multiple frequencies
    test_image = np.zeros((size, size))
    
    # Low frequency component
    test_image += 128 + 50 * np.sin(2 * np.pi * 2 * xx)
    
    # High frequency component
    test_image += 30 * np.sin(2 * np.pi * 20 * xx) * np.sin(2 * np.pi * 20 * yy)
    
    # Add noise
    test_image += np.random.normal(0, 10, (size, size))
    
    test_image = np.clip(test_image, 0, 255).astype(np.uint8)
    
    # Test spectrum analysis
    spectrum_result = analyze_fourier(test_image, operation='spectrum')
    print(f"Spectrum Analysis:")
    print(f"  Low frequency energy: {spectrum_result['stats']['low_freq_energy']:.2%}")
    print(f"  High frequency energy: {spectrum_result['stats']['high_freq_energy']:.2%}")
    print(f"  Sharpness index: {spectrum_result['stats']['sharpness_index']:.2f}")
    
    # Test filtering
    filtered_result = analyze_fourier(
        test_image,
        operation='filter',
        filter_type='lowpass',
        cutoff=0.1
    )
    print(f"\nLowpass Filter:")
    print(f"  Mean change: {filtered_result['stats']['mean_change']:.1f}")
    
    # Test phase correlation
    shifted_image = np.roll(test_image, (10, -15), axis=(0, 1))
    registration_result = analyze_fourier(
        test_image,
        operation='phase_correlation',
        reference_image=shifted_image
    )
    print(f"\nPhase Correlation:")
    print(f"  Detected shift: ({registration_result['result']['shift_x']:.1f}, "
          f"{registration_result['result']['shift_y']:.1f})")
    print(f"  Shift magnitude: {registration_result['stats']['shift_magnitude']:.1f}")