import express, { type Application, Request, Response } from 'express'
import dotenv from 'dotenv'

dotenv.config()

const app: Application = express()


app.use(express.json())


app.get('/', (req: Request, res: Response) => {
  res.send('Server is running with TypeScript ⚡')
})

const PORT = process.env.PORT || 3000


app.listen(PORT, () => {
  console.log(`🚀 Server running on http://localhost:${PORT}`)
})
