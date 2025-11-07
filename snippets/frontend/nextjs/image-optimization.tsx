/**
 * Next.js Image Optimization examples
 */
import Image from 'next/image';

// Basic responsive image
export function BasicImage() {
  return (
    <Image
      src="/hero.jpg"
      alt="Hero image"
      width={1200}
      height={600}
      priority // Load image with high priority
    />
  );
}

// Fill container
export function FillImage() {
  return (
    <div style={{ position: 'relative', width: '100%', height: '400px' }}>
      <Image
        src="/background.jpg"
        alt="Background"
        fill
        style={{ objectFit: 'cover' }}
      />
    </div>
  );
}

// Responsive sizes
export function ResponsiveImage() {
  return (
    <Image
      src="/responsive.jpg"
      alt="Responsive image"
      width={800}
      height={600}
      sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
    />
  );
}

// External images
export function ExternalImage() {
  return (
    <Image
      src="https://example.com/image.jpg"
      alt="External image"
      width={800}
      height={600}
      unoptimized={false} // Enable optimization for external images
    />
  );
}

// Image with blur placeholder
export function BlurImage() {
  return (
    <Image
      src="/photo.jpg"
      alt="Photo"
      width={800}
      height={600}
      placeholder="blur"
      blurDataURL="data:image/jpeg;base64,/9j/4AAQSkZJRg..." // Generate with plaiceholder
    />
  );
}

// Image with loading state
export function ImageWithLoading() {
  return (
    <Image
      src="/image.jpg"
      alt="Image"
      width={800}
      height={600}
      loading="lazy"
      onLoadingComplete={(img) => {
        console.log('Image loaded:', img.naturalWidth);
      }}
    />
  );
}

// Art direction with picture
export function ArtDirectionImage() {
  return (
    <picture>
      <source
        media="(max-width: 768px)"
        srcSet="/mobile-image.jpg"
      />
      <source
        media="(min-width: 769px)"
        srcSet="/desktop-image.jpg"
      />
      <Image
        src="/fallback-image.jpg"
        alt="Responsive art direction"
        width={1200}
        height={600}
      />
    </picture>
  );
}

// Remote patterns configuration (next.config.js)
/**
module.exports = {
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'example.com',
        port: '',
        pathname: '/images/**',
      },
    ],
    formats: ['image/avif', 'image/webp'],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
  },
};
*/

// Image loader for custom CDN
export function CustomLoaderImage() {
  const myLoader = ({ src, width, quality }: any) => {
    return `https://mycdn.com/${src}?w=${width}&q=${quality || 75}`;
  };

  return (
    <Image
      loader={myLoader}
      src="image.jpg"
      alt="Custom loader"
      width={800}
      height={600}
    />
  );
}

// Image gallery with optimization
export function ImageGallery({ images }: { images: string[] }) {
  return (
    <div className="grid grid-cols-3 gap-4">
      {images.map((src, index) => (
        <div key={index} className="relative h-64">
          <Image
            src={src}
            alt={`Gallery image ${index + 1}`}
            fill
            sizes="(max-width: 768px) 100vw, 33vw"
            style={{ objectFit: 'cover' }}
          />
        </div>
      ))}
    </div>
  );
}
