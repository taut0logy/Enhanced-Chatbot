'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/auth-context';
import { toast } from 'sonner';
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { format } from 'date-fns';

export function ContentHistory() {
  const { user } = useAuth();
  const [contents, setContents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [contentType, setContentType] = useState('ALL');
  const [page, setPage] = useState(0);

  const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  const fetchContents = async () => {
    try {
      const token = localStorage.getItem('token');
      const queryType = contentType === 'ALL' ? '' : contentType;
      const response = await fetch(
        `/api/content?content_type=${queryType}&limit=10&offset=${page * 10}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error('Failed to fetch content');
      }

      const data = await response.json();
      setContents(prev => page === 0 ? data : [...prev, ...data]);
    } catch (error) {
      toast.error('Failed to load content history');
      console.error('Error fetching contents:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (user) {
      setPage(0);
      fetchContents();
    }
  }, [user, contentType]);

  const handleLoadMore = () => {
    setPage(prev => prev + 1);
    fetchContents();
  };

  const handleDelete = async (contentId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/content/${contentId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to delete content');
      }

      setContents(prev => prev.filter(content => content.id !== contentId));
      toast.success('Content deleted successfully');
    } catch (error) {
      toast.error('Failed to delete content');
      console.error('Error deleting content:', error);
    }
  };

  const handleDownload = async (content) => {
    try {
      const token = localStorage.getItem('token');
      
      if (content.type === 'PDF' && content.filename) {
        const response = await fetch(`${BACKEND_URL}/api/pdf/download/${content.filename}`, {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });
        
        if (!response.ok) {
          throw new Error('Failed to download PDF');
        }
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${content.title}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } else if (content.fileUrl) {
        window.open(content.fileUrl, '_blank');
      } else if (content.content) {
        const blob = new Blob([content.content], { type: 'text/plain' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = content.filename || `${content.title}.txt`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }
    } catch (error) {
      toast.error('Failed to download file');
      console.error('Error downloading file:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Content History</h2>
        <Select value={contentType} onValueChange={setContentType}>
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="Filter by type" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="ALL">All</SelectItem>
            <SelectItem value="CHAT">Chat</SelectItem>
            <SelectItem value="PDF">PDF</SelectItem>
            <SelectItem value="VOICE">Voice</SelectItem>
            <SelectItem value="FILE">File</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {contents.map((content) => (
          <Card key={content.id}>
            <CardHeader>
              <CardTitle>{content.title}</CardTitle>
              <CardDescription>
                {format(new Date(content.createdAt), 'PPpp')}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Type: {content.type}
              </p>
              {content.filename && (
                <p className="text-sm text-muted-foreground">
                  File: {content.filename}
                </p>
              )}
            </CardContent>
            <CardFooter className="flex justify-between">
              <Button
                variant="outline"
                onClick={() => handleDownload(content)}
              >
                Download
              </Button>
              <Button
                variant="destructive"
                onClick={() => handleDelete(content.id)}
              >
                Delete
              </Button>
            </CardFooter>
          </Card>
        ))}
      </div>

      {contents.length >= (page + 1) * 10 && (
        <div className="flex justify-center mt-4">
          <Button onClick={handleLoadMore}>
            Load More
          </Button>
        </div>
      )}
    </div>
  );
} 