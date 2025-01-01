const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export const api = {
  // Chat endpoints
  async sendMessage(message, modelName = null) {
    const response = await fetch(`${API_BASE_URL}/api/chat/text`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
      body: JSON.stringify({ 
        message,
        model_name: modelName 
      }),
    })
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to send message')
    }
    const data = await response.json()
    return data // Return the actual response data
  },

  async sendVoice(audioBlob, modelName = null) {
    const formData = new FormData()
    formData.append('audio', audioBlob, 'audio.webm')
    if (modelName) {
      formData.append('model_name', modelName)
    }

    const response = await fetch(`${API_BASE_URL}/api/chat/voice`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
      body: formData
    })
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to process voice')
    }
    const data = await response.json()
    return data.data
  },

  async textToSpeech(text) {
    const response = await fetch(`${API_BASE_URL}/api/chat/text-to-speech`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
      body: JSON.stringify({ text }),
    })
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to convert text to speech')
    }
    return response.blob()
  },

  // File endpoints
  async uploadFile(file) {
    const formData = new FormData()
    formData.append('file', file)

    const response = await fetch(`${API_BASE_URL}/api/files/upload`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
      body: formData,
    })
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to upload file')
    }
    return response.json()
  },

  async processFile(file, modelName = null) {
    const formData = new FormData()
    formData.append('file', file)
    if (modelName) {
      formData.append('model_name', modelName)
    }

    const response = await fetch(`${API_BASE_URL}/api/files/process-file`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
      body: formData,
    })
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to process image')
    }
    return response.json()
  },

  // PDF endpoints
  async generateStory(prompt, modelName = null) {
    const response = await fetch(`${API_BASE_URL}/api/pdf/generate-story`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
      body: JSON.stringify({
        prompt,
        model_name: modelName
      })
    })
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to generate story')
    }
    return response.json()
  },

  async downloadPdf(fileId) {
    const response = await fetch(`${API_BASE_URL}/api/pdf/download/${fileId}`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
    })
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to download PDF')
    }
    return response.blob()
  },

  async listPdfs() {
    const response = await fetch(`${API_BASE_URL}/api/pdf/files`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
    })
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to list PDFs')
    }
    return response.json()
  },

  async generateCustomPDF(prompt, templateType) {
    const response = await fetch(`${API_BASE_URL}/api/pdf/generate-custom`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
      body: JSON.stringify({ prompt, template_type: templateType }),
    })
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to generate custom PDF')
    }
    return response.json()
  },
} 