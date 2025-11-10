/**
 * File System Operations in Node.js
 */
import fs from 'fs/promises';
import { createReadStream, createWriteStream } from 'fs';
import path from 'path';

// Read file
export async function readFile(filePath: string): Promise<string> {
  try {
    return await fs.readFile(filePath, 'utf-8');
  } catch (error) {
    throw new Error(`Failed to read file: ${error}`);
  }
}

// Write file
export async function writeFile(filePath: string, content: string): Promise<void> {
  try {
    await fs.writeFile(filePath, content, 'utf-8');
  } catch (error) {
    throw new Error(`Failed to write file: ${error}`);
  }
}

// Append to file
export async function appendFile(filePath: string, content: string): Promise<void> {
  try {
    await fs.appendFile(filePath, content, 'utf-8');
  } catch (error) {
    throw new Error(`Failed to append to file: ${error}`);
  }
}

// Delete file
export async function deleteFile(filePath: string): Promise<void> {
  try {
    await fs.unlink(filePath);
  } catch (error) {
    throw new Error(`Failed to delete file: ${error}`);
  }
}

// Check if file exists
export async function fileExists(filePath: string): Promise<boolean> {
  try {
    await fs.access(filePath);
    return true;
  } catch {
    return false;
  }
}

// Read directory
export async function readDirectory(dirPath: string): Promise<string[]> {
  try {
    return await fs.readdir(dirPath);
  } catch (error) {
    throw new Error(`Failed to read directory: ${error}`);
  }
}

// Create directory
export async function createDirectory(dirPath: string): Promise<void> {
  try {
    await fs.mkdir(dirPath, { recursive: true });
  } catch (error) {
    throw new Error(`Failed to create directory: ${error}`);
  }
}

// Copy file
export async function copyFile(source: string, destination: string): Promise<void> {
  try {
    await fs.copyFile(source, destination);
  } catch (error) {
    throw new Error(`Failed to copy file: ${error}`);
  }
}

// Get file stats
export async function getFileStats(filePath: string): Promise<fs.Stats> {
  try {
    return await fs.stat(filePath);
  } catch (error) {
    throw new Error(`Failed to get file stats: ${error}`);
  }
}
