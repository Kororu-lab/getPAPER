# getPAPER

An automated tool for downloading AI and Computer Vision papers from arXiv. This tool systematically downloads papers from the cs.AI and cs.CV categories, starting from December 31, 2024, and moving backwards in time.

## Features

- Automated paper collection from arXiv
- Downloads papers from cs.AI and cs.CV categories
- Systematic collection starting from 2024-12-31
- Progress tracking with detailed statistics
- Duplicate download prevention
- Error handling and retry mechanism
- Detailed logging of download progress

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Kororu-lab/getPAPER.git
cd getPAPER
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

## Usage

Run the paper downloader:
```bash
python src/paper_downloader.py
```

The downloaded PDF files will be saved in the `data/pdf` directory.

## Project Structure

```
getPAPER/
├── src/
│   └── paper_downloader.py    # Main script for paper downloading
├── data/
│   └── pdf/                  # Directory for downloaded PDFs
├── requirements.txt          # Project dependencies
└── README.md                # Project documentation
```

## Features in Detail

- **Batch Processing**: Downloads papers in batches of 1000
- **Progress Tracking**: Shows detailed progress for:
  - Overall progress (by days)
  - Individual paper downloads
  - Download statistics
- **Error Handling**: 
  - Automatic retry mechanism (up to 3 times)
  - Detailed error logging
  - Continues operation even if some papers fail to download
- **Rate Limiting**: Implements delays to respect arXiv API limits

## Statistics Tracking

The tool keeps track of:
- Total number of papers downloaded
- Total number of failed downloads
- Current progress and date range being processed

## Notes

- Please respect arXiv's terms of service and rate limits
- The tool automatically implements delays to prevent API throttling
- Downloaded papers are saved with their arXiv IDs as filenames 