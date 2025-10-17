import WebSocket from 'ws'
import readline from 'readline'
import dotenv from 'dotenv'

dotenv.config()

const socket = new WebSocket(`ws://${process.env.PC_IPV4_ADDRESS}:${process.env.PORT}`)

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
})

socket.on('open', () => {
  console.log('Connected to game server')

  rl.on('line', (input) => {
    socket.send(input)
  })
})

socket.on('message', (data) => {
  const message = data.toString()

  if (message.startsWith('client:')) {
    console.log(message) // shows 'client: text'
  } else if (message.startsWith('server:')) {
    console.log(message) // shows 'server: text'
  } else {
    console.log('unknown:', message)
  }
})

socket.on('close', () => {
  console.log('Disconnected from server')
})
