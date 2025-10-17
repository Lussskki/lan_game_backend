import express, { type Application } from 'express'
import http from 'http'
import { WebSocketServer } from 'ws'
import readline from 'readline'
import dotenv from 'dotenv'

dotenv.config()

const app: Application = express()
const server = http.createServer(app)
const wss = new WebSocketServer({ server })

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
})

rl.on('line', (input) => {
  const serverMessage = `server: ${input}`

  wss.clients.forEach((client) => {
    if (client.readyState === 1) {
      client.send(serverMessage)
    }
  })

  console.log(`You (server) sent: ${input}`)
})

wss.on('connection', (socket) => {
  console.log('New player connected')

  socket.on('message', (data) => {
    const message = data.toString()

    const taggedMessage = `client: ${message}`

    wss.clients.forEach((client) => {
      if (client.readyState === 1) {
        client.send(taggedMessage)
      }
    })

    console.log(`👤 ${taggedMessage}`)
  })

  socket.on('close', () => {
    console.log('Player disconnected')
  })
})

const PORT = process.env.PORT || 3000

server.listen(PORT, () => {
  console.log(`Game backend running on http://localhost:${PORT}`)
  console.log('Type a message below to send to client:')
})
