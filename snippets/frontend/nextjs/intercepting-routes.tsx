/**
 * Next.js Intercepting Routes examples
 */

// Modal intercepting route: app/photos/(..)photo/[id]/page.tsx
export default function PhotoModal({ params }: { params: { id: string } }) {
  return (
    <div className="modal">
      <div className="modal-backdrop" />
      <div className="modal-content">
        <h2>Photo {params.id}</h2>
        <img src={`/photos/${params.id}.jpg`} alt="Photo" />
      </div>
    </div>
  );
}

// Regular route: app/photo/[id]/page.tsx
export function PhotoPage({ params }: { params: { id: string } }) {
  return (
    <div className="page">
      <h1>Photo {params.id}</h1>
      <img src={`/photos/${params.id}.jpg`} alt="Photo" />
    </div>
  );
}

// Gallery with intercepted modal
export function Gallery() {
  const photos = [1, 2, 3, 4];

  return (
    <div className="grid grid-cols-2 gap-4">
      {photos.map((id) => (
        <a key={id} href={`/photo/${id}`}>
          <img src={`/photos/${id}.jpg`} alt={`Photo ${id}`} />
        </a>
      ))}
    </div>
  );
}

// Login modal: app/@auth/(.)login/page.tsx
export function LoginModal() {
  return (
    <div className="modal">
      <h2>Login</h2>
      <form>
        <input type="email" placeholder="Email" />
        <input type="password" placeholder="Password" />
        <button type="submit">Login</button>
      </form>
    </div>
  );
}
