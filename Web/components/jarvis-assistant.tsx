'use client'

import React, { useState, useEffect, useRef } from 'react'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Mic, MicOff, Menu } from 'lucide-react'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

interface Message {
  text: string
  sender: 'user' | 'jarvis'
}

export default function JarvisAssistant() {
  const [messages, setMessages] = useState<Message[]>([
    { text: "你好!我是Jarvis,有什么我可以帮助你的吗?", sender: 'jarvis' }
  ])
  const [input, setInput] = useState('')
  const [isListening, setIsListening] = useState(false)
  const [pythonCode, setPythonCode] = useState<string>('')
  const scrollAreaRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight
    }
  }, [messages])

  const handleSendMessage = async (text: string) => {
    if (text.trim() === '') return

    const userMessage: Message = { text, sender: 'user' }
    setMessages(prev => [...prev, userMessage])
    setInput('')

    try {
      const response = await fetch('/api/jarvis', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text }),
      })
      const data = await response.json()
      const jarvisMessage: Message = { text: data.response, sender: 'jarvis' }
      setMessages(prev => [...prev, jarvisMessage])

      // 使用浏览器的语音合成API
      const speech = new SpeechSynthesisUtterance(data.response)
      speech.lang = 'zh-CN'
      window.speechSynthesis.speak(speech)
    } catch (error) {
      console.error('Error getting response:', error)
    }
  }

  const toggleListening = () => {
    if (isListening) {
      stopListening()
    } else {
      startListening()
    }
  }

  const startListening = () => {
    if ('webkitSpeechRecognition' in window) {
      const recognition = new (window as any).webkitSpeechRecognition()
      recognition.continuous = false
      recognition.lang = 'zh-CN'

      recognition.onstart = () => {
        setIsListening(true)
      }

      recognition.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript
        setInput(transcript)
        handleSendMessage(transcript)
      }

      recognition.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error)
        setIsListening(false)
      }

      recognition.onend = () => {
        setIsListening(false)
      }

      recognition.start()
    } else {
      console.error('Speech recognition not supported')
    }
  }

  const stopListening = () => {
    if ('webkitSpeechRecognition' in window) {
      const recognition = new (window as any).webkitSpeechRecognition()
      recognition.stop()
    }
  }

  const fetchPythonCode = async () => {
    try {
      const response = await fetch('/api/python-code')
      const data = await response.json()
      setPythonCode(data.code)
    } catch (error) {
      console.error('Error fetching Python code:', error)
    }
  }

  return (
    <div className="flex flex-col h-screen max-w-2xl mx-auto p-4 bg-gray-100">
      <h1 className="text-2xl font-bold mb-4 text-center">Jarvis 智能助手 (网页版)</h1>
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="outline" size="icon">
            <Menu className="h-4 w-4" />
            <span className="sr-only">功能菜单</span>
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end">
          <DropdownMenuItem onClick={fetchPythonCode}>
            显示Python程序
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
      {pythonCode && (
        <div className="mb-4 p-4 bg-gray-800 text-white rounded-lg overflow-x-auto">
          <pre><code>{pythonCode}</code></pre>
        </div>
      )}
      <ScrollArea className="flex-grow mb-4 p-4 bg-white rounded-lg shadow" ref={scrollAreaRef}>
        {messages.map((message, index) => (
          <div
            key={index}
            className={`mb-2 p-2 rounded-lg ${
              message.sender === 'user' ? 'bg-blue-100 text-right' : 'bg-gray-200'
            }`}
          >
            {message.text}
          </div>
        ))}
      </ScrollArea>
      <div className="flex gap-2">
        <Input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSendMessage(input)}
          placeholder="输入消息..."
          className="flex-grow"
        />
        <Button onClick={() => handleSendMessage(input)}>发送</Button>
        <Button onClick={toggleListening} variant="outline">
          {isListening ? <MicOff className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
        </Button>
      </div>
    </div>
  )
}

