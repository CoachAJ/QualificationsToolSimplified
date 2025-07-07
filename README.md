# Youngevity Rank Up Blueprint

An AI-powered tool to help Youngevity distributors analyze their business and create a step-by-step plan for rank advancement.

## Features

- **Comprehensive Analysis**: Get a detailed breakdown of your current business status
- **Personalized Plan**: Receive a customized action plan for rank advancement
- **Interactive Chat**: Ask follow-up questions and get specific advice
- **Multi-Rank Support**: Get guidance for any rank from 1SE to 5SE
- **Data Privacy**: Your data stays on your machine - no data is stored on our servers

## Prerequisites

- Python 3.8 or higher
- Google AI API key (get one from [Google AI Studio](https://aistudio.google.com/))
- Youngevity Group Volume Details CSV
- Youngevity Advanced Genealogy Report CSV

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/youngevity-rank-up.git
   cd youngevity-rank-up
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```bash
   streamlit run app.py
   ```

2. In the sidebar:
   - Enter your Google AI API key
   - Upload your Group Volume Details CSV
   - Upload your Advanced Genealogy Report CSV
   - Select your target rank
   - Click "Generate Rank Up Plan"

3. Review your personalized action plan and use the chat feature for follow-up questions.

## CSV File Requirements

### Group Volume Details CSV
Should contain at least these columns:
- `Associate #`
- `Volume` (PQV will be automatically calculated by summing volumes for each Associate Number)

### Advanced Genealogy Report CSV
Should contain at least these columns:
- `ID#`
- `Title`
- `Enroller ID` (or `Enroller` - both column names are supported)

## Troubleshooting

- **API Key Issues**: Ensure your Google AI API key is valid and has sufficient quota
- **CSV Format**: Verify your CSV files match the required format
- **Error Messages**: Read error messages carefully as they often contain specific guidance

## Support

For issues or feature requests, please open an issue on the [GitHub repository](https://github.com/yourusername/youngevity-rank-up/issues).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This tool is not affiliated with Youngevity International, Inc. All product and company names are trademarks™ or registered® trademarks of their respective holders.
