import express, { Request, Response } from 'express'
import cors from 'cors'

const app = express()
const PORT = 5000

app.use(cors())
app.use(express.json())

interface Player {
  playerName: string
  score: number
}

let leaderboard: Player[] = []


app.post('/game-connected', (req: Request, res: Response) => {
  const { client_ip } = req.body
  console.log(`🎮 Game connected from ${client_ip || 'unknown IP'}`)
  res.json({ message: 'Game connection registered successfully' })
})

app.post('/update-score', (req: Request, res: Response) => {
  const { playerName, score } = req.body

  if (!playerName || typeof score !== 'number') {
    return res.status(400).json({ error: 'Invalid input' })
  }

  const existing = leaderboard.find(p => p.playerName === playerName)
  if (existing) {
    existing.score = Math.max(existing.score, score)
  } else {
    leaderboard.push({ playerName, score })
  }

  leaderboard.sort((a, b) => b.score - a.score)

  return res.json({ message: 'Score updated', leaderboard })
})



app.get('/leaderboard', (_req: Request, res: Response) => { 
  res.json(leaderboard)
})

app.listen(PORT, () => {
  console.log('http://192.168.100.5:5000 connected')
})
