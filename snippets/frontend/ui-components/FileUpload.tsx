import React, { useState } from 'react';

interface FileUploadProps {
  onUpload?: (files: FileList) => void;
  accept?: string;
  multiple?: boolean;
}

export const FileUpload = ({ onUpload, accept, multiple = false }: FileUploadProps) => {
  const [files, setFiles] = useState<File[]>([]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const fileList = Array.from(e.target.files);
      setFiles(fileList);
      onUpload?.(e.target.files);
    }
  };

  return (
    <div className="w-full">
      <label className="flex cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed border-gray-300 bg-gray-50 p-6 hover:bg-gray-100">
        <div className="text-center">
          <p className="mb-2 text-sm text-gray-500">
            Click to upload or drag and drop
          </p>
          <input
            type="file"
            className="hidden"
            onChange={handleChange}
            accept={accept}
            multiple={multiple}
          />
        </div>
      </label>
      {files.length > 0 && (
        <ul className="mt-2 text-sm">
          {files.map((file, index) => (
            <li key={index}>{file.name}</li>
          ))}
        </ul>
      )}
    </div>
  );
};
