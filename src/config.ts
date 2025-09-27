import path, { dirname } from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

const config = {
  username: 'Vixify',
  avatar: path.join(__dirname, 'assets', 'avatar.png'),
  customPresence: [
    'Monetizing your freedom',
    'Everything is for sale',
    'Investing in inequality',
    'Cutting corners for profit',
    'Growth at any cost',
    'Paywalling your dreams',
    'Targeting your wallet',
    'You are the product',
    'Innovating your obsolescence',
    'Selling your inbox',
  ],
  commandOnlyInGuildWarning: 'This command may only be used in a server.',
}

export default config
