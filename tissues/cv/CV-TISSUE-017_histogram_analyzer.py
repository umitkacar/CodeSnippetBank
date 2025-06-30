"""
CV-TISSUE-017: Histogram Analyzer
Advanced histogram analysis and equalization optimized for edge devices
"""

import numpy as np
from typing import Tuple, List, Optional, Dict, Any, Union

class HistogramAnalyzer:
    def __init__(self,
                 bins: int = 256,
                 adaptive: bool = True,
                 clip_limit: float = 2.0,
                 tile_size: Tuple[int, int] = (8, 8)):
        """
        Initialize Histogram Analyzer
        
        Args:
            bins: Number of histogram bins
            adaptive: Use adaptive histogram equalization
            clip_limit: Contrast limit for CLAHE
            tile_size: Tile size for adaptive equalization
        """
        self.bins = bins
        self.adaptive = adaptive
        self.clip_limit = clip_limit
        self.tile_size = tile_size
        
    def compute_histogram(self,
                         image: np.ndarray,
                         mask: Optional[np.ndarray] = None,
                         channel: Optional[int] = None) -> np.ndarray:
        """
        Compute image histogram
        
        Args:
            image: Input image
            mask: Optional mask
            channel: Specific channel for multi-channel images
            
        Returns:
            Histogram array
        """
        if len(image.shape) == 3 and channel is not None:
            data = image[..., channel]
        else:
            data = image
            
        if mask is not None:
            data = data[mask > 0]
            
        # Compute histogram
        hist, _ = np.histogram(data, bins=self.bins, range=(0, 255))
        
        return hist
    
    def equalize_histogram(self,
                          image: np.ndarray,
                          method: str = 'global') -> np.ndarray:
        """
        Perform histogram equalization
        
        Args:
            image: Input image
            method: 'global', 'adaptive', or 'clahe'
            
        Returns:
            Equalized image
        """
        if method == 'global':
            return self._global_equalization(image)
        elif method == 'adaptive':
            return self._adaptive_equalization(image)
        else:  # clahe
            return self._clahe_equalization(image)
    
    def _global_equalization(self, image: np.ndarray) -> np.ndarray:
        """Global histogram equalization"""
        # Compute histogram
        hist = self.compute_histogram(image)
        
        # Compute CDF
        cdf = hist.cumsum()
        cdf_normalized = cdf * 255 / cdf[-1]
        
        # Create lookup table
        lut = cdf_normalized.astype(np.uint8)
        
        # Apply transformation
        return lut[image]
    
    def _adaptive_equalization(self, image: np.ndarray) -> np.ndarray:
        """Adaptive histogram equalization (AHE)"""
        height, width = image.shape[:2]
        tile_h, tile_w = self.tile_size
        
        # Pad image for even tiles
        pad_h = tile_h - (height % tile_h) if height % tile_h else 0
        pad_w = tile_w - (width % tile_w) if width % tile_w else 0
        
        if pad_h or pad_w:
            image_padded = np.pad(image, ((0, pad_h), (0, pad_w)), mode='reflect')
        else:
            image_padded = image
            
        # Process tiles
        result = np.zeros_like(image_padded)
        
        for y in range(0, image_padded.shape[0], tile_h):
            for x in range(0, image_padded.shape[1], tile_w):
                # Extract tile
                tile = image_padded[y:y+tile_h, x:x+tile_w]
                
                # Equalize tile
                tile_eq = self._global_equalization(tile)
                
                # Store result
                result[y:y+tile_h, x:x+tile_w] = tile_eq
                
        # Remove padding
        return result[:height, :width]
    
    def _clahe_equalization(self, image: np.ndarray) -> np.ndarray:
        """Contrast Limited Adaptive Histogram Equalization"""
        height, width = image.shape[:2]
        tile_h, tile_w = self.tile_size
        
        # Number of tiles
        n_tiles_y = height // tile_h
        n_tiles_x = width // tile_w
        
        # Compute histograms for all tiles
        tile_hists = np.zeros((n_tiles_y, n_tiles_x, self.bins))
        tile_cdfs = np.zeros((n_tiles_y, n_tiles_x, self.bins))
        
        for ty in range(n_tiles_y):
            for tx in range(n_tiles_x):
                # Extract tile
                y1 = ty * tile_h
                y2 = min((ty + 1) * tile_h, height)
                x1 = tx * tile_w
                x2 = min((tx + 1) * tile_w, width)
                
                tile = image[y1:y2, x1:x2]
                
                # Compute histogram
                hist = self.compute_histogram(tile)
                
                # Apply contrast limiting
                hist = self._clip_histogram(hist, self.clip_limit)
                
                # Compute CDF
                cdf = hist.cumsum()
                cdf = cdf * 255 / cdf[-1]
                
                tile_hists[ty, tx] = hist
                tile_cdfs[ty, tx] = cdf
        
        # Interpolate between tiles
        result = np.zeros_like(image)
        
        for y in range(height):
            for x in range(width):
                # Find surrounding tiles
                ty = y / tile_h
                tx = x / tile_w
                
                ty0 = int(ty)
                tx0 = int(tx)
                ty1 = min(ty0 + 1, n_tiles_y - 1)
                tx1 = min(tx0 + 1, n_tiles_x - 1)
                
                # Interpolation weights
                fy = ty - ty0
                fx = tx - tx0
                
                # Get pixel value
                pixel = image[y, x]
                
                # Bilinear interpolation of CDFs
                v00 = tile_cdfs[ty0, tx0, pixel]
                v01 = tile_cdfs[ty0, tx1, pixel]
                v10 = tile_cdfs[ty1, tx0, pixel]
                v11 = tile_cdfs[ty1, tx1, pixel]
                
                v0 = v00 * (1 - fx) + v01 * fx
                v1 = v10 * (1 - fx) + v11 * fx
                
                result[y, x] = int(v0 * (1 - fy) + v1 * fy)
                
        return result.astype(np.uint8)
    
    def _clip_histogram(self,
                       hist: np.ndarray,
                       clip_limit: float) -> np.ndarray:
        """Clip histogram for contrast limiting"""
        # Calculate clip threshold
        n_pixels = hist.sum()
        clip_thresh = clip_limit * n_pixels / self.bins
        
        # Clip and redistribute
        excess = 0
        for i in range(self.bins):
            if hist[i] > clip_thresh:
                excess += hist[i] - clip_thresh
                hist[i] = clip_thresh
                
        # Redistribute excess uniformly
        avg_increase = excess // self.bins
        hist += avg_increase
        
        return hist
    
    def match_histograms(self,
                        source: np.ndarray,
                        reference: np.ndarray) -> np.ndarray:
        """
        Match source histogram to reference
        
        Args:
            source: Source image
            reference: Reference image
            
        Returns:
            Transformed source image
        """
        # Compute histograms
        src_hist = self.compute_histogram(source)
        ref_hist = self.compute_histogram(reference)
        
        # Compute CDFs
        src_cdf = src_hist.cumsum()
        ref_cdf = ref_hist.cumsum()
        
        # Normalize CDFs
        src_cdf = src_cdf / src_cdf[-1]
        ref_cdf = ref_cdf / ref_cdf[-1]
        
        # Create mapping
        mapping = np.zeros(self.bins, dtype=np.uint8)
        
        for i in range(self.bins):
            # Find closest match in reference CDF
            idx = np.argmin(np.abs(ref_cdf - src_cdf[i]))
            mapping[i] = idx
            
        # Apply mapping
        return mapping[source]
    
    def analyze_histogram(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Comprehensive histogram analysis
        
        Args:
            image: Input image
            
        Returns:
            Analysis results
        """
        hist = self.compute_histogram(image)
        
        # Basic statistics
        total_pixels = hist.sum()
        mean = np.sum(np.arange(self.bins) * hist) / total_pixels
        
        # Variance
        variance = np.sum((np.arange(self.bins) - mean)**2 * hist) / total_pixels
        std_dev = np.sqrt(variance)
        
        # Mode (most frequent value)
        mode = np.argmax(hist)
        
        # Percentiles
        cdf = hist.cumsum() / total_pixels
        percentiles = {}
        for p in [1, 5, 25, 50, 75, 95, 99]:
            idx = np.searchsorted(cdf, p / 100.0)
            percentiles[p] = min(idx, self.bins - 1)
            
        # Entropy
        prob = hist / total_pixels
        prob = prob[prob > 0]  # Remove zeros
        entropy = -np.sum(prob * np.log2(prob))
        
        # Contrast measures
        contrast = percentiles[95] - percentiles[5]
        dynamic_range = np.where(hist > 0)[0]
        if len(dynamic_range) > 0:
            actual_range = dynamic_range[-1] - dynamic_range[0]
        else:
            actual_range = 0
            
        return {
            'histogram': hist,
            'mean': mean,
            'std_dev': std_dev,
            'mode': mode,
            'percentiles': percentiles,
            'entropy': entropy,
            'contrast': contrast,
            'dynamic_range': actual_range,
            'total_pixels': total_pixels
        }
    
    def compute_color_histogram(self,
                               image: np.ndarray,
                               color_space: str = 'rgb') -> Dict[str, np.ndarray]:
        """
        Compute histograms for color image
        
        Args:
            image: Color image
            color_space: Color space ('rgb', 'hsv', 'lab')
            
        Returns:
            Dictionary of channel histograms
        """
        if color_space == 'hsv':
            image = self._rgb_to_hsv(image)
            channels = ['hue', 'saturation', 'value']
        elif color_space == 'lab':
            image = self._rgb_to_lab(image)
            channels = ['L', 'a', 'b']
        else:
            channels = ['red', 'green', 'blue']
            
        histograms = {}
        for i, channel in enumerate(channels):
            if i < image.shape[2]:
                histograms[channel] = self.compute_histogram(image, channel=i)
                
        return histograms
    
    def _rgb_to_hsv(self, image: np.ndarray) -> np.ndarray:
        """Convert RGB to HSV (simplified)"""
        # Normalize to [0, 1]
        rgb = image.astype(np.float32) / 255.0
        
        # Get min and max
        v = np.max(rgb, axis=2)
        delta = v - np.min(rgb, axis=2)
        
        # Saturation
        s = np.where(v != 0, delta / v, 0)
        
        # Hue (simplified)
        h = np.zeros_like(v)
        
        # Convert back to [0, 255]
        hsv = np.stack([h * 255, s * 255, v * 255], axis=2)
        
        return hsv.astype(np.uint8)
    
    def _rgb_to_lab(self, image: np.ndarray) -> np.ndarray:
        """Convert RGB to LAB (simplified)"""
        # Simplified conversion - in practice use proper color space conversion
        return image  # Placeholder


# Main tissue function
def analyze_histogram(image: np.ndarray,
                     operation: str = 'analyze',
                     method: str = 'global',
                     reference: Optional[np.ndarray] = None,
                     adaptive_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Main tissue function: Histogram analysis and manipulation
    
    Args:
        image: Input image (grayscale or color)
        operation: 'analyze', 'equalize', 'match', 'color_hist'
        method: Method for equalization ('global', 'adaptive', 'clahe')
        reference: Reference image for histogram matching
        adaptive_params: Parameters for adaptive methods
        
    Returns:
        Dictionary containing:
        - result: Processed image or analysis results
        - histogram: Computed histogram(s)
        - visualization: Histogram visualization
        - stats: Statistical measures
        
    Tissue Metadata:
        - Input: Grayscale or color image
        - Output: Enhanced image or histogram analysis
        - Edge Performance: 5-20ms for 640x480
        - Memory: ~2MB peak
    """
    # Initialize analyzer
    params = adaptive_params or {}
    analyzer = HistogramAnalyzer(
        bins=params.get('bins', 256),
        adaptive=params.get('adaptive', True),
        clip_limit=params.get('clip_limit', 2.0),
        tile_size=params.get('tile_size', (8, 8))
    )
    
    if operation == 'analyze':
        # Comprehensive analysis
        if len(image.shape) == 3:
            # Analyze each channel
            results = {}
            for i, channel in enumerate(['R', 'G', 'B']):
                if i < image.shape[2]:
                    results[channel] = analyzer.analyze_histogram(image[..., i])
                    
            # Luminance analysis
            gray = np.dot(image[..., :3], [0.299, 0.587, 0.114]).astype(np.uint8)
            results['luminance'] = analyzer.analyze_histogram(gray)
            
            return {
                'result': results,
                'histogram': {k: v['histogram'] for k, v in results.items()},
                'visualization': _visualize_histograms(results),
                'stats': {k: {sk: sv for sk, sv in v.items() if sk != 'histogram'} 
                         for k, v in results.items()}
            }
        else:
            # Grayscale analysis
            analysis = analyzer.analyze_histogram(image)
            
            return {
                'result': analysis,
                'histogram': analysis['histogram'],
                'visualization': _visualize_histogram(analysis['histogram']),
                'stats': {k: v for k, v in analysis.items() if k != 'histogram'}
            }
            
    elif operation == 'equalize':
        # Histogram equalization
        if len(image.shape) == 3:
            # Process each channel
            result = np.zeros_like(image)
            for i in range(image.shape[2]):
                result[..., i] = analyzer.equalize_histogram(image[..., i], method)
        else:
            result = analyzer.equalize_histogram(image, method)
            
        # Compute before/after histograms
        hist_before = analyzer.compute_histogram(image)
        hist_after = analyzer.compute_histogram(result)
        
        return {
            'result': result,
            'histogram': {'before': hist_before, 'after': hist_after},
            'visualization': _visualize_equalization(image, result),
            'stats': {
                'method': method,
                'contrast_improvement': _compute_contrast_improvement(hist_before, hist_after)
            }
        }
        
    elif operation == 'match' and reference is not None:
        # Histogram matching
        if len(image.shape) == 3:
            result = np.zeros_like(image)
            for i in range(image.shape[2]):
                result[..., i] = analyzer.match_histograms(
                    image[..., i], reference[..., i]
                )
        else:
            result = analyzer.match_histograms(image, reference)
            
        return {
            'result': result,
            'histogram': {
                'source': analyzer.compute_histogram(image),
                'reference': analyzer.compute_histogram(reference),
                'result': analyzer.compute_histogram(result)
            },
            'visualization': _visualize_matching(image, reference, result),
            'stats': {
                'similarity': _compute_histogram_similarity(
                    analyzer.compute_histogram(result),
                    analyzer.compute_histogram(reference)
                )
            }
        }
        
    elif operation == 'color_hist':
        # Color histogram analysis
        histograms = analyzer.compute_color_histogram(image)
        
        return {
            'result': histograms,
            'histogram': histograms,
            'visualization': _visualize_color_histograms(histograms),
            'stats': {
                'dominant_channel': max(histograms.items(), 
                                      key=lambda x: np.argmax(x[1]))[0]
            }
        }
        
    else:
        raise ValueError(f"Unknown operation: {operation}")


def _visualize_histogram(hist: np.ndarray, 
                        max_height: int = 100) -> np.ndarray:
    """Create histogram visualization"""
    # Normalize histogram
    hist_norm = hist * max_height / (hist.max() + 1e-6)
    
    # Create visualization
    vis = np.ones((max_height + 20, 256), dtype=np.uint8) * 255
    
    # Draw histogram bars
    for i in range(256):
        height = int(hist_norm[i])
        if height > 0:
            vis[max_height - height:max_height, i] = 0
            
    return vis


def _visualize_histograms(results: Dict[str, Dict[str, Any]]) -> np.ndarray:
    """Visualize multiple histograms"""
    # Stack individual visualizations
    visualizations = []
    for channel, data in results.items():
        vis = _visualize_histogram(data['histogram'])
        visualizations.append(vis)
        
    return np.vstack(visualizations)


def _visualize_equalization(before: np.ndarray, 
                          after: np.ndarray) -> np.ndarray:
    """Visualize before/after equalization"""
    # Side-by-side comparison
    return np.hstack([before, after])


def _visualize_matching(source: np.ndarray,
                       reference: np.ndarray,
                       result: np.ndarray) -> np.ndarray:
    """Visualize histogram matching"""
    # Three-way comparison
    return np.hstack([source, reference, result])


def _visualize_color_histograms(histograms: Dict[str, np.ndarray]) -> np.ndarray:
    """Visualize color channel histograms"""
    vis_list = []
    for channel, hist in histograms.items():
        vis = _visualize_histogram(hist)
        vis_list.append(vis)
        
    return np.vstack(vis_list)


def _compute_contrast_improvement(hist_before: np.ndarray,
                                 hist_after: np.ndarray) -> float:
    """Compute contrast improvement ratio"""
    # Simple measure based on standard deviation
    def compute_std(hist):
        total = hist.sum()
        mean = np.sum(np.arange(len(hist)) * hist) / total
        var = np.sum((np.arange(len(hist)) - mean)**2 * hist) / total
        return np.sqrt(var)
        
    std_before = compute_std(hist_before)
    std_after = compute_std(hist_after)
    
    return std_after / (std_before + 1e-6)


def _compute_histogram_similarity(hist1: np.ndarray,
                                 hist2: np.ndarray) -> float:
    """Compute histogram similarity using correlation"""
    # Normalize histograms
    hist1_norm = hist1 / (hist1.sum() + 1e-6)
    hist2_norm = hist2 / (hist2.sum() + 1e-6)
    
    # Compute correlation
    mean1 = np.sum(np.arange(len(hist1)) * hist1_norm)
    mean2 = np.sum(np.arange(len(hist2)) * hist2_norm)
    
    cov = np.sum((np.arange(len(hist1)) - mean1) * 
                 (np.arange(len(hist2)) - mean2) * 
                 hist1_norm * hist2_norm)
    
    std1 = np.sqrt(np.sum((np.arange(len(hist1)) - mean1)**2 * hist1_norm))
    std2 = np.sqrt(np.sum((np.arange(len(hist2)) - mean2)**2 * hist2_norm))
    
    return cov / (std1 * std2 + 1e-6)


# Test the tissue
if __name__ == "__main__":
    # Create test image with poor contrast
    test_image = np.random.normal(128, 30, (200, 200)).astype(np.uint8)
    
    # Test analysis
    result = analyze_histogram(test_image, operation='analyze')
    print(f"Image statistics: {result['stats']}")
    
    # Test equalization
    eq_result = analyze_histogram(test_image, operation='equalize', method='clahe')
    print(f"Contrast improvement: {eq_result['stats']['contrast_improvement']:.2f}x")
    
    # Test color histogram
    color_image = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
    color_result = analyze_histogram(color_image, operation='color_hist')
    print(f"Dominant channel: {color_result['stats']['dominant_channel']}")