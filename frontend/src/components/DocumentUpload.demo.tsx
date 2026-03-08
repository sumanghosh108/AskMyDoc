import { DocumentUpload } from './DocumentUpload';
import { useUploadStore } from '../stores/uploadStore';
import { uploadFiles } from '../services/ingestService';

/**
 * Demo component showing DocumentUpload usage
 * This demonstrates the complete upload flow with the ingest service
 */
export function DocumentUploadDemo() {
  const { isUploading, setUploading, setProgress, updateFileProgress } = useUploadStore();

  const handleUpload = async (files: File[]) => {
    try {
      // Initialize upload state
      setUploading(true);
      setProgress(files.map(f => ({
        fileName: f.name,
        progress: 0,
        status: 'pending' as const,
      })));

      // Upload files with progress tracking
      await uploadFiles(files, (progress) => {
        updateFileProgress(progress.fileName, progress);
      });

      console.log('Upload completed successfully');
    } catch (error) {
      console.error('Upload failed:', error);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-6">Document Upload Demo</h1>
      <DocumentUpload 
        onUpload={handleUpload}
        isUploading={isUploading}
      />
    </div>
  );
}
