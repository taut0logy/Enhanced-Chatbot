const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export const api = {
  // Chat endpoints
  async sendMessage(message) {
    const response = await fetch(`${API_BASE_URL}/chat/text`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message }),
    })
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to send message')
    }
    return response.json()
  },

  async sendVoice(formData) {
    const response = await fetch(`${API_BASE_URL}/chat/voice`, {
      method: 'POST',
      body: formData
    })
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to process voice')
    }
    return response.json()
  },

  async textToSpeech(text) {
    const response = await fetch(`${API_BASE_URL}/chat/text-to-speech`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
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

    const response = await fetch(`${API_BASE_URL}/files/upload`, {
      method: 'POST',
      body: formData,
    })
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to upload file')
    }
    return response.json()
  },

  async processImage(imageFile) {
    const formData = new FormData()
    formData.append('image', imageFile)

    const response = await fetch(`${API_BASE_URL}/files/process-image`, {
      method: 'POST',
      body: formData,
    })
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to process image')
    }
    return response.json()
  },

  // PDF endpoints
  async generateStory(prompt) {
    const response = await fetch(`${API_BASE_URL}/pdf/generate-story`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ prompt }),
    })
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to generate story')
    }
    return response.json()
  },

  async downloadPdf(fileId) {
    const response = await fetch(`${API_BASE_URL}/pdf/download/${fileId}`)
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to download PDF')
    }
    return response.blob()
  },

  async listPdfs() {
    const response = await fetch(`${API_BASE_URL}/pdf/files`)
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to list PDFs')
    }
    return response.json()
  },

  async generateCustomPDF(prompt, templateType) {
    const response = await fetch(`${API_BASE_URL}/pdf/generate-custom`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
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