import { DocumentUpload } from '@/components';
import { useUploadStore } from '@/stores';
import { uploadFiles } from '@/services';
import toast from 'react-hot-toast';
import type { UploadProgress } from '@/types';

export default function UploadPage() {
  const { isUploading, setUploading, updateFileProgress } = useUploadStore();

  const handleUpload = async (files: File[]) => {
    setUploading(true);

    try {
      const results = await uploadFiles(files, (progress: UploadProgress) => {
        updateFileProgress(progress.fileName, {
          progress: progress.progress,
          status: progress.status,
          error: progress.error,
        });
      });

      const successCount = results.filter(r => r.status === 'success').length;
      toast.success(`Successfully uploaded ${successCount} file(s)`);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to upload files';
      toast.error(errorMessage);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Upload Documents</h2>
        <p className="text-gray-600 mb-6">
          Upload PDF, Markdown, or text files to add them to the knowledge base.
        </p>
        
        <DocumentUpload 
          onUpload={handleUpload}
          isUploading={isUploading}
        />

        {/* Upload Instructions */}
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-blue-900 mb-2">Upload Guidelines</h3>
          <ul className="text-sm text-blue-800 space-y-1 list-disc list-inside">
            <li>Supported formats: PDF, Markdown (.md), Text (.txt)</li>
            <li>Maximum file size: 10 MB per file</li>
            <li>You can upload multiple files at once</li>
            <li>Files are processed and indexed automatically</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
