import { useCallback, useState } from 'react';
import { PhotoIcon, XMarkIcon } from '@heroicons/react/24/outline';

export function ImageUpload({ value, onChange, className = '' }) {
  const [preview, setPreview] = useState(value);
  const [dragActive, setDragActive] = useState(false);

  const handleFile = useCallback(
    (file) => {
      if (file && file.type.startsWith('image/')) {
        onChange(file);
        const reader = new FileReader();
        reader.onloadend = () => setPreview(reader.result);
        reader.readAsDataURL(file);
      }
    },
    [onChange]
  );

  const handleDrop = useCallback(
    (e) => {
      e.preventDefault();
      setDragActive(false);
      const file = e.dataTransfer.files[0];
      handleFile(file);
    },
    [handleFile]
  );

  const handleChange = (e) => {
    const file = e.target.files[0];
    handleFile(file);
  };

  const handleRemove = () => {
    onChange(null);
    setPreview(null);
  };

  return (
    <div className={className}>
      {preview ? (
        <div className="relative">
          <img
            src={preview}
            alt="Preview"
            className="w-full h-48 object-cover rounded-lg"
          />
          <button
            type="button"
            onClick={handleRemove}
            className="absolute top-2 right-2 p-1 bg-red-500 text-white rounded-full hover:bg-red-600"
          >
            <XMarkIcon className="h-5 w-5" />
          </button>
        </div>
      ) : (
        <div
          onDragOver={(e) => {
            e.preventDefault();
            setDragActive(true);
          }}
          onDragLeave={() => setDragActive(false)}
          onDrop={handleDrop}
          className={`
            border-2 border-dashed rounded-lg p-8 text-center cursor-pointer
            transition-colors duration-200
            ${dragActive ? 'border-primary-500 bg-primary-50' : 'border-gray-300 hover:border-gray-400'}
          `}
        >
          <input
            type="file"
            accept="image/*"
            onChange={handleChange}
            className="hidden"
            id="image-upload"
          />
          <label htmlFor="image-upload" className="cursor-pointer">
            <PhotoIcon className="h-12 w-12 mx-auto text-gray-400 mb-4" />
            <p className="text-gray-600">
              Drag and drop an image, or click to select
            </p>
            <p className="text-sm text-gray-400 mt-1">
              JPEG, PNG, WebP up to 5MB
            </p>
          </label>
        </div>
      )}
    </div>
  );
}
