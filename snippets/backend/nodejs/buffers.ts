/**
 * Buffer Operations in Node.js
 */

// Create buffer from string
export function createBuffer(str: string, encoding: BufferEncoding = 'utf-8'): Buffer {
  return Buffer.from(str, encoding);
}

// Convert buffer to string
export function bufferToString(buffer: Buffer, encoding: BufferEncoding = 'utf-8'): string {
  return buffer.toString(encoding);
}

// Concatenate buffers
export function concatBuffers(buffers: Buffer[]): Buffer {
  return Buffer.concat(buffers);
}

// Compare buffers
export function compareBuffers(buf1: Buffer, buf2: Buffer): number {
  return Buffer.compare(buf1, buf2);
}

// Allocate buffer
export function allocateBuffer(size: number, fill?: string | number): Buffer {
  return Buffer.alloc(size, fill);
}

// Buffer from hex
export function bufferFromHex(hex: string): Buffer {
  return Buffer.from(hex, 'hex');
}

// Buffer to hex
export function bufferToHex(buffer: Buffer): string {
  return buffer.toString('hex');
}

// Buffer to base64
export function bufferToBase64(buffer: Buffer): string {
  return buffer.toString('base64');
}

// Buffer from base64
export function bufferFromBase64(base64: string): Buffer {
  return Buffer.from(base64, 'base64');
}
