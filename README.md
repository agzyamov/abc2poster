# ABC Poster Generator 🔤📋

An intelligent poster generation system that creates educational ABC posters for kids using an agentic workflow powered by ChatGPT API.

## Overview

This application generates beautiful ABC learning posters through a coordinated multi-agent system. Each agent has a specific role in the poster creation process, working together to produce a complete alphabet learning tool for children.

## How It Works

The application uses a **3-agent workflow** to create the ABC poster:

### 🤖 Agent 1: Picture Generator
- **Input**: A letter and corresponding word
- **Process**: Uses ChatGPT API to generate a square picture containing:
  - Capital letter (e.g., "A")
  - English word starting with that letter (e.g., "Apple")
  - Visual illustration of the word
- **Output**: Saves the generated picture to local storage

### 🔄 Agent 2: Coordinator
- **Process**: Orchestrates the generation process by calling Agent 1 in a loop
- **Input Data**: Predefined letter-word pairs:
  ```
  A - Apple    N - Nest
  B - Banana   O - Orange
  C - Cat      P - Penguin
  D - Dog      Q - Queen
  E - Elephant R - Rainbow
  F - Fish     S - Sun
  G - Giraffe  T - Tiger
  H - House    U - Umbrella
  I - Ice      V - Violin
  J - Jellyfish W - Whale
  K - Kite     X - Xylophone
  L - Lion     Y - Yacht
  M - Mouse    Z - Zebra
  ```
- **Output**: 26 individual letter pictures saved locally

### 🎨 Agent 3: Poster Assembler
- **Input**: All 26 generated pictures from local storage
- **Process**: Combines all individual letter pictures into a cohesive poster layout
- **Output**: Final ABC poster ready for printing or display

## Features

- ✨ **AI-Generated Content**: Each letter picture is uniquely created using ChatGPT API
- 🎯 **Educational Focus**: Designed specifically for children's learning
- 🔄 **Automated Workflow**: Fully automated generation process
- 💾 **Local Storage**: Pictures are saved locally for reuse and assembly
- 📐 **Consistent Format**: Square pictures ensure uniform poster layout
- 🎨 **Visual Learning**: Combines letters, words, and pictures for effective learning

## Prerequisites

Before running the application, ensure you have:

- Node.js (v14 or higher)
- NPM or Yarn package manager
- ChatGPT API key from OpenAI
- Sufficient local storage space for 26+ images

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/abc2poster.git
   cd abc2poster
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Environment setup**
   ```bash
   cp .env.example .env
   ```
   
4. **Configure your environment variables**
   ```env
   OPENAI_API_KEY=your_chatgpt_api_key_here
   STORAGE_PATH=./generated_images
   POSTER_OUTPUT_PATH=./output
   ```

## Usage

### Quick Start
```bash
# Generate the complete ABC poster
npm start
```

### Step-by-step execution
```bash
# Run individual agents
npm run agent:generator    # Agent 1: Generate individual pictures
npm run agent:coordinator  # Agent 2: Coordinate the generation process
npm run agent:assembler    # Agent 3: Assemble the final poster
```

### Custom word list
```bash
# Use custom letter-word pairs
npm run generate -- --config custom-words.json
```

## Configuration

### Custom Word Pairs
Create a `custom-words.json` file to use different word associations:

```json
{
  "A": "Astronaut",
  "B": "Butterfly",
  "C": "Castle",
  // ... rest of alphabet
}
```

### Picture Settings
Modify `config/picture-settings.js` to customize:
- Image dimensions
- Font styles and sizes
- Color schemes
- Layout preferences

## Output

The application generates:

1. **Individual Pictures**: 26 square images (one per letter) in `./generated_images/`
2. **Final Poster**: Combined poster in `./output/abc-poster.png`
3. **Metadata**: Generation log and settings in `./output/generation-info.json`

## API Usage

### ChatGPT Integration
The application uses OpenAI's ChatGPT API to generate images. Ensure your API key has:
- Image generation capabilities
- Sufficient usage credits
- Appropriate rate limits configured

### Rate Limiting
The coordinator agent includes built-in rate limiting to respect API constraints:
- Default: 1 request per 2 seconds
- Configurable via `RATE_LIMIT_MS` environment variable

## Troubleshooting

### Common Issues

**API Key Errors**
```bash
Error: Invalid API key
```
- Verify your OpenAI API key in `.env` file
- Ensure the key has image generation permissions

**Storage Issues**
```bash
Error: Cannot write to storage path
```
- Check write permissions for the storage directory
- Ensure sufficient disk space

**Generation Failures**
```bash
Error: Failed to generate image for letter X
```
- Check API rate limits
- Verify internet connection
- Review ChatGPT API status

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📧 Email: support@abc2poster.com
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/abc2poster/issues)
- 📖 Documentation: [Wiki](https://github.com/yourusername/abc2poster/wiki)

## Acknowledgments

- OpenAI for ChatGPT API
- Contributors and educators who inspired this project
- The open-source community for tools and libraries used

---

**Made with ❤️ for children's education** 