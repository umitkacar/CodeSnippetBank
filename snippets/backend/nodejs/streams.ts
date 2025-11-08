/**
 * Stream Operations in Node.js
 */
import { Readable, Writable, Transform, pipeline } from 'stream';
import { promisify } from 'util';

const pipelineAsync = promisify(pipeline);

// Create readable stream
export function createReadableStream(data: string[]): Readable {
  return Readable.from(data);
}

// Create writable stream
export function createWritableStream(onData: (chunk: any) => void): Writable {
  return new Writable({
    write(chunk, encoding, callback) {
      try {
        onData(chunk.toString());
        callback();
      } catch (error: any) {
        callback(error);
      }
    },
  });
}

// Create transform stream
export function createTransformStream(
  transform: (chunk: string) => string
): Transform {
  return new Transform({
    transform(chunk, encoding, callback) {
      try {
        const result = transform(chunk.toString());
        callback(null, result);
      } catch (error: any) {
        callback(error);
      }
    },
  });
}

// Uppercase transform
export function uppercaseTransform(): Transform {
  return createTransformStream((chunk) => chunk.toUpperCase());
}

// Pipeline example
export async function streamPipeline(
  input: Readable,
  ...transforms: (Transform | Writable)[]
): Promise<void> {
  return pipelineAsync(input, ...transforms);
}
