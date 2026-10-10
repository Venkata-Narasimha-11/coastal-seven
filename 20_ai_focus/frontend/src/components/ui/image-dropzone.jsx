import React, { useState, useEffect, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { UploadCloud, Image as ImageIcon, X, CheckCircle2, AlertCircle } from "lucide-react";
import { cn } from "../../lib/utils";
import { Button } from "./button";

export function ImageDropzone({
  value,
  onChange,
  onFileSelect,
  maxSize = 5 * 1024 * 1024, // 5MB
  accept = {
    "image/jpeg": [".jpg", ".jpeg"],
    "image/png": [".png"],
    "image/webp": [".webp"],
  },
  className,
  previewClassName,
  disabled = false,
  error,
}) {
  const [preview, setPreview] = useState(null);
  const [fileInfo, setFileInfo] = useState(null);
  const [dropError, setDropError] = useState(null);

  // If a string URL is passed in as existing value (e.g. from backend)
  useEffect(() => {
    if (typeof value === "string" && value) {
      setPreview(value);
      setFileInfo({ name: value.split("/").pop() || "Uploaded Image", size: null });
    } else if (value instanceof File) {
      const objectUrl = URL.createObjectURL(value);
      setPreview(objectUrl);
      setFileInfo({ name: value.name, size: (value.size / 1024).toFixed(1) + " KB" });
      return () => URL.revokeObjectURL(objectUrl);
    } else if (!value) {
      setPreview(null);
      setFileInfo(null);
    }
  }, [value]);

  const onDrop = useCallback(
    (acceptedFiles) => {
      setDropError(null);
      if (acceptedFiles.length > 0) {
        const file = acceptedFiles[0];
        const objectUrl = URL.createObjectURL(file);
        setPreview(objectUrl);
        setFileInfo({
          name: file.name,
          size: (file.size / 1024).toFixed(1) + " KB",
          type: file.type,
        });

        if (onChange) onChange(file);
        if (onFileSelect) onFileSelect(file);
      }
    },
    [onChange, onFileSelect]
  );

  const onDropRejected = useCallback((fileRejections) => {
    if (fileRejections.length > 0) {
      const rejection = fileRejections[0];
      const errorMsg = rejection.errors[0]?.message || "Invalid file selected";
      setDropError(errorMsg);
    }
  }, []);

  const handleRemove = (e) => {
    e.stopPropagation();
    setPreview(null);
    setFileInfo(null);
    setDropError(null);
    if (onChange) onChange(null);
    if (onFileSelect) onFileSelect(null);
  };

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    onDropRejected,
    accept,
    maxSize,
    multiple: false,
    disabled,
  });

  const displayError = dropError || error;

  return (
    <div className={cn("space-y-2", className)}>
      <div
        {...getRootProps()}
        className={cn(
          "relative flex flex-col items-center justify-center rounded-xl border-2 border-dashed p-6 transition-all duration-200 cursor-pointer select-none",
          isDragActive
            ? "border-primary bg-primary/10 scale-[1.01]"
            : "border-muted-foreground/30 hover:border-primary/60 hover:bg-muted/30",
          isDragReject && "border-destructive bg-destructive/10",
          preview && "border-solid border-border bg-card",
          disabled && "opacity-50 cursor-not-allowed",
          displayError && "border-destructive bg-destructive/5"
        )}
        role="region"
        aria-label="Image upload dropzone"
      >
        <input {...getInputProps()} aria-label="Upload product image file" />

        {preview ? (
          <div className="flex flex-col items-center w-full space-y-4">
            <div className={cn("relative group overflow-hidden rounded-lg border bg-muted/20 flex items-center justify-center max-h-60 w-full", previewClassName)}>
              <img
                src={preview}
                alt="File upload preview"
                className="max-h-60 max-w-full object-contain rounded-lg shadow-sm transition-transform duration-300 group-hover:scale-105"
              />
              <button
                type="button"
                onClick={handleRemove}
                aria-label="Remove image"
                className="absolute top-2 right-2 rounded-full bg-destructive p-1.5 text-white shadow-md hover:bg-destructive/90 transition-all focus:outline-none focus:ring-2 focus:ring-ring"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            {fileInfo && (
              <div className="flex items-center justify-between w-full px-2 text-xs text-muted-foreground border-t pt-2">
                <span className="truncate max-w-[200px] font-medium text-foreground">
                  {fileInfo.name}
                </span>
                {fileInfo.size && (
                  <span className="bg-muted px-2 py-0.5 rounded text-[11px]">
                    {fileInfo.size}
                  </span>
                )}
              </div>
            )}

            <Button
              type="button"
              variant="outline"
              size="sm"
              className="mt-1 text-xs"
              onClick={(e) => {
                // Clicking button activates input via getRootProps
              }}
            >
              <UploadCloud className="w-3.5 h-3.5 mr-1.5" />
              Change Image
            </Button>
          </div>
        ) : (
          <div className="flex flex-col items-center text-center space-y-2 py-4">
            <div className="p-3 rounded-full bg-primary/10 text-primary">
              <UploadCloud className="h-8 w-8 stroke-[1.75]" />
            </div>
            <div>
              <p className="text-sm font-semibold text-foreground">
                {isDragActive
                  ? "Drop image here..."
                  : "Click to upload or drag & drop"}
              </p>
              <p className="text-xs text-muted-foreground mt-0.5">
                PNG, JPG, or WebP (max {(maxSize / (1024 * 1024)).toFixed(0)}MB)
              </p>
            </div>
            <div className="flex items-center gap-1.5 text-[11px] text-muted-foreground mt-2 bg-muted/60 px-2.5 py-1 rounded-full">
              <CheckCircle2 className="w-3 h-3 text-emerald-500" />
              Auto-generates WebP thumbnails on upload
            </div>
          </div>
        )}
      </div>

      {displayError && (
        <p className="text-xs font-medium text-destructive flex items-center gap-1.5" role="alert">
          <AlertCircle className="w-3.5 h-3.5" />
          <span>{displayError}</span>
        </p>
      )}
    </div>
  );
}
