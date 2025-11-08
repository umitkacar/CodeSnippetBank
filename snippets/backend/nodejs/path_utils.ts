/**
 * Path Utility Functions
 */
import path from 'path';

// Join paths
export function joinPaths(...paths: string[]): string {
  return path.join(...paths);
}

// Resolve absolute path
export function resolvePath(...paths: string[]): string {
  return path.resolve(...paths);
}

// Get basename
export function getBasename(filePath: string, ext?: string): string {
  return path.basename(filePath, ext);
}

// Get directory name
export function getDirname(filePath: string): string {
  return path.dirname(filePath);
}

// Get file extension
export function getExtension(filePath: string): string {
  return path.extname(filePath);
}

// Parse path
export function parsePath(filePath: string): path.ParsedPath {
  return path.parse(filePath);
}

// Format path
export function formatPath(pathObject: path.FormatInputPathObject): string {
  return path.format(pathObject);
}

// Normalize path
export function normalizePath(filePath: string): string {
  return path.normalize(filePath);
}

// Check if absolute path
export function isAbsolutePath(filePath: string): boolean {
  return path.isAbsolute(filePath);
}

// Get relative path
export function getRelativePath(from: string, to: string): string {
  return path.relative(from, to);
}
